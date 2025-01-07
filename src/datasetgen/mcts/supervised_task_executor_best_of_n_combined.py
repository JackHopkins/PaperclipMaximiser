import json
import os
from typing import List, Dict, Optional, Any, Tuple
import asyncio
from math import floor
import logging
from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.supervised_task_executor_abc import SupervisedTaskExecutorABC, PlanningGroupV2
from datasetgen.mcts.planning_models import PlanOutput, TaskOutput, Step, LanguageOutput, InitialPlanOutput
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.program import Program
from factorio_instance import FactorioInstance
from results.supervised_results.tasks import TaskConfig
from datasetgen.mcts.parallel_supervised_config import SupervisedExecutorConfig
from datasetgen.mcts.conversation import Conversation, GenerationParameters, Message
from tenacity import retry, wait_exponential
from datasetgen.mcts.planning_mcts import get_mining_setup
import copy
logger = logging.basicConfig(level=logging.INFO)




class BestOfNCombinedExecutor(SupervisedTaskExecutorABC):
    def __init__(self,
                 instances: List[FactorioInstance],
                 db_client: DBClient,
                 llm_factory: Any,
                 config: SupervisedExecutorConfig,
                 version=None,
                 version_description="",
                 ):
        """
        Initialize parallel planning MCTS

        Args:
            instances: List of Factorio instances to distribute
            db_client: Database client
            llm_factory: Factory for creating language models
            config: Configuration parameters including model paths and prompts
        """

        super().__init__(instances, db_client, llm_factory, config, version, version_description)

        # Initialize other attributes from config
        self.max_steps_per_objective = config.supervised_kwargs["max_steps_per_objective"]


        self.model_to_evaluate = config.model_to_evaluate
        self.prompt_path = config.supervised_kwargs['prompt_path']
        self.beam_unificatin_prompt_path = config.supervised_kwargs['beam_unification_prompt_path']
        self.beam_unification_user_prompt, self.beam_unification_system_prompt = self.read_in_prompts(
            self.beam_unificatin_prompt_path)
        self.system_prompt, self.user_prompt = self.read_in_prompts(
            self.prompt_path)
        
        # format the 2 system prompts
        self.system_prompt = self.system_prompt.format(schema=self.api_description)

        self.beam_unification_steps = config.supervised_kwargs.get("beam_unification_steps", 0)
    async def generate_plans(self, task: TaskConfig, nr_of_beams: int) -> List[InitialPlanOutput]:
        
        plan_outputs = {}
        for idx in range(nr_of_beams):
            # plan id coincides with instance id it will be evaluated on
            plan_output = PlanOutput(task=TaskOutput(task=task.task), meta={"plan_id": idx})
            plan_outputs[idx] = plan_output

        return plan_outputs
    

    async def _run_group_search(self, group: PlanningGroupV2, 
                                task: TaskConfig, 
                                n_iterations: int, 
                                skip_failures: bool = False,
                                run_id: str = ""):
        """Run parallel planning search across all groups"""
        """
        Need to check again over what to do mcts exactly
        """
        try:
            solutions = []
            for iteration in range(n_iterations):
                output_dict_to_save = None
                group.plans = await self.generate_plans(task, nr_of_beams=len(group.active_instances))
                start_state = self.config.initial_state
                start_state.inventory = task.starting_inventory
                saved_step_ids = []

                for step_idx in range(self.max_steps_per_objective):
                    if step_idx == 0:
                        # reset the instances
                        for instance_id, instance in enumerate(group.evaluator.instances):
                            instance.reset(start_state)

                    plans = await self._process_group_step(group, step_idx, skip_failures, start_state, parent = None, task = task)
                    output_dicts = []
                    for plan in plans:
                        try:
                            # Save the step
                            step_to_save = plan.steps[-1]
                            # lets first try to only save the steps that are final
                            if step_to_save.program.id not in saved_step_ids:
                                output_dict = await self.save_step(plan, step_to_save,
                                                    original_parent=None,
                                                    run_id=run_id)
                                saved_step_ids.append(step_to_save.program.id)
                                output_dicts.append(output_dict)
                        except Exception as e:
                            print("Could not save step - possibly missing (in case of skipping errors)")
                            print(e)
                    group.evaluator.logger.update_progress()
                    # check the output dicts
                    for output_dict in output_dicts:
                        if output_dict["solution_found"]:
                            output_dict_to_save = output_dict
                            break
                    # break out of search loop
                    if output_dict_to_save:
                        break
                    if self.beam_unification_steps > 0 and (step_idx +1)%self.beam_unification_steps == 0:
                        group = await self.unify_beams(group, task)
                if output_dict_to_save is None:
                    output_dict_to_save = {"solution_found": False,
                                            "correct_solution": False,
                                            "number_of_steps": len(plans[0].steps),
                                            "production_flows" : None,
                                            "program_id": None}
                solutions.append(output_dict_to_save)

        except Exception as e:
            print(f"Error during parallel search: {str(e)}")
            raise
        finally:
            self.cleanup()
            return solutions


    async def unify_beams(self, group: PlanningGroupV2, task: TaskConfig):
        plan_outputs = group.plans
        generation_params = GenerationParameters(
            model=self.model_to_evaluate,
            max_tokens=4096,
            temperature = 0.3
        )
        conversations_to_process = []
        starting_inv = group.plans[0].steps[-self.beam_unification_steps].program.meta["starting_inventory"]
        mining_setup = group.plans[0].steps[-self.beam_unification_steps].program.meta["mining_setup"]
        starting_idx = max(0, len(group.plans[0].logs) - self.beam_unification_steps)
        logs = group.plans[0].logs[:starting_idx]
        starting_logs_str = self.format_log_string(logs)
        objective = task.task
        trace_str = ""
        plan_output_list = []
        for instance_id, plan_output in plan_outputs.items():
            if plan_output.success:
                continue
            steps = plan_output.steps
            trace_str_candidate_str = f"CANDIDATE TRACE {len(plan_output_list)}\n"
            for step_idx in range(starting_idx, len(steps)): 
                trace_str_candidate_str += f"Step {step_idx}: {steps[step_idx].chosen_step}\n{steps[step_idx].program.response}\n"
            trace_str_candidate_str += "\n"
            trace_str += trace_str_candidate_str
            plan_output_list.append((instance_id, plan_output))

        user_message = self.beam_unification_user_prompt.format(objective=objective,
                                                          starting_inventory=starting_inv,
                                                          mining_setup=mining_setup, logs=starting_logs_str,
                                                          analysis_step_str=trace_str)
        conversations_to_process.append(
            (Conversation(messages=[Message(role="system", content=self.beam_unification_system_prompt),
                                    Message(role="user", content=user_message)]), plan_output.meta["plan_id"]))

        trace_outputs = [asyncio.ensure_future(
            self._generate_natural_language_batch(conversation[0], generation_params, meta={"type": "beam_unification",
                                                                                            "plan_id": conversation[
                                                                                                1]})) for conversation
                        in conversations_to_process]
        responses = await asyncio.gather(*trace_outputs)

        output = responses[0][0]
        trace_output = output.response.strip()
        # extra postprocessing step, change all <CHOICE> and <Choice> to <choice>
        # makes it more robust
        tags_to_lowercase = ["<Choice>", "<CHOICE>", "</Choice>", "</CHOICE>"]
        for tag in tags_to_lowercase:
            trace_output = trace_output.replace(tag, tag.lower())
            

        # split it by <choice>
        # Should we make it lowercase?
        if "<choice>" in trace_output:
            trace_idx = trace_output.split("<choice>")[-1].strip()
            trace_idx = trace_idx.split("</choice>")[0].strip()
            try:
                plan = plan_output_list[int(trace_idx)][1]
                instance_id = plan_output_list[int(trace_idx)][0]
                instance = group.evaluator.instances[instance_id]
                instance_game_state = GameState.from_instance(instance)
            except:
                return group
        else:
            # How should we actually handle this? When it wasn't a choice
            return group
        
        # we need to override all plans with the chosen plan
        # also need to reset the instances to the new game state
        for instance_id, plan_output in group.plans.items():
            group.plans[instance_id] = copy.deepcopy(plan)
            group.plans[instance_id].meta["plan_id"] = instance_id
            group.evaluator.instances[instance_id].reset(instance_game_state)

        return group

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_next_step(self, group, start_state) -> List[PlanOutput]:
        plan_outputs = group.plans
        generation_params = GenerationParameters(
            model=self.model_to_evaluate,
            max_tokens=4096,
            temperature = 0.7
        )
        conversations_to_process = []
        start_states = {}
        for instance_id, plan_output in plan_outputs.items():
            if plan_output.success:
                continue
            instance = group.evaluator.instances[instance_id]
            if len(plan_output.steps) == 0:
                # we use the initial starting state
                start_state_to_reset_to = start_state
            else:
                start_state_to_reset_to = plan_output.steps[-1].end_state
            instance.reset(start_state_to_reset_to)
            starting_state = GameState.from_instance(instance)
            start_states[instance_id] = starting_state
            
            mining_setup = get_mining_setup(instance)
            # dumb test
            #mining_setup += "These have been put down by another agent and form a working copper ore factory"
            # end of dumb test
            starting_inventory = instance.inspect_inventory()
            starting_inventory_dict = self.get_inventory_dict(starting_inventory)
            logs = plan_output.logs if plan_output.logs else []
            log_str = self.format_log_string(logs)
            objective = plan_output.task.task
            user_message = self.user_prompt.format(mining_setup=mining_setup,
                                                                  starting_inventory=starting_inventory,
                                                                  game_logs=log_str, task=objective)
            conversations_to_process += [(Conversation(
                messages=[Message(role="system", content=self.system_prompt),
                          Message(role="user", content=user_message)]),
                                          {"plan_id": instance_id,
                                           "mining_setup": mining_setup,
                                           "starting_inventory": starting_inventory_dict})]

        step_outputs = [asyncio.ensure_future(self._generate_programs_batch(conversation[0], generation_params,
                                                                                    meta={
                                                                                        "type": "step_programs",
                                                                                        "plan_id": conversation[1]["plan_id"],
                                                                                        "mining_setup": conversation[1]["mining_setup"],
                                                                                        "starting_inventory": conversation[1]["starting_inventory"]}))
                        for conversation in conversations_to_process]
        responses = await asyncio.gather(*step_outputs)
        step_output_objects = {}
        for idx, response in enumerate(responses):
            output = response[0]
            plan_id = output.meta["plan_id"]
            # We need to create a new step object
            step_output_objects[plan_id] = Step(candidate_language_outputs=[], start_state=start_states[plan_id])
            # extra postprocessing step, change all <Step> and <STEP> to <step>
            # same with <Objective_completed> and <OBJECTIVE_COMPLETED>
            # makes it more robust
            if output.code == "":
                text = output.meta["text_response"]
                tags_to_lowercase = ["<Objective_completed>", "<OBJECTIVE_COMPLETED>", "</Objective_completed>", "</OBJECTIVE_COMPLETED>"]
                for tag in tags_to_lowercase:
                    text = text.replace(tag, tag.lower())
                text = text.strip()
            
                # check if the step says it is a success
                if "<objective_completed>" in text:
                    step_output = text.split("<objective_completed>")[-1].strip()
                    step_output = step_output.split("</objective_completed>")[0].strip()
                    # put the success flag in the plan_output as True
                    plan_outputs[plan_id].success = True
                    plan_outputs[plan_id].final_output = step_output
                    step_output_objects[plan_id].chosen_step = step_output

            else:
                step_output_objects[plan_id].sampled_programs.append(output)

        for plan_id, step_output in step_output_objects.items():
            plan_outputs[plan_id].steps.append(step_output)

        return plan_outputs
    

    async def _process_group_step(self, group: PlanningGroupV2, step_idx: int, 
                                  skip_failures: bool, start_state: GameState, parent: Program,
                                  task: TaskConfig) -> List[PlanOutput]:
        """Process a single step for a group"""
        try:
            # Generate candidates
            group.evaluator.set_status(f"Getting candidates for step {step_idx}")
            group.plans = await self.generate_next_step(group, start_state)

            # Evaluate programs in parallel across instances
            eval_futures = []
            completed_plans = []
            for instance_id, (instance, plan) in enumerate(zip(group.active_instances, group.plans.values())):
                if plan.success:
                    if plan.steps[-1].program is None:
                        plan.steps[-1].program = self._create_output_completed_program(plan = plan, 
                                                                                       parent_id=parent.id if parent else None,
                                                                                       task=task,
                                                                                       group = group)
                    completed_plans.append(plan)
                    continue

                group.evaluator.logger.update_instance(instance_id, status="evaluating")

                eval_futures.append(self._process_last_step(
                    plan=plan,
                    start_state=start_state,
                    group=group,
                    instance_id=instance_id,
                    parent_id=parent.id if parent else None,
                    skip_failures=skip_failures
                ))

            return await asyncio.gather(*eval_futures) + completed_plans

        except Exception as e:
            print(f"Error in group {group.group_id}, step {step_idx}: {str(e)}")
            raise

    async def _evaluate_step(self,
                             step: Step,
                             start_state: GameState,
                             group: PlanningGroupV2,
                             instance_id: int,
                             parent_id) -> Tuple[Step, float, List]:
        """Modified to work with instance groups"""
        entity_list = []

        try:
            instance = group.active_instances[instance_id]
            group.evaluator.logger.update_instance(instance_id, status="executing")
            for program in step.sampled_programs:
                instance.reset(step.start_state)
                if not isinstance(program, Program):
                    print(f"Weird program 1: {program}")
                # reset the instance to the start state
                instance.reset(step.start_state)
                reward, state, response, entities, achievements, profits, error = await group.evaluator._evaluate_single(
                    instance_id,
                    program,
                    instance
                )
                if not isinstance(program, Program):
                    print(f"Weird program 2: {program}")
                if error:
                    print(f"Error in group {group.group_id}, instance {instance_id}: {error}")
                step.program = program
                if not error:
                    break
            entity_list.append(entities)
            step.end_state = state
            step.reward = reward
            post_production_flows = instance.get_production_stats()
            step.program.meta["post_production_flows"] = post_production_flows
            step.program.meta["profits"] = profits
        except Exception as e:
            print(f"Error during evaluation in group {group.group_id}, instance {instance_id}: {e}")
            raise e

        step.program.raw_reward = step.reward
        step.program.state = step.end_state
        step.program.response = response
        step.program.parent_id = parent_id
        step.program.achievements = achievements
        return step, entity_list

    async def save_step(self, plan: PlanOutput, step: Step, original_parent: Program, run_id: str):
        candidate_step_meta = []
        # first we check if judge has been done on this step
        # If not, then its the final output step
        if step.program.meta["type"] == "completed_objective":
            for candidate_step in step.candidate_language_outputs:
                try:
                    messages = candidate_step.conversation.model_dump()['messages']
                except:
                    messages = candidate_step.conversation.dict()['messages']
                output = candidate_step.response
                candidate_step_meta.append({"output": output, "messages": messages,
                                            })
            step.program.meta["candidate_steps"] = candidate_step_meta
            await self.db_client.create_program(step.program)
            output_dict = {"solution_found": True,
                            "correct_solution": step.program.meta["checked_result_correct"],
                            "number_of_steps": len(plan.steps),
                            "production_flows" : step.program.meta["post_production_flows"],
                            "program_id": step.program.id
                            }
            return output_dict
        # we need to save all the programs but we need to add some meta fields
        objective = plan.task.task
        initial_plan = plan.initial_plan.initial_plan if plan.initial_plan else None
        parent_id = original_parent.id if original_parent else None

        # find the step before `step` in the plan to get the `parent_id`
        for current_step, next_step in zip(plan.steps[:-1], plan.steps[1:]):
            if next_step.program.id == step.program.id:
                parent_id = current_step.program.id


        post_production_flows = step.program.meta["post_production_flows"]
        node_profit = step.program.meta["profits"]
        meta = {"objective": objective, 
                "initial_plan": initial_plan, 
                "candidate_steps": candidate_step_meta,
                "text_response": step.program.meta["text_response"],
                "final_output": plan.final_output,
                "type": "step",
                "search_type": "best_of_n_combined",
                "full_production_flows": post_production_flows,
                "step_idx": len(plan.steps),
                "sampled_state_id": original_parent.id if original_parent else None,
                "profits": {"node_profit": node_profit},
                "run_id": run_id,
                "mining_setup": step.program.meta["mining_setup"],
                "starting_inventory": step.program.meta["starting_inventory"],
                }

        program = step.program
        program.meta = meta
        program.parent_id = parent_id
        await self.db_client.create_program(program)
        output_dict = {"solution_found": False,
                        "correct_solution": False,
                        "number_of_steps": len(plan.steps),
                        "production_flows" : post_production_flows,
                        "program_id": program.id
                        }
        return output_dict

    async def _process_last_step(self, plan: PlanOutput,
                                 start_state: GameState,
                                 group: PlanningGroupV2,
                                 instance_id: int,
                                 parent_id: Optional[int],
                                 skip_failures: bool) -> PlanOutput:
        try:
            step_to_process = plan.steps[-1]
            if len(step_to_process.sampled_programs) == 0:
                # pop the last step from plan
                plan.steps.pop()
                return plan
            step_to_process, entity_list = await self._evaluate_step(step_to_process, start_state, group, instance_id,
                                                                              parent_id)

            if skip_failures and "error" in step_to_process.program.response.lower():
                raise Exception("Found error in response. Skipping step.")

            plan.steps[-1] = step_to_process
            log_str = f"Step {len(plan.steps)}\n{step_to_process.program.response}"
            plan.logs.append(log_str)
            return plan


        except Exception as e:
            print(f"Failed to evaluate program on instance {instance_id}: {str(e)}")
            # pop the last step from plan
            plan.steps.pop()
            return plan
    
