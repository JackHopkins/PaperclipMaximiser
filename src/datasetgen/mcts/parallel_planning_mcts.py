import json
import os
from typing import List, Dict, Optional, Any, Tuple
import asyncio
from math import floor
import logging
from dataclasses import dataclass
from rich.console import Console
from tenacity import retry, wait_exponential

from datasetgen.mcts.conversation import Conversation, GenerationParameters, Message
from datasetgen.mcts.conversation_formatter import ConversationFormatter, DefaultFormatter, StructurePreservingFormatter
from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.factorio_evaluator import FactorioEvaluator
from datasetgen.mcts.grouped_logger import GroupedFactorioLogger
from datasetgen.mcts.instance_group import InstanceGroup
from datasetgen.mcts.parallel_mcts_config import ParallelMCTSConfig
from datasetgen.mcts.planning_mcts import get_mining_setup
from datasetgen.mcts.planning_models import PlanOutput, TaskOutput, Step, LanguageOutput, InitialPlanOutput
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.program import Program
from factorio_instance import FactorioInstance

logger = logging.basicConfig(level=logging.INFO)


@dataclass
class PlanningGroup:
    group_id: int
    mcts: 'ParallelPlanningMCTS'
    evaluator: FactorioEvaluator
    active_instances: List[FactorioInstance]
    holdout_instance: FactorioInstance
    plans: Dict[int, PlanOutput] = None


class ParallelPlanningMCTS:
    def __init__(self,
                 instances: List[FactorioInstance],
                 db_client: DBClient,
                 llm_factory: Any,
                 config: ParallelMCTSConfig,
                 version=26,
                 version_description="",
                 formatter: ConversationFormatter = StructurePreservingFormatter(),
                 ):
        """
        Initialize parallel planning MCTS

        Args:
            instances: List of Factorio instances to distribute
            db_client: Database client
            llm_factory: Factory for creating language models
            config: Configuration parameters including model paths and prompts
        """
        self.console = Console()
        self.config = config
        self.sampler = config.sampler
        self.db_client = db_client
        self.llm = llm_factory
        self.version = version
        self.version_description = version_description
        self.formatter = formatter

        # Validate instance count
        self._validate_instance_count(len(instances), config.n_parallel)

        # Initialize logger
        instances_per_group = floor(len(instances) / config.n_parallel)
        self.logger = GroupedFactorioLogger(
            n_groups=config.n_parallel,
            instances_per_group=instances_per_group,

        )
        self.logger.start()

        # Initialize other attributes from config
        self.max_steps_per_objective = config.max_steps_per_objective
        self.number_of_steps_for_judge = config.number_of_steps_for_judge


        self.planning_model = config.mcts_kwargs['planning_model']
        self.executor_model = config.mcts_kwargs['executor_model']
        self.objective_model = config.mcts_kwargs['objective_model']
        self.step_executor_prompt_path = config.mcts_kwargs['step_executor_prompt_path']
        self.step_generator_prompt_path = config.mcts_kwargs['step_generator_prompt_path']
        self.step_judge_prompt_path = config.mcts_kwargs['step_judge_prompt_path']
        self.example_plan_prompt_path = config.mcts_kwargs['example_plan_prompt_path']
        self.step_executor_system_prompt, self.step_executor_user_prompt = self.read_in_prompts(
            config.mcts_kwargs['step_executor_prompt_path'])
        self.step_generator_system_prompt, self.step_generator_user_prompt = self.read_in_prompts(
            config.mcts_kwargs['step_generator_prompt_path'])
        self.step_judge_system_prompt, self.step_judge_user_prompt = self.read_in_prompts(config.mcts_kwargs['step_judge_prompt_path'])
        self.example_plan_system_prompt, self.example_plan_user_prompt = self.read_in_prompts(config.mcts_kwargs['example_plan_prompt_path'])

        # Create instance groups
        self.instance_groups = self._create_instance_groups(instances)
        self.api_description = self.instance_groups[0].evaluator.instances[0].get_system_prompt()
        # format the 2 system prompts
        self.step_executor_system_prompt = self.step_executor_system_prompt.format(schema=self.api_description)
        self.example_plan_system_prompt = self.example_plan_system_prompt.format(schema=self.api_description)

    def read_in_prompts(self, path):
        system_prompt_path = os.path.join(path, "system_prompt.md")
        user_prompt_path = os.path.join(path, "user_prompt.md")
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
        with open(user_prompt_path, "r") as f:
            user_prompt = f.read()
        return system_prompt, user_prompt


    def _create_instance_groups(self, instances: List['FactorioInstance']) -> List[PlanningGroup]:
        """Create instance groups for parallel execution"""
        instances_per_group = floor(len(instances) / self.config.n_parallel)
        groups = []

        for group_id in range(self.config.n_parallel):
            # Slice instances for this group
            start_idx = group_id * instances_per_group
            end_idx = start_idx + instances_per_group
            group_instances = instances[start_idx:end_idx]

            # Split into active and holdout instances
            active_instances = group_instances[:-1]
            holdout_instance = group_instances[-1]

            # Create evaluator for this group
            evaluator = FactorioEvaluator(
                db_client=self.db_client,
                instances=group_instances,
                value_accrual_time=3,
                logger=self.logger
            )

            # Create MCTS instance
            mcts = self.config.mcts_class(
                llm_factory=self.llm,
                db_client=self.db_client,
                sampler=self.sampler,
                evaluator=evaluator,
                **self.config.mcts_kwargs
            )

            groups.append(PlanningGroup(
                group_id=group_id,
                mcts=mcts,
                evaluator=evaluator,
                active_instances=active_instances,
                holdout_instance=holdout_instance,

            ))

        return groups

    def _validate_instance_count(self, total_instances: int, n_parallel: int):
        min_required = n_parallel * 2
        if total_instances < min_required:
            raise ValueError(
                f"Need at least {min_required} instances for {n_parallel} parallel searches "
                f"(got {total_instances})"
            )

        instances_per_group = floor(total_instances / n_parallel)
        if instances_per_group < 2:
            raise ValueError(
                f"Not enough instances per group (need at least 2, got {instances_per_group})"
            )

    async def search(self, n_iterations: int, skip_failures: bool = False):
        """
        Run truly parallel MCTS search across all groups

        Args:
            n_iterations: Number of iterations to run
            skip_failures: Whether to skip failed program generations
        """
        try:
            # Create group search tasks that will run in parallel
            search_tasks = []
            for group in self.instance_groups:
                # Each group search runs independently
                task = asyncio.create_task(self._run_group_search(
                    group=group,
                    n_iterations=n_iterations,
                    skip_failures=skip_failures
                ))
                search_tasks.append(task)

            # Wait for ALL groups to complete, allowing them to run simultaneously
            await asyncio.gather(*search_tasks)

        except Exception as e:
            print(f"Error during parallel search: {str(e)}")
            raise
        finally:
            self.cleanup()

    async def _run_group_search(self, group: PlanningGroup, n_iterations: int, skip_failures: bool = False):
        """Run parallel planning search across all groups"""
        try:
            for iteration in range(n_iterations):

                parent = await self.sampler.sample_parent(version=self.version)

                group.evaluator.set_status(f"Generating tasks")
                tasks, start_state = await self._get_tasks(group, parent)

                group.evaluator.set_status(f"Generating plans")
                group.plans = await self.generate_plans(tasks)
                saved_step_ids = []
                for step_idx in range(self.max_steps_per_objective):
                    if step_idx == 0:
                        # reset the instances
                        for instance_id, instance in enumerate(group.evaluator.instances):
                            instance.reset(start_state)

                    plans = await self._process_group_step(group, step_idx, skip_failures, start_state, parent)

                    for plan in plans:
                        try:
                            # Save the step
                            step_to_save = plan.steps[-1]
                            if step_to_save.program.id not in saved_step_ids:
                                await self.save_step(plan, step_to_save,
                                                    starting_state_program_id=parent.id if parent else None)
                                saved_step_ids.append(step_to_save.program.id)
                        except Exception as e:
                            print("Could not save step - possibly missing (in case of skipping errors)")

                    group.evaluator.logger.update_progress()

        except Exception as e:
            print(f"Error during parallel search: {str(e)}")
            raise
        finally:
            self.cleanup()

    async def _process_group_step(self, group: PlanningGroup, step_idx: int, skip_failures: bool, start_state: GameState, parent: Program) -> List[PlanOutput]:
        """Process a single step for a group"""
        try:
            # Generate candidates
            group.evaluator.set_status(f"Getting candidates for step {step_idx}")
            group.plans = await self.generate_next_step_candidates(group)

            # Judge candidates
            group.evaluator.set_status(f"Judging candidates for step {step_idx}")
            group.plans = await self.get_next_step_with_judge(group)

            # Generate programs
            group.evaluator.set_status(f"Generating programs for step {step_idx}")
            group.plans = await self.get_next_step_programs(group)

            # Evaluate programs in parallel across instances
            eval_futures = []
            completed_plans = []
            for instance_id, (instance, plan) in enumerate(zip(group.active_instances, group.plans.values())):
                if plan.success:
                    if plan.steps[-1].program is None:
                        plan.steps[-1].program = self._create_output_completed_program(plan, parent.id if parent else None)
                    completed_plans.append(plan)
                    continue

                latest_program = plan.steps[-1].program
                group.evaluator.logger.update_instance(instance_id, program_id=latest_program.id, status="evaluating")

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

    def cleanup(self):
        """Clean up resources"""
        self.logger.stop()
        for group in self.instance_groups:
            if hasattr(group.evaluator, 'logger'):
                group.evaluator.logger.stop()

    def get_group_metrics(self, group_id: int) -> Dict[str, Any]:
        """Get metrics for a specific group"""
        if 0 <= group_id < len(self.instance_groups):
            group = self.instance_groups[group_id]
            return {
                'active_instances': len(group.active_instances),
                'total_programs': sum(
                    inst.total_programs
                    for inst in group.evaluator.logger.groups[group_id].instances.values()
                ),
                'error_count': sum(
                    inst.error_count
                    for inst in group.evaluator.logger.groups[group_id].instances.values()
                )
            }
        return {}

    async def _evaluate_step(self,
                             step: Step,
                             start_state: GameState,
                             group: PlanningGroup,
                             instance_id: int,
                             parent_id) -> Tuple[Step, float, List]:
        """Modified to work with instance groups"""
        group.holdout_instance.reset(start_state)
        holdout_future = asyncio.create_task(group.evaluator._run_holdout())
        entity_list = []

        try:
            instance = group.active_instances[instance_id]
            step.start_state = GameState.from_instance(instance)
            group.evaluator.logger.update_instance(instance_id, status="executing")

            reward, state, response, entities, achievements = await group.evaluator._evaluate_single(
                instance_id,
                step.program,
                instance
            )
            entity_list.append(entities)
            step.end_state = state
            step.reward = reward
            post_production_flows = instance.get_production_stats()
            step.program.meta["post_production_flows"] = post_production_flows
        except Exception as e:
            print(f"Error during evaluation in group {group.group_id}, instance {instance_id}: {e}")
            raise e

        holdout_value = await holdout_future
        step.program.value = step.reward - holdout_value
        step.program.raw_reward = step.reward
        step.program.holdout_value = holdout_value
        step.program.state = step.end_state
        step.program.response = response
        step.program.parent_id = parent_id
        step.program.achievements = achievements

        return step, holdout_value, entity_list

    async def save_step(self, plan: PlanOutput, step: Step, starting_state_program_id):
        candidate_step_meta = []
        # first we check if judge has been done on this step
        # If not, then its the final output step
        if step.judge_step_str == "":
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
            return
        # we need to save all the programs but we need to add some meta fields
        objective = plan.task.task
        initial_plan = plan.initial_plan.initial_plan
        parent_id = starting_state_program_id

        # find the step before `step` in the plan to get the `parent_id`
        for current_step, next_step in zip(plan.steps[:-1], plan.steps[1:]):
            if next_step.final_step == step.final_step:
                parent_id = current_step.program.id

        for candidate_step in step.candidate_language_outputs:
            try:
                messages = candidate_step.conversation.model_dump()['messages']
            except:
                messages = candidate_step.conversation.dict()['messages']
            output = candidate_step.response
            start_state = step.start_state
            candidate_step_meta.append({"output": output, "messages": messages,
                                        })
            mining_setup = candidate_step.meta["mining_setup"]
            starting_inventory = candidate_step.meta["starting_inventory"]
        try:
            judge_messages = step.judge_language_output_step.conversation.model_dump()['messages']
        except:
            judge_messages = step.judge_language_output_step.conversation.dict()['messages']
        judge_output = step.judge_step_str
        executor_step = step.final_step
        post_production_flows = step.program.meta["post_production_flows"]
        meta = {"objective": objective, 
                "initial_plan": initial_plan, 
                "candidate_steps": candidate_step_meta,
                "judge_step": {"messages": judge_messages,
                               "output": judge_output}, 
                "executor_step": {"input_step":executor_step,
                                  "natural_language_plan": step.program.meta["text_response"],
                                  "model": step.program.meta["model"]},
                "mining_setup": mining_setup, 
                "starting_inventory": starting_inventory,
                "final_output": plan.final_output,
                "type": "step",
                "full_production_flows": post_production_flows,
                "step_idx": len(plan.steps)}

        program = step.program
        program.meta = meta
        program.parent_id = parent_id
        await self.db_client.create_program(program)
        parent_id = program.id

    async def _process_last_step(self, plan: PlanOutput,
                                 start_state: GameState,
                                 group: PlanningGroup,
                                 instance_id: int,
                                 parent_id: Optional[int],
                                 skip_failures: bool) -> PlanOutput:
        try:
            step_to_process = plan.steps[-1]
            step_to_process, holdout, entity_list = await self._evaluate_step(step_to_process, start_state, group, instance_id,
                                                                              parent_id)

            if skip_failures and "error" in step_to_process.program.response.lower():
                raise Exception("Found error in response. Skipping step.")

            plan.steps[-1] = step_to_process
            log_str = f"Step {len(plan.steps)}: {step_to_process.final_step}\n{step_to_process.program.response}"
            plan.logs.append(log_str)
            return plan


        except Exception as e:
            print(f"Failed to evaluate program on instance {instance_id}: {str(e)}")
            # pop the last step from plan
            plan.steps.pop()
            return plan
        
    def _create_output_completed_program(self, plan: PlanOutput,
                                 parent_id: Optional[int]) -> PlanOutput:
        objective = f"'{plan.task.task}'"
        python_code = f"print('Objective {objective} has been completed. Now lets prepare the next objective.')"
        program_parent_id = plan.steps[-2].program.id if len(plan.steps) > 1 else parent_id
        program = Program(
                        id=hash((python_code, plan.task.task, program_parent_id)),
                        code=python_code,
                        conversation=Conversation(messages = []),
                        parent_id=program_parent_id,
                        version=self.version,
                        version_description=self.version_description,
                        meta={"objective": plan.task.task,
                              "type": "completed_objective"}
                    )
        return program

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_natural_language_batch(self, conversation: Conversation,
                                               generation_params: GenerationParameters,
                                               meta: dict) -> List[LanguageOutput]:
        """Generate multiple programs in a single API call using 'n' parameter"""
        formatted_messages = self.formatter.to_llm_messages(
            self.formatter.format_conversation(conversation)
        )
        if "claude" in generation_params.model:
            assert generation_params.n == 1, "Number of samples must be 1 for Claude"

        try:
            # Single API call to generate n_samples completions
            response = await self.llm.acall(
                messages=formatted_messages,
                n_samples=generation_params.n,
                temperature=generation_params.temperature,
                max_tokens=generation_params.max_tokens,
                logit_bias=generation_params.logit_bias,
                stop_sequences=generation_params.stop_sequences,
                model=generation_params.model

            )

            outputs = []
            try:
                messages = conversation.model_dump()['messages']
            except:
                messages = conversation.dict()['messages']

            # Process all choices from the response
            if "claude" in generation_params.model:

                str_output = response.content[0].text
                outputs.append(LanguageOutput(
                    id=hash((str_output, json.dumps(messages))),
                    response=str_output,  # I think this could also be multiple
                    conversation=conversation,
                    token_usage=response.usage.output_tokens + response.usage.input_tokens if hasattr(response,
                                                                                                      'usage') else None,
                    completion_token_usage=response.usage.output_tokens if hasattr(response, 'usage') else None,
                    prompt_token_usage=response.usage.input_tokens if hasattr(response, 'usage') else None,
                    version=self.version,
                    version_description=self.version_description,
                    meta=meta
                ))
            else:
                # Handle OpenAI response format with multiple choices
                for choice in response.choices:
                    str_output = choice.message.content
                    outputs.append(LanguageOutput(
                        id=hash((str_output, json.dumps(messages))),
                        response=str_output,
                        conversation=conversation,
                        token_usage=response.usage.total_tokens // generation_params.n if hasattr(response,
                                                                                                  'usage') else None,
                        completion_token_usage=response.usage.completion_tokens // generation_params.n if hasattr(
                            response,
                            'usage') else None,
                        prompt_token_usage=response.usage.prompt_tokens // generation_params.n if hasattr(response,
                                                                                                          'usage') else None,
                        version=self.version,
                        version_description=self.version_description,
                        meta=meta
                    ))

            return outputs
        except Exception as e:
            print(f"Batch program generation failed: {str(e)}")
            return []

    def get_inventory_dict(self, inventory):
        inventory_dict = {}
        for item in inventory:
            if isinstance(item, tuple):
                inventory_dict[item[0]] = inventory[item]
            else:
                inventory_dict[item] = inventory[item]
        return inventory_dict

    async def _get_tasks(self,
                         group: PlanningGroup,
                         parent: Program = None) -> Tuple[List[TaskOutput], GameState]:
        """Modified to work with instance groups"""
        start_state = parent.state if parent else self.config.initial_state

        # Reset the first instance in this group
        first_instance = group.active_instances[0]
        first_instance.reset(start_state)

        # Get mining setup for this instance
        mining_setup = get_mining_setup(first_instance)
        starting_inventory = first_instance.inspect_inventory()

        conversation = Conversation(messages=[
            Message(role="system", content=self.config.system_prompt),
            Message(role="user",
                    content=f"Your starting inventory is {starting_inventory}. Your mining setup is {mining_setup}. Create an useful task that is doable in the current game setup given your inventory and mining setup."),
        ])

        generation_params = GenerationParameters(
            model=self.config.mcts_kwargs['objective_model'],
            n=len(group.active_instances),
            stop_sequences=["\n"]
        )

        inventory_dict = self.get_inventory_dict(starting_inventory)
        game_state_str = GameState.from_instance(first_instance).entities

        tasks = await self._generate_natural_language_batch(
            conversation,
            generation_params,
            meta={
                "type": "objective_generation",
                "inventory": inventory_dict,
                "mining_setup": mining_setup,
                "game_state": game_state_str,
                "group_id": group.group_id
            }
        )

        task_outputs = []
        for task in tasks:
            task_string = task.response.split("\n")[0].strip()
            task_string = task_string.lower().replace("sure! the task i will carry out is", "").strip()
            if "." in task_string:
                task_string = task_string.split(".")[0]
            task_outputs.append(TaskOutput(task=task_string, language_output=task))

        return task_outputs, start_state

    async def generate_plans(self, task_outputs: List[TaskOutput]) -> List[InitialPlanOutput]:
        generation_params = GenerationParameters(
            model=self.executor_model,
            stop_sequences=["```"],
            logits={
                '7032': -100
            }
        )
        conversations_to_process = [
            Conversation(messages=[Message(role="system", content=self.example_plan_system_prompt),
                                   Message(role="user",
                                           content=self.example_plan_user_prompt.format(task=task_output.task))]) for
            task_output in task_outputs]

        initial_plans = [asyncio.ensure_future(self._generate_natural_language_batch(conversation, generation_params,
                                                                                     meta={"type": "initial_plan_generation"}))
                         for conversation in conversations_to_process]
        # initial_plans = [self._generate_natural_language_batch(conversation, generation_params, meta={"type": "initial_plan_generation"}) for conversation in conversations_to_process]

        responses = await asyncio.gather(*initial_plans)
        plan_outputs = {}
        for idx, response in enumerate(responses):
            initial_plan = response[0].response.strip()
            new_line_idx = initial_plan.rfind("\n")
            if new_line_idx != -1:
                initial_plan = initial_plan[:new_line_idx].strip()
            initial_plan_output = InitialPlanOutput(initial_plan=initial_plan, language_output=response[0])
            # plan id coincides with instance id it will be evaluated on
            plan_output = PlanOutput(task=task_outputs[idx], initial_plan=initial_plan_output, meta={"plan_id": idx})
            plan_outputs[idx] = plan_output

        return plan_outputs

    def format_log_string(self, plan_output: PlanOutput):
        return "\n\n".join(plan_output.logs) if plan_output.logs else "The agent has not yet interacted with the world"

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_next_step_candidates(self, group) -> List[PlanOutput]:
        plan_outputs = group.plans
        generation_params = GenerationParameters(
            model=self.planning_model,
            max_tokens=4096
        )
        conversations_to_process = []
        for instance_id, plan_output in plan_outputs.items():
            if plan_output.success:
                continue
            instance = group.evaluator.instances[instance_id]
            mining_setup = get_mining_setup(instance)
            starting_inventory = instance.inspect_inventory()
            starting_inventory_dict = self.get_inventory_dict(starting_inventory)
            log_str = self.format_log_string(plan_output)
            objective = plan_output.task.task
            initial_plan = plan_output.initial_plan.initial_plan
            user_message = self.step_generator_user_prompt.format(mining_setup=mining_setup,
                                                                  starting_inventory=starting_inventory,
                                                                  logs=log_str, objective=objective, plan=initial_plan)
            conversations_to_process += [(Conversation(
                messages=[Message(role="system", content=self.step_generator_system_prompt),
                          Message(role="user", content=user_message)]),
                                          plan_output.meta["plan_id"])] * self.number_of_steps_for_judge

        step_outputs = [asyncio.ensure_future(self._generate_natural_language_batch(conversation[0], generation_params,
                                                                                    meta={
                                                                                        "type": "next_step_candidates",
                                                                                        "plan_id": conversation[1],
                                                                                        "mining_setup": mining_setup,
                                                                                        "starting_inventory": starting_inventory_dict}))
                        for conversation in conversations_to_process]
        responses = await asyncio.gather(*step_outputs)
        step_output_objects = {}
        for idx, response in enumerate(responses):
            output = response[0]
            plan_id = output.meta["plan_id"]
            # extra postprocessing step, change all <Step> and <STEP> to <step>
            # same with <Output> and <OUTPUT>
            # makes it more robust
            tags_to_lowercase = ["<Step>", "<STEP>", "<Output>", "<OUTPUT>", "</Step>", "</STEP>", "</Output>", "</OUTPUT>"]
            for tag in tags_to_lowercase:
                output.response = output.response.replace(tag, tag.lower())
            if not ("<output>" in output.response and "</output>" in output.response) and not (
                    "<step>" in output.response and "</step>" in output.response):
                continue
            step_output = output.response.strip()
            # first check if the step says it is a success
            # We need to create a new step object
            if plan_id not in step_output_objects:
                step_output_objects[plan_id] = Step(candidate_language_outputs=[])
            
            if "<output>" in step_output and "<step>" not in step_output:
                step_output = step_output.split("<output>")[-1].strip()
                step_output = step_output.split("</output>")[0].strip()
                # put the success flag in the plan_output as True
                plan_outputs[plan_id].success = True
                plan_outputs[plan_id].final_output = step_output
                step_output_objects[plan_id].final_step = step_output
            else:
                parsed_step = step_output.split("<step>")[-1].strip()
                parsed_step = parsed_step.split("</step>")[0].strip()
                output.meta["parsed_step"] = parsed_step

            step_output_objects[plan_id].candidate_language_outputs.append(output)

        for plan_id, step_output in step_output_objects.items():
            plan_outputs[plan_id].steps.append(step_output)

        return plan_outputs

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_next_step_with_judge(self, group) -> List[PlanOutput]:
        plan_outputs = group.plans
        generation_params = GenerationParameters(
            model=self.planning_model,
            max_tokens=4096,
        )
        conversations_to_process = []
        for instance_id, plan_output in plan_outputs.items():
            if plan_output.success:
                continue
            # This should be done more efficiently,this should be gotten from the step to process
            instance = group.evaluator.instances[instance_id]
            mining_setup = get_mining_setup(instance)
            starting_inventory = instance.inspect_inventory()
            log_str = self.format_log_string(plan_output)
            objective = plan_output.task.task
            initial_plan = plan_output.initial_plan.initial_plan
            step_to_process = plan_output.steps[-1].candidate_language_outputs
            if len(step_to_process) == 0:
                continue
            step_candidate_str = ""
            for step_idx, step_candidate in enumerate(step_to_process):
                step_candidate_str += f"CANDIDATE STEP {step_idx}\n{step_candidate.response}\n\n"
            user_message = self.step_judge_user_prompt.format(objective=objective,
                                                              starting_inventory=starting_inventory,
                                                              mining_setup=mining_setup, logs=log_str,
                                                              plan=initial_plan,
                                                              analysis_step_str=step_candidate_str)
            conversations_to_process.append(
                (Conversation(messages=[Message(role="system", content=self.step_judge_system_prompt),
                                        Message(role="user", content=user_message)]), plan_output.meta["plan_id"]))

        step_outputs = [asyncio.ensure_future(
            self._generate_natural_language_batch(conversation[0], generation_params, meta={"type": "next_step_judge",
                                                                                            "plan_id": conversation[
                                                                                                1]})) for conversation
                        in conversations_to_process]
        responses = await asyncio.gather(*step_outputs)
        for idx, response in enumerate(responses):
            output = response[0]
            plan_id = output.meta["plan_id"]
            step_output = output.response.strip()
            # extra postprocessing step, change all <CHOICE> and <Choice> to <choice>
            # makes it more robust
            tags_to_lowercase = ["<Choice>", "<CHOICE>", "</Choice>", "</CHOICE>"]
            for tag in tags_to_lowercase:
                step_output = step_output.replace(tag, tag.lower())
            # add the output to the last step
            plan_outputs[plan_id].steps[-1].judge_language_output_step = output
            plan_outputs[plan_id].steps[-1].judge_step_str = step_output

            # split it by <choice>
            # Should we make it lowercase?
            if "<choice>" in step_output:
                step_idx = step_output.split("<choice>")[-1].strip()
                step_idx = step_idx.split("</choice>")[0].strip()
                try:
                    steps_to_choose_from = plan_outputs[plan_id].steps[-1].candidate_language_outputs
                    step = steps_to_choose_from[int(step_idx)]
                    step = step.meta["parsed_step"]
                except:
                    step = None
            else:
                # How should we actually handle this? When it wasn't a choice
                step = None
            if step:
                plan_outputs[plan_id].steps[-1].final_step = step

        return plan_outputs

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_next_step_programs(self, group: PlanningGroup) -> List[
        PlanOutput]:
        """Generate programs for the next step in a specific group"""
        plan_outputs = group.plans
        generation_params = GenerationParameters(
            model=self.config.mcts_kwargs['executor_model'],
            temperature=0.5,
            max_tokens=4096,
            logits={'7032': -100} # 'while' should never be sampled to prevent infinite loops
        )
        conversations_to_process = []

        for instance_id, plan_output in plan_outputs.items():
            if plan_output.success:
                continue

            instance = group.active_instances[instance_id]
            mining_setup = get_mining_setup(instance)
            starting_inventory = instance.inspect_inventory()
            executor_objective = plan_output.steps[-1].final_step

            user_message = self.step_executor_user_prompt.format(
                task=executor_objective,
                starting_inventory=starting_inventory,
                mining_setup=mining_setup
            )

            conversations_to_process.append((
                Conversation(messages=[
                    Message(role="system", content=self.step_executor_system_prompt),
                    Message(role="user", content=user_message)
                ]),
                {
                    "plan_id": plan_output.meta["plan_id"],
                    "group_id": group.group_id
                }
            ))

        step_outputs = [
            asyncio.ensure_future(
                self._generate_programs_batch(
                    conversation[0],
                    generation_params,
                    meta={
                        "type": "next_step_program",
                        "plan_id": conversation[1]["plan_id"],
                        "group_id": conversation[1]["group_id"]
                    }
                )
            )
            for conversation in conversations_to_process
        ]

        responses = await asyncio.gather(*step_outputs)

        for idx, response in enumerate(responses):
            output = response[0]
            plan_id = output.meta["plan_id"]
            # add the output program to the last step
            plan_outputs[plan_id].steps[-1].program = output

        return plan_outputs

    def _verify_response_is_python(self, content):
        code = content
        # Parse into an AST to verify that this is a program
        try:
            ast = compile(code, filename="<ast>", mode="exec")
        except SyntaxError:
            # Take the last line off and try again
            code = code.rsplit('\n', 1)[0] + '\n'
            ast = compile(code, filename="<ast>", mode="exec")

        return code

    def _extract_code_from_choice(self, choice) -> Optional[str]:
        """Extract code from a single completion choice"""
        code = ""
        try:
            content = choice.message.content
            code = self._verify_response_is_python(content)
            code = code.replace("from factorio_instance import *", "")
            return code, None
        except Exception as e:
            try:
                content = choice.message.content
                content_split = content.split('```python')
                code = content_split[1].split('```')[0].strip()
                text_response = content_split[0].strip()
                code = self._verify_response_is_python(code)
                code = code.replace("from factorio_instance import *", "")
                return code, text_response
            except Exception as e1:
                # Sometimes it samples a leading line, before writing unblocked python code.
                content = "\n".join(choice.message.content.split("\n")[1:])
                try:
                    code = self._verify_response_is_python(content)
                    code = code.replace("from factorio_instance import *", "")
                    return code, None
                except Exception as e2:
                    try:
                        content_split = content.split('from factorio_instance import *')
                        code = content_split[1].strip()
                        text_response = content_split[0].strip()
                        code = self._verify_response_is_python(code)
                        return code, text_response
                    except Exception as e2:
                        #print(f"Failed to extract code from choice after removing leading line and factorio_instance import: {str(e2)} \n\n`{content}`")
                        chain_of_thoughts = '"""\n'+content.strip().strip("\"")+'\n"""'
                        return chain_of_thoughts, content.strip()
                    #print(f"Failed to extract code from choice after removing leading line: {str(e2)}")
                print(f"Failed to extract code from choice: {str(e1)}")

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_programs_batch(self, conversation: Conversation,
                                       generation_params: GenerationParameters,
                                       meta={}
                                       ) -> List[Program]:
        """Generate multiple programs in a single API call using 'n' parameter"""
        formatted_messages = self.formatter.to_llm_messages(
            self.formatter.format_conversation(conversation)
        )
        if "claude" in generation_params.model:
            assert generation_params.n == 1, "Number of samples must be 1 for Claude"

        try:
            # Single API call to generate n_samples completions
            response = await self.llm.acall(
                messages=formatted_messages,
                n_samples=generation_params.n,
                temperature=generation_params.temperature,
                max_tokens=generation_params.max_tokens,
                logit_bias=generation_params.logit_bias,
                stop_sequences=generation_params.stop_sequences,
                model=generation_params.model,
                presency_penalty=generation_params.presency_penalty
            )

            programs = []
            try:
                messages = conversation.model_dump()['messages']
            except Exception as e:
                messages = conversation.dict()['messages']

            # Process all choices from the response
            if "claude" in generation_params.model:

                # Handle Claude response format
                code, text_response = self._extract_code_from_choice(response)
                if code:
                    programs.append(Program(
                        id=hash((code, json.dumps(messages))),
                        code=code,
                        conversation=conversation,
                        response=response.message.content,
                        token_usage=response.usage.total_tokens if hasattr(response, 'usage') else None,
                        completion_token_usage=response.usage.completion_tokens if hasattr(response, 'usage') else None,
                        prompt_token_usage=response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                        version=self.version,
                        version_description=self.version_description,
                        meta={"text_response": text_response,
                              "model": generation_params.model}
                    ))
                    if meta:
                        programs[0].meta.update(meta)
            else:
                # Handle OpenAI response format with multiple choices
                for choice in response.choices:
                    code, text_response = self._extract_code_from_choice(choice)
                    if code:
                        programs.append(Program(
                            id=hash((code, json.dumps(messages))),
                            code=code,
                            conversation=conversation,
                            response=choice.message.content,
                            token_usage=response.usage.total_tokens // generation_params.n if hasattr(response,
                                                                                                      'usage') else None,
                            completion_token_usage=response.usage.completion_tokens // generation_params.n if hasattr(
                                response,
                                'usage') else None,
                            prompt_token_usage=response.usage.prompt_tokens // generation_params.n if hasattr(response,
                                                                                                              'usage') else None,
                            version=self.version,
                            version_description=self.version_description,
                            meta={"text_response": text_response,
                                  "model": generation_params.model}
                        ))
                        if meta:
                            programs[-1].meta.update(meta)

            return programs

        except Exception as e:
            print(f"Batch program generation failed: {str(e)}")
            return []