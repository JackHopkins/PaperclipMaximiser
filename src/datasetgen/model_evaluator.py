import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")

import os
import ast
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from factorio_instance import FactorioInstance
import random
from skills.bottoms_up_sampler import eval_program_with_result_trace, get_mining_setup
load_dotenv()
from llm_factory import LLMFactory
from datasets.dataset_utils import instantiate_the_map, initialise_starting_scenario
class ModelEvaluator:
    def __init__(self, model_path, system_prompt_path, save_path, starting_scenarios_folder):
        
        self.model_path = model_path
        self.system_prompt_path = system_prompt_path
        self.llm_factory = LLMFactory(model_path)
        self.save_path = save_path
        self.starting_scenarios_folder = starting_scenarios_folder
        self.planning_addition_for_prompt = """
First bring out a thorough step-by-step plan how you can achieve this task and then create the python script to achieve the task.
For your plan, follow this structure:
1) What entities are needed for the task
2) What entities do we have on the map, in different entity inventories or in our inventory
3) What entities are we missing for the task
4) Execution -- Taking into account 1,2 and 3, what steps do we need to take to successfully carry out the task
"""


    def get_inventory_dict(self, inventory):
        inventory_dict = {}
        for item in inventory:
            if isinstance(item, tuple):
                inventory_dict[item[0]] = inventory[item]
            else:
                inventory_dict[item] = inventory[item]
        return inventory_dict

    def run_unsupervised_episode(self, instance, length: int, include_plan: bool = False):
        """
        Runs the traces, adds the plan to the prompt and saves the traces to the save path
        """
        traces = []
        for i in range(length):
            messages = [{"role": "system", "content": self.system_prompt}]
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a useful task that you can carry out in the current game and the python script to achieve the task"
            if include_plan:
                user_message += f"\n{self.planning_addition_for_prompt}"
                user_message = user_message.strip()
            messages.append({"role": "user", "content": user_message})
            response = self.llm_factory.call(messages=messages,
                                            temperature=0.7,
                                            max_tokens=4096)
            full_output = response.choices[0].message.content
            if "```python" in full_output:
                program = full_output.split("```python")[1]
                program = program.split("```")[0]
            else:
                print(f"Missing python code in response: {full_output}")
                continue
            output_list, result = eval_program_with_result_trace(instance, program)
            inventory_dict = self.get_inventory_dict(starting_inventory)
            traces.append({"program": program, "output": output_list, "result": result,
                            "starting_inventory": inventory_dict, "mining_setup": mining_setup,
                            "messages": messages, "planning": include_plan,
                            "full_output": full_output, 
                            "success": "error" not in result.lower()
                            })
            if "error" in result.lower():
                print(f"Error in program: {result}")
            else:
                print(f"Succcess")
        
        # save the traces to the save path
        unsupervised_save_path = os.path.join(self.save_path, "unsupervised_traces")
        # first get the number of folders in unsupervised_save_path
        num_folders = len([name for name in os.listdir(unsupervised_save_path) if os.path.isdir(os.path.join(unsupervised_save_path, name))])
        # create a new folder for the traces
        save_folder = os.path.join(unsupervised_save_path, f"trace_{num_folders}")
        os.makedirs(save_folder)
        with open(os.path.join(save_folder, "trace.jsonl"), "w") as f:
            for trace in traces:
                f.write(json.dumps(trace) + "\n")
        for idx, trace in enumerate(traces):
            # save the the program and output to a file
            with open(os.path.join(save_folder, f"program_{idx}_{trace['success']}.py"), "w") as f:
                f.write(trace["program"])
        

    def get_unsupervised_objective(self, instance):
        """
        Runs the traces, adds the plan to the prompt and saves the traces to the save path
        """
        starting_inventory = instance.inspect_inventory()
        self.init_system_prompt(instance)
        mining_setup = get_mining_setup(instance)
        messages = [{"role": "system", "content": self.system_prompt}]
        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a useful task that you can carry out in the current game and the python script to achieve the task"
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                            temperature=0.7,
                                            max_tokens=4096,
                                            stop_sequences = ["\n"])
        
        
        full_output = response.choices[0].message.content
        full_output = full_output.lower().replace("sure! the task i will carry out is", "").strip()
        return full_output


    def run_supervised_episode(self, instance, tries: int, task, include_plan: bool = False):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        self.init_system_prompt(instance)
        success = False
        traces = []
        for i in range(tries):
            messages = [{"role": "system", "content": self.system_prompt}]
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a python script that achieves the following task\n{task}"
            if include_plan:
                user_message += f"\n{self.planning_addition_for_prompt}"
                user_message = user_message.strip()
            messages.append({"role": "user", "content": user_message})
            response = self.llm_factory.call(messages=messages,
                                            temperature=0.7,
                                            max_tokens=4096)
            full_output = response.choices[0].message.content
            if "```python" in full_output:
                program = full_output.split("```python")[1]
                program = program.split("```")[0]
            else:
                print(f"Missing python code in response: {program}")
                continue
            output_list, result = eval_program_with_result_trace(instance, program)
            inventory_dict = self.get_inventory_dict(starting_inventory)
            traces.append({"program": program, "logs": output_list, "result": result, "full_output": full_output,
                           "starting_inventory": inventory_dict, "mining_setup": mining_setup,
                           "messages": messages, "planning": include_plan,
                           "success": "error" not in result.lower()})
            if "error" in result.lower():
                print(f"Error in program: {result}")
                continue
            success = True
            break
        return {"traces": traces, "success": success, "task": task}
    
    def read_in_prompt(self, path):
        with open(path, "r") as f:
            return f.read()

    def save_planner_executor_traces(self, output_dict, save_folder):
        # save the traces to the save path
        unsupervised_save_path = os.path.join(self.save_path, save_folder)
        # first get the number of folders in unsupervised_save_path
        num_folders = len([name for name in os.listdir(unsupervised_save_path) if os.path.isdir(os.path.join(unsupervised_save_path, name))])
        # create a new folder for the traces
        save_folder = os.path.join(unsupervised_save_path, f"episode_{num_folders}")
        os.makedirs(save_folder)
        general_detail_json = {"general_objective": output_dict["general_objective"],
                                "success": output_dict["success"]}
        # save the general details
        with open(os.path.join(save_folder, "general_details.json"), "w") as f:
            f.write(json.dumps(general_detail_json))
        step_traces = output_dict["traces"]
        # for each, create a folder and save the details
        for trace_idx, trace in enumerate(step_traces): 
            planner_details_json = {"step": trace["step"],
                                   "planning_output": trace["planning_output"],
                                   "success": trace["executor_output"]["success"],
                                   "inventory_dict": trace["inventory_dict"],
                                   "mining_setup": trace["mining_setup"],
                                   "messages": trace["messages"]}
            # create a folder for the trace
            trace_folder = os.path.join(save_folder, f"step_{trace_idx}")
            os.makedirs(trace_folder)
            # save the general details
            with open(os.path.join(trace_folder, f"planner_details.json"), "w") as f:
                f.write(json.dumps(planner_details_json))

            # save the executor traces into a jsonl file
            with open(os.path.join(trace_folder, f"executor_traces.jsonl"), "w") as f:
                for trace in trace["executor_output"]["traces"]:
                    f.write(json.dumps(trace) + "\n")
            # save each program to a file
            for program_idx, program_trace in enumerate(trace["executor_output"]["traces"]):
                with open(os.path.join(trace_folder, f"program_{program_idx}_{program_trace['success']}.py"), "w") as f:
                    f.write(program_trace["program"])


    def run_external_planning_episode(self, number_of_tasks: int, episode_length = 7, executor_tries = 1, instance = None, task:str = None):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        if not instance:
            # instantiate the instance
            instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory={})
        
        planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt.md"
        planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt.md"
        system_prompt = self.read_in_prompt(planning_agent_system_prompt_path)
        user_prompt_base = self.read_in_prompt(planning_agent_user_prompt)
        for i in range(number_of_tasks):
            logs = []
            planning_output = ""
            current_step = 0
            traces = []
            success = False
            if not task:
                task = self.get_unsupervised_objective(instance)
            while "#objective completed" not in planning_output.lower() and current_step < episode_length:
                log_str = "\n\n".join(logs) if logs else "The agent has not yet interacted with the world"
                starting_inventory = instance.inspect_inventory()
                inventory_dict = self.get_inventory_dict(starting_inventory)
                mining_setup = get_mining_setup(instance)
                messages = [{"role": "system", "content": system_prompt}]
                user_message = user_prompt_base.format(objective = task, starting_inventory=starting_inventory, mining_setup=mining_setup, logs=log_str)
                messages.append({"role": "user", "content": user_message})
                response = self.llm_factory.call(model = "gpt-4o",
                                                    messages=messages,
                                                    temperature=0.7,
                                                    max_tokens=4096)

                current_step += 1
                full_output = response.choices[0].message.content
                if "#output" in full_output.lower():
                    planning_output = full_output.lower().split("#output")[-1].strip()
                    traces.append({"step": current_step, "executor_output": {"success": True, "traces": []}, "planning_output": planning_output,
                                   "inventory_dict": inventory_dict, "mining_setup": mining_setup, "messages": messages})
                    success = True
                    break
                # get the output between two #STEP tags
                if "#STEP" in full_output:
                    planning_output = full_output.split("#STEP")[-2].strip()
                   # planning_output = planning_output.split("#STEP")[0]
                else:
                    print(f"Missing planning output in response: {full_output}")
                    continue
                output = self.run_supervised_episode(instance, executor_tries, planning_output, include_plan=True)
                trace_logs = []
                for trace in output["traces"]:
                    trace_logs+= trace["logs"]
                log_str = f"Step {current_step}: {planning_output}\nLogs from output\n{trace_logs}"
                logs.append(log_str)
                traces.append({"step": current_step, "executor_output": output, "planning_output": planning_output,
                               "inventory_dict": inventory_dict, "mining_setup": mining_setup, "messages": messages})
            output =  {"general_objective": task, "traces": traces, "success": success}
            self.save_planner_executor_traces(output, "planner_executor_traces")

    
    def init_system_prompt(self, instance):
        api_description = instance.get_system_prompt()
        system_prompt_path = self.system_prompt_path
        # read in the system prompt
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
        self.system_prompt = system_prompt.format(schema=api_description)
        # change all " marks to '
        #self.system_prompt.replace('"', "'")

    def run_simulations_from_starting_scenarios(self, list_of_starting_scenario_folders: List[str], 
                                                num_episodes: int, episode_length: int, include_plan: bool = False, 
                                                episode_type = "external_planning"):
        """
        Runs the simulations from the starting scenarios
        args:
        list_of_starting_scenario_folders: List[str] -- the list of starting scenario folders to run the simulations from
        num_episodes: int -- the number of episodes to run
        episode_length: int -- the length of each episode
        include_plan: bool -- whether to get the LLM to generate a plan before the task or only the policy
        """
        # start the factorio instance
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory={})
        self.init_system_prompt(instance) # Inits the system prompt
        for starting_scenario_folder in list_of_starting_scenario_folders:
            starting_scenario_path = os.path.join(self.starting_scenarios_folder, starting_scenario_folder)
            for i in range(num_episodes):
                starting_scenario = initialise_starting_scenario(starting_scenario_path) # Gets the starting scenario details
                # instantiate the map
                result = instantiate_the_map(starting_scenario, instance, self.starting_scenarios_folder)
                if not result["success"]:
                    print(f"Error in starting scenario: {result['error']}")
                    continue
                # runs the actual episode
                if episode_type == "external_planning":
                    self.run_external_planning_episode(instance = instance, number_of_tasks= episode_length)
                else:
                    self.run_unsupervised_episode(instance, episode_length, include_plan)

def get_all_folders_in_path(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]


if __name__ == "__main__":
    model_path = r"ft:gpt-4o-2024-08-06:paperplane-ai:fact-self-gen-planning:AQzcPI91"
    evaluator = ModelEvaluator(model_path, 
                               #r"prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_self_gen.md",
                               r"prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_supervised.md",
                               save_path = r"datasets\finetuned_model_gen", # Where to save the traces
                               starting_scenarios_folder=r"skills\data_scenarios\starting_scenarios" # Where the starting scenarios are stored
                               )
    unsupervised_trace = True
    #evaluator.run_external_planning_episode(number_of_tasks = 2)
    if unsupervised_trace:
        starting_scenarios = ["full_scratch"]
        #starting_scenarios = get_all_folders_in_path(r"skills\data_scenarios\starting_scenarios")
        #starting_scenarios = ["multiple_entiti_environment"]
        evaluator.run_simulations_from_starting_scenarios(starting_scenarios, 2, 2, include_plan=True)
    else:
       objective = "You need to manually mine 50 iron ore, 50 copper ore and 70 coal"
       evaluator.run_supervised_episode(5, objective, include_plan=True)
