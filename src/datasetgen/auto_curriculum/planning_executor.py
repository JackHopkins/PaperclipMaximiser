from factorio_types import BeltGroup
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from factorio_instance import FactorioInstance
import random
from skills.bottoms_up_sampler import eval_program_with_result_trace, get_mining_setup
load_dotenv()
from llm_factory import LLMFactory
from datasetgen.auto_curriculum.dataset_utils import instantiate_the_map, initialise_starting_scenario
from skills.skills_db import SkillsDB
from datasetgen.mcts.game_state import GameState

class PlanningExecutor:
    def __init__(self, instance, step_executor_model, planner_model, step_executor_prompt_path, step_generator_prompt_path, 
                 step_judge_prompt_path, example_plan_prompt_path):
        
        self.step_executor_model = step_executor_model
        self.planner_model = planner_model
        self.step_executor_prompt_path = step_executor_prompt_path
        self.step_generator_prompt_path = step_generator_prompt_path
        self.step_judge_prompt_path = step_judge_prompt_path
        self.example_plan_prompt_path = example_plan_prompt_path
        self.instance = instance
        self.api_description = instance.get_system_prompt()
        self.llm_factory = LLMFactory(step_executor_model)
        self.skills_db = SkillsDB()
        self.step_executor_system_prompt, self.step_executor_user_prompt = self.read_in_prompts(step_executor_prompt_path)
        self.step_generator_system_prompt, self.step_generator_user_prompt = self.read_in_prompts(step_generator_prompt_path)
        self.step_judge_system_prompt, self.step_judge_user_prompt = self.read_in_prompts(step_judge_prompt_path)
        self.example_plan_system_prompt, self.example_plan_user_prompt = self.read_in_prompts(example_plan_prompt_path)

        # format the 2 system prompts
        self.step_executor_system_prompt = self.step_executor_system_prompt.format(schema = self.api_description)
        self.example_plan_system_prompt = self.example_plan_system_prompt.format(schema = self.api_description)

        self.number_of_candidate_steps = 3
        self.number_of_executor_retries = 3
        self.number_of_judge_retries = 3
        self.episode_max_length = 10

    def get_inventory_dict(self, inventory):
        inventory_dict = {}
        for item in inventory:
            if isinstance(item, tuple):
                inventory_dict[item[0]] = inventory[item]
            else:
                inventory_dict[item] = inventory[item]
        return inventory_dict
    


    def get_plan_for_task_from_executor(self, task):
        user_message = self.example_plan_user_prompt.format(task = task)
        messages = [{"role": "system", "content": self.example_plan_system_prompt}]
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                        temperature=0.7,
                                        max_tokens=4096,
                                        stop_sequences = ["```"],
                                        )
        full_output = response.choices[0].message.content
        full_output = full_output.strip()
        new_line_idx = full_output.rfind("\n")
        if new_line_idx != -1:
            full_output = full_output[:new_line_idx].strip()
        return full_output


    def get_next_step(self,task,starting_inventory, mining_setup,
                      plan, log_str):
        outputs = []
        for i in range(self.number_of_candidate_steps):
            system_prompt = self.step_generator_system_prompt
            user_prompt = self.step_generator_user_prompt.format(objective = task, starting_inventory=starting_inventory, mining_setup=mining_setup, logs=log_str, plan = plan)
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": user_prompt})
            response = self.llm_factory.call(model = self.planner_model,
                                                messages=messages,
                                                temperature=0.7,
                                                max_tokens=4096)

            if "claude" in self.planner_model:
                full_output = response.content[0].text
            else:
                full_output = response.choices[0].message.content
            if "#output" in full_output.lower() and "#step" not in full_output.lower():
                outputs.append({"full_output": full_output, "messages": messages, "completion": True})
                break
            outputs.append({"full_output": full_output, "messages": messages, "completion": False})
        return outputs
    

    def get_next_step_judge(self, task, starting_inventory, mining_setup, plan, log_str):
        step = None
        outputs = self.get_next_step(task, starting_inventory, mining_setup, plan, log_str)
        # check for completions
        for output in outputs:
            if output["completion"]:
                step = output["full_output"].lower().split("#output")[-2].strip()
                return {"meta": {"type": "single","step_outputs": []}, "full_output": output["full_output"],
                        "messages": output["messages"], "step": step, "completion": True}
            
        candidates = [x["full_output"] for x in outputs]
        step_candidate_str = ""
        for step_idx, step_candidate in enumerate(candidates):
            step_candidate_str += f"Step {step_idx}\n{step_candidate}\n\n"
        
        judge_system_prompt = self.step_judge_system_prompt
        judge_user_prompt_base = self.step_judge_user_prompt
        messages = [{"role": "system", "content": judge_system_prompt}]
        user_message = judge_user_prompt_base.format(objective = task, starting_inventory=starting_inventory, 
                                                     mining_setup=mining_setup, logs=log_str, plan = plan,
                                                     analysis_step_str = step_candidate_str)
        messages.append({"role": "user", "content": user_message})
        for i in range(self.number_of_judge_retries):
            response = self.llm_factory.call(model = self.planner_model,
                                            messages=messages,
                                            temperature=0.4,
                                            max_tokens=4096)

            if "claude" in self.planner_model:
                full_output = response.content[0].text
            else:
                full_output = response.choices[0].message.content
            # split it by #step
            if "#STEP" in full_output:
                step = full_output.split("#STEP")[-2].strip()
                break

        if step is None:
            raise ValueError("No step was found fro judge after retries")
        return {"meta": {"type": "judge", "step_outputs": outputs}, "full_output": full_output,
                 "messages": messages, "step": step, "completion": False}

    def run_supervised_episode(self, instance, task, include_plan: bool = False):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        success = False
        traces = []
        # get the starting state of the game
        game_state = GameState.from_instance(instance)
        for i in range(self.number_of_executor_retries):
            if i != 0:
                # reset the game
                instance.reset(game_state)
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            
            system_prompt = self.step_executor_system_prompt
            user_message = self.step_executor_user_prompt.format(task = task, starting_inventory=starting_inventory, mining_setup=mining_setup)
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": user_message})
            response = self.llm_factory.call(messages=messages,
                                            temperature=0.5,
                                            max_tokens=4096)
            full_output = response.choices[0].message.content
            if "```python" in full_output:
                program = full_output.split("```python")[1]
                program = program.split("```")[0]
            else:
                print(f"Missing python code in response: {program}")
                continue
            output_list, result, error = eval_program_with_result_trace(instance, program)
            inventory_dict = self.get_inventory_dict(starting_inventory)
            traces.append({"program": program, "logs": output_list, "result": result, "full_output": full_output,
                           "starting_inventory": inventory_dict, "mining_setup": mining_setup,
                           "messages": messages, "planning": include_plan,
                           "success": "error" not in result.lower()})
            if error:
                print(f"Error in program: {result}")
                continue
            success = True
            break
        return {"traces": traces, "success": success, "task": task}
    
    def read_in_prompts(self, path):
        system_prompt_path = os.path.join(path, "system_prompt.md")
        user_prompt_path = os.path.join(path, "user_prompt.md")
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
        with open(user_prompt_path, "r") as f:
            user_prompt = f.read()
        return system_prompt, user_prompt

    def save_planner_executor_traces(self, output_dict, save_folder):
        # save the traces to the save path
        unsupervised_save_path = os.path.join(self.save_path, save_folder)
        # first get the number of folders in unsupervised_save_path
        num_folders = len([name for name in os.listdir(unsupervised_save_path) if os.path.isdir(os.path.join(unsupervised_save_path, name))])
        # create a new folder for the traces
        save_folder = os.path.join(unsupervised_save_path, f"episode_{num_folders}")
        os.makedirs(save_folder)
        general_detail_json = {"general_objective": output_dict["general_objective"],
                                "success": output_dict["success"],
                                "mining_setup": output_dict["traces"][0]["mining_setup"],
                                "starting_inventory": output_dict["traces"][0]["inventory_dict"]}
        # save the general details
        with open(os.path.join(save_folder, "general_details.json"), "w") as f:
            f.write(json.dumps(general_detail_json))
        step_traces = output_dict["traces"]
        # for each, create a folder and save the details
        for trace_idx, step_trace in enumerate(step_traces): 
            planner_details_json = {"step_idx": step_trace["step_idx"],
                                    "step": step_trace["step"],
                                   "planning_output": step_trace["planning_output"],
                                   "success": step_trace["executor_output"]["success"],
                                   "inventory_dict": step_trace["inventory_dict"],
                                   "mining_setup": step_trace["mining_setup"],
                                   "messages": step_trace["messages"],
                                   "meta": step_trace["meta"]}
            # create a folder for the trace
            trace_folder = os.path.join(save_folder, f"step_{trace_idx}")
            os.makedirs(trace_folder)
            # save the general details
            with open(os.path.join(trace_folder, f"planner_details.json"), "w") as f:
                f.write(json.dumps(planner_details_json))

            # save the executor traces into a jsonl file
            with open(os.path.join(trace_folder, f"executor_traces.jsonl"), "w") as f:
                for trace in step_trace["executor_output"]["traces"]:
                    f.write(json.dumps(trace) + "\n")
            # save each program to a file
            for program_idx, program_trace in enumerate(step_trace["executor_output"]["traces"]):
                with open(os.path.join(trace_folder, f"program_{program_idx}_{program_trace['success']}.py"), "w") as f:
                    f.write(program_trace["program"])

        # if success, save to db
        if output_dict["success"]:
            self.skills_db.save_function(name = output_dict["general_objective"], 
                                         implementation = "N/A",
                                         description = "N/A",
                                         dependencies = [],
                                         signature = "N/a",
                                         implementation_model = self.executor_model,
                                         version = "planner_executor_v1.0",
                                         meta = output_dict)

    def run_external_planning_episode(self, number_of_tasks: int, task:str = None):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        plan = self.get_plan_for_task_from_executor(task)
        
        for i in range(number_of_tasks):
            logs = []
            planning_output = ""
            current_step = 0
            traces = []
            success = False
            while current_step < self.episode_max_length:
                log_str = "\n\n".join(logs) if logs else "The agent has not yet interacted with the world"
                starting_inventory = self.instance.inspect_inventory()
                inventory_dict = self.get_inventory_dict(starting_inventory)
                mining_setup = get_mining_setup(self.instance)
                planner_output = self.get_next_step_judge(task, starting_inventory, 
                                                       mining_setup, plan, log_str)
                current_step += 1
                if planner_output["completion"]:
                    traces.append({"step_idx": current_step, "executor_output": {"success": True, "traces": []}, "step": planner_output["step"],
                                   "inventory_dict": inventory_dict, "mining_setup": mining_setup, "messages": planner_output["messages"],
                                   "meta": planner_output["meta"], "planning_output": planner_output["full_output"]})
                    success = True
                    break
                planning_output = planner_output["step"]
                pre_executor_mining_setup = self.instance.get_entities()
                output = self.run_supervised_episode(self.instance, planning_output, 
                                                     include_plan=True)
                post_executor_mining_setup = self.instance.get_entities()
                new_entities, removed_entities = self.get_changed_entities(pre_executor_mining_setup, post_executor_mining_setup)
                trace_logs = output["traces"][-1]["logs"]
                log_str = f"Step {current_step}: {planning_output}\nLogs from output\n{trace_logs}"
                if new_entities:
                    new_entity_str_list = [f"{entity}" for entity in new_entities if entity.name != "transport-belt"]
                    new_entity_str_list = "\n".join(new_entity_str_list)
                    log_str += f"\nThe following entities have been added by the agent\n{new_entity_str_list}"
                if removed_entities:
                    removed_entity_str_list = [f"{entity}" for entity in removed_entities if entity.name != "transport-belt"]
                    removed_entity_str_list = "\n".join(removed_entity_str_list)
                    log_str += f"\nThe following entities have been removed by the agent\n{removed_entity_str_list}"
                logs.append(log_str)
                traces.append({"step_idx": current_step, "step":planning_output,  "executor_output": output, "planning_output": planner_output["full_output"],
                               "inventory_dict": inventory_dict, "mining_setup": mining_setup, "messages": planner_output["messages"],
                               "meta": planner_output["meta"]})
            output =  {"general_objective": task, "traces": traces, "success": success}
            self.save_planner_executor_traces(output, "planner_executor_traces")

    

    def get_changed_entities(self, baseline_setup, new_setup):
        new_entities = []
        removed_entities = []
        for entity in new_setup:
            if isinstance(entity, BeltGroup):
                continue
            exists = False
            for baseline_entity in baseline_setup:
                if isinstance(baseline_entity, BeltGroup):
                    continue
                if entity.name == baseline_entity.name and entity.position == baseline_entity.position:
                    exists = True
            if not exists:
                new_entities.append(entity)
        
        for entity in baseline_setup:
            if isinstance(entity, BeltGroup):
                continue
            exists = False
            for new_entity in new_setup:
                if isinstance(new_entity, BeltGroup):
                    continue
                if entity.name == new_entity.name and entity.position == new_entity.position:
                    exists = True
            if not exists:
                removed_entities.append(entity)
        return new_entities, removed_entities


    def run_simulation(self, game_state:str, task = None):
        # start the factorio instance
        self.instance.reset(game_state)
        self.run_external_planning_episode(task = task)

def get_all_folders_in_path(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def sample_random_folders(folders, num_samples):
    return random.sample(folders, num_samples)


if __name__ == "__main__":
    
    step_executor_model_path = "ft:gpt-4o-2024-08-06:paperplane-ai:fact-instruct-1:ATSVGf4d:ckpt-step-214"
    planner_model = "claude-3-5-sonnet-20241022"
    step_executor_prompt_path = "prompts/bottoms_up_prompts/finetuning_prompts/step_supervised"
    step_generator_prompt_path = "prompts/bottoms_up_prompts/finetuning_prompts/step_generator"
    executor_plan_prompt_path = "prompts/bottoms_up_prompts/finetuning_prompts/executor_plan"
    step_judge_prompt_path = "prompts/bottoms_up_prompts/finetuning_prompts/step_judge"
    evaluator = PlanningExecutor(step_executor_model = step_executor_model_path, 
                                 planner_model = planner_model,
                                 step_executor_prompt_path=step_executor_prompt_path,
                                 step_generator_prompt_path=step_generator_prompt_path,
                                 step_judge_prompt_path=step_judge_prompt_path,
                                 example_plan_prompt_path = executor_plan_prompt_path,
                                                              )
    game_string = "test"
    task = "Get 5 offshore pumps"
    evaluator.run_simulation(game_state = game_string, task = task)
                                                          
