import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")
from factorio_types import BeltGroup
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
from datasetgen.auto_curriculum.dataset_utils import instantiate_the_map, initialise_starting_scenario
from skills.skills_db import SkillsDB
from datasetgen.mcts.game_state import GameState
class ModelEvaluator:
    def __init__(self, executor_model, system_prompt_path, save_path, starting_scenarios_folder, objective_model = None):
        
        self.executor_model = executor_model
        self.system_prompt_path = system_prompt_path
        self.llm_factory = LLMFactory(executor_model)
        self.save_path = save_path
        self.starting_scenarios_folder = starting_scenarios_folder
        self.skills_db = SkillsDB()
        self.planner_model = "claude-3-5-sonnet-20241022"
        self.objective_model = objective_model if objective_model else executor_model
        self.planning_addition_for_prompt = """
First bring out a thorough step-by-step plan how you can achieve this task and then create the one python script to achieve the full task.
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
                                         model = self.objective_model,
                                        temperature=0.7,
                                        max_tokens=4096,
                                        stop_sequences = ["\n"])
        
        
        full_output = response.choices[0].message.content
        full_output = full_output.lower().replace("sure! the task i will carry out is", "").strip()
        if "." in full_output:
            full_output = full_output.split(".")[0]
        return full_output


    def get_general_plan_for_task_with_env(self, instance, task):
        self.init_system_prompt(instance)
        messages = [{"role": "system", "content": self.system_prompt}]
        starting_inventory = instance.inspect_inventory()
        mining_setup = get_mining_setup(instance)
        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. The user has given you the following task\nPrint the entities that are missing to achieve: {task}\nPrevious tasks that have been completed with logs: This is the first call to the agent"
        user_message += self.planning_addition_for_prompt
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                        temperature=0.5,
                                        max_tokens=4096,
                                        #stop_sequences = ["```"],
                                        )
        full_output = response.choices[0].message.content

        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a python script that achieves the following task\n{task}"
        #user_message += self.planning_addition_for_prompt
        #user_message += self.planning_addition_for_prompt
        planning_addition_for_prompt = """
First bring out a thorough step-by-step plan how you can achieve this task and then create the python script to achieve the task.
For your plan, follow this structure:
1) What entities are needed for the task. If you don't know the required number for an entity, leave it as 'will be calculated later'
2) Execution -- What steps do we need to take to successfully carry out the task
"""     
        planning_addition_for_prompt = """
First bring out a general step-by-step list of steps you need to carry out to achieve this task and then create the python script to achieve the task. The plan should not mention any specific entities on the map, only general steps that need to be taken for a task like this
"""     

        user_message += planning_addition_for_prompt
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                        temperature=0.3,
                                        max_tokens=4096,
                                        stop_sequences = ["```"],
                                        )
        full_output = response.choices[0].message.content
        # get everything until the last \ sign
        last_backslash = full_output.strip().rfind("\n")
        if last_backslash != -1:
            full_output = full_output[:last_backslash]

        plan = full_output.strip()
        #return plan
        initial_planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_draft_initial_plan_v4.md"
        initial_planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_draft_initial_plan_v4.md"
        initial_system_prompt = self.read_in_prompt(initial_planning_agent_system_prompt_path)
        initial_user_prompt_base = self.read_in_prompt(initial_planning_agent_user_prompt)

        planning_model = self.planner_model

        logs = []
        planning_output = ""
        current_step = 0
        while "#ENTITIES" not in planning_output:
            log_str = "\n\n".join(logs) if logs else "The agent has not yet interacted with the world"
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            messages = [{"role": "system", "content": initial_system_prompt}]
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            user_message = initial_user_prompt_base.format(objective = task, starting_inventory=starting_inventory, mining_setup=mining_setup,
                                                            logs=log_str, plan = plan)
            messages.append({"role": "user", "content": user_message})
            response = self.llm_factory.call(model = planning_model,
                                                messages=messages,
                                                temperature=0.7,
                                                max_tokens=4096)

            current_step += 1
            if "claude" in planning_model:
                entity_analysis = response.content[0].text
            else:
                entity_analysis = response.choices[0].message.content
            if "#entities" in entity_analysis.lower():
                entity_analysis = entity_analysis.lower().split("#entities")[-2].strip()
                return entity_analysis

            # get the output between two #STEP tags
            if "#COMMAND" in entity_analysis:
                planning_output = entity_analysis.split("#COMMAND")[-2].strip()
            else:
                print(f"Missing planning output in response: {entity_analysis}")
                continue
            output = self.run_supervised_episode(instance, 1, planning_output, include_plan=True)
            trace_logs = []
            for trace in output["traces"]:
                trace_logs+= trace["logs"]
            log_str = f"Step {current_step}: {planning_output}\nLogs from output\n{trace_logs}"
            logs.append(log_str)
        # get everything after "Required entities"
        entity_analysis = entity_analysis.split("#ENTITIES")[-1]
        return entity_analysis

    def get_plan_for_task_from_executor(self, instance, task):
        self.init_system_prompt(instance)
        messages = [{"role": "system", "content": self.system_prompt}]
        starting_inventory = instance.inspect_inventory()
        mining_setup = get_mining_setup(instance)
        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Bring out the plan and python policy for the objective\n{task}"
        user_message = f"Your starting inventory is {{}}. Your initial mining setup is: There are no entities on the map. Bring out the list of entities required for the objective\n{task}"
        user_message += "\nFirst plan step by step and bring out a thorough list of entities you need to craft to achieve this objective, do not forget required fuel. Then create the python script to achieve the task. The list of entities should incldue all the entities that you need to craft to achieve this objective"
        
        #user_message += self.planning_addition_for_prompt
        #user_message += f"\nFirst bring out a thorough step-by-step list of steps you need to carry out to achieve this task and the entities you require for this task. Then create the python script to achieve the task."
        messages.append({"role": "user", "content": user_message})
        #assistant_message = "```python\n"
        #messages.append({"role": "assistant", "content": assistant_message})
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
        # split by ```
        split_plan = full_output.split("```")
        plan_string = split_plan[0]
        program = split_plan[1]
        # split program by """
        split_program = program.split('"""')
        return full_output

    def get_general_plan_for_task(self, instance, task):
        self.init_system_prompt(instance)
        messages = [{"role": "system", "content": self.system_prompt}]
        starting_inventory = instance.inspect_inventory()
        mining_setup = get_mining_setup(instance)
        user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a python script that achieves the following task\n{task}"
        user_message += "\nBring out a general step-by-step list of steps you need to carry out to achieve this task. Bring out a list of entities you need for the task"
        
        #user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Print out the entities to achieve the following task\n{task}"
        #user_message += "\nFirst analyse what entities you need to achieve the task. Then in python code print out the entities and the amount of each entity you need\nFor connection entities like transport belts, poles or pipes, calculate the amount by using using get_connection_amount function. Use the actual positions where you will place the entities to calculate the amount of connection entities needed"
        messages.append({"role": "user", "content": user_message})
        response = self.llm_factory.call(messages=messages,
                                        temperature=0.3,
                                        max_tokens=4096,
                                        #stop_sequences = ["```"],
                                        )
        full_output = response.choices[0].message.content
        #if "```python" in full_output:
        #        program = full_output.split("```python")[1]
        #        program = program.split("```")[0]
        #else:
        #    print(f"Missing python code in response: {program}")
        #output_list, result = eval_program_with_result_trace(instance, program)
        
        plan = full_output.strip()

        initial_planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_draft_initial_plan.md"
        initial_planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_draft_initial_plan_v2.md"
        initial_system_prompt = self.read_in_prompt(initial_planning_agent_system_prompt_path)
        initial_user_prompt_base = self.read_in_prompt(initial_planning_agent_user_prompt)
        starting_inventory = instance.inspect_inventory()
        mining_setup = get_mining_setup(instance)
        messages = [{"role": "system", "content": initial_system_prompt}]
        user_message = initial_user_prompt_base.format(objective = task, starting_inventory=starting_inventory, mining_setup=mining_setup, input_plan = plan)
        messages.append({"role": "user", "content": user_message})
        planning_model = self.planner_model
        response = self.llm_factory.call(model = planning_model,
                                            messages=messages,
                                            temperature=0.7,
                                            max_tokens=4096)
        if "claude" in planning_model:
            entity_analysis = response.content[0].text
        else:
            entity_analysis = response.choices[0].message.content
        # get everything after "Required entities"
        entity_analysis = entity_analysis.split("Required entities")[-1]
        return entity_analysis

    def run_supervised_mcts(self, instance, tries: int, task, include_plan: bool = False):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        planning_addition_for_prompt = """
First bring out a thorough step-by-step plan how you can achieve this task and then create the python script to achieve the task.
For your plan, follow this structure:
1) What entities are needed for the task
2) What entities do we have on the map, in different entity inventories or in our inventory
3) What entities are we missing for the task
"""
        self.init_system_prompt(instance)
        success = False
        traces = []
        # get the starting state of the game
        save_string = instance._save_entity_state(distance=1000)
        logs = []
        for i in range(tries):
            #if i != 0:
            #    # reset the game
            #    instance._load_entity_state(save_string)
            messages = [{"role": "system", "content": self.system_prompt}]
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a python script that achieves the following task\n{task}"
            log_str = "\n\n".join(logs) if logs else ""
            log_str += f"Logs from previous executions to solve this task\n{log_str}" if log_str else "" 
            if log_str:
                user_message += f"\n{log_str}"
            if include_plan:
                user_message += f"\n{self.planning_addition_for_prompt}"
                user_message = user_message.strip()
            messages.append({"role": "user", "content": user_message})
            response = self.llm_factory.call(messages=messages,
                                            temperature=0.4,
                                            max_tokens=4096)
            full_output = response.choices[0].message.content
            if "```python" in full_output:
                program = full_output.split("```python")[1]
                program = program.split("```")[0]
            else:
                print(f"Missing python code in response: {program}")
                continue
            output_list, result, error = eval_program_with_result_trace(instance, program)
            logs_from_execution = "\n".join(output_list)
            logs.append(logs_from_execution)
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

    def get_next_step(self, system_prompt, user_prompt_base, task, 
                      starting_inventory, mining_setup, plan, log_str,
                      number_of_steps = 4):
        outputs = []
        for i in range(number_of_steps):
            messages = [{"role": "system", "content": system_prompt}]
            user_message = user_prompt_base.format(objective = task, starting_inventory=starting_inventory, mining_setup=mining_setup, logs=log_str, plan = plan)
            messages.append({"role": "user", "content": user_message})
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
    

    def get_next_step_judge(self, system_prompt, user_prompt_base, task, 
                      starting_inventory, mining_setup, plan, log_str,
                      ):
        tries = 4
        step = None
        outputs = self.get_next_step(system_prompt, user_prompt_base, task,
                                             starting_inventory, mining_setup, plan, 
                                             log_str, 2)
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
        judge_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_step_judge.md"
        judge_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_step_judge.md"
        judge_system_prompt = self.read_in_prompt(judge_system_prompt_path)
        judge_user_prompt_base = self.read_in_prompt(judge_user_prompt)
        messages = [{"role": "system", "content": judge_system_prompt}]
        user_message = judge_user_prompt_base.format(objective = task, starting_inventory=starting_inventory, 
                                                     mining_setup=mining_setup, logs=log_str, plan = plan,
                                                     analysis_step_str = step_candidate_str)
        messages.append({"role": "user", "content": user_message})
        for i in range(tries):
            response = self.llm_factory.call(model = self.planner_model,
                                            messages=messages,
                                            temperature=0.4,
                                            max_tokens=4096)

            if "claude" in self.planner_model:
                full_output = response.content[0].text
            else:
                full_output = response.choices[0].message.content
            # get the output after OUTPUT
            if "#OUTPUT" in full_output:
                step = full_output.split("#OUTPUT")[-2].strip()
            
            # split it by #step
            if "#STEP" in full_output:
                step = full_output.split("#STEP")[-2].strip()
                break

        if step is None:
            raise ValueError("No step was found fro judge after retries")
        return {"meta": {"type": "judge", "step_outputs": outputs}, "full_output": full_output,
                 "messages": messages, "step": step, "completion": False}

    def run_supervised_episode(self, instance, tries: int, task, include_plan: bool = False):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        self.init_system_prompt(instance)
        success = False
        traces = []
        # get the starting state of the game
        game_state = GameState.from_instance(instance)
        for i in range(tries):
            if i != 0:
                # reset the game
                instance.reset(game_state)
            messages = [{"role": "system", "content": self.system_prompt}]
            starting_inventory = instance.inspect_inventory()
            mining_setup = get_mining_setup(instance)
            user_message = f"Your starting inventory is {starting_inventory}. Your initial mining setup is: {mining_setup}. Create a python script that achieves the following task\n{task}"
            if include_plan:
                user_message += f"\n{self.planning_addition_for_prompt}"
                user_message = user_message.strip()
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
            output_list, result, success = eval_program_with_result_trace(instance, program)
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

    def run_external_planning_episode(self, number_of_tasks: int, episode_length = 10, executor_tries = 3, instance = None, task:str = None):
        """
        Run the supervised task
        Need to implement saving the successful trace
        """
        #ob = self.get_unsupervised_objective(instance)
        #task = self.run_supervised_mcts(instance, executor_tries, task, include_plan = True)
        plan = self.get_plan_for_task_from_executor(instance, task)
        #plan = "To complete this objective, we need to create a basic iron ore mining operation. We'll need a burner mining drill to extract the iron ore and a wooden chest to store it. Since the chest needs to be placed 10 spaces away from the drill, we'll also need transport belts or inserters to move the ore from the drill to the chest.\n\nHere's a breakdown of the entities we need to craft:\n\n1. Burner Mining Drill:\n   - Recipe: 3 iron gear wheels, 3 iron plates, 1 stone furnace\n   - Total raw resources needed: 9 iron plates, 5 stone\n\n2. Wooden Chest:\n   - Recipe: 2 wood\n   - Total raw resources needed: 2 wood\n\n3. Burner Inserter (to insert ore into the chest):\n   - Recipe: 1 iron gear wheel, 1 iron plate\n   - Total raw resources needed: 3 iron plates\n\n4. Transport Belts (optional, if needed):\n   - Recipe: 1 iron gear wheel, 1 iron plate (crafts 2 belts)\n   - Total raw resources needed per pair: 3 iron plates\n\n5. Fuel for the burner mining drill and inserter:\n   - Coal or wood (exact amount depends on availability and usage rate)\n\nIn total, we'll need at least 15 iron plates, 5 stone, and some coal or wood for fuel. We'll also need some additional iron plates if we need to craft transport belts.\n\nWe should also consider crafting a stone furnace if we need to smelt the iron plates from iron ore. This would require an additional 5 stone."
        if not instance:
            # instantiate the instance
            instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory={})
        #planning_output = "Create the iron ore mine into a wooden chest you 10 squares away"
        #planning_output = "Put down a drill at a iron patch, put down a chest 10 spaces away and create a iron ore mine from the drill to the chest. Check that the chest gets filled with iron ore"
        #output = self.run_supervised_episode(instance, executor_tries, planning_output, include_plan=True)
                
        #planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt.md"
        #planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt.md"
        #system_prompt = self.read_in_prompt(planning_agent_system_prompt_path)
        #user_prompt_base = self.read_in_prompt(planning_agent_user_prompt)

        planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_draft_with_initial_plan_v2.md"
        planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_draft_with_initial_plan_v2.md"
        system_prompt = self.read_in_prompt(planning_agent_system_prompt_path)
        user_prompt_base = self.read_in_prompt(planning_agent_user_prompt)
        
        #multiple_planning_agent_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_multiple.md"
        #multiple_planning_agent_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_multiple.md"
        #system_prompt_multiple = self.read_in_prompt(multiple_planning_agent_system_prompt_path)
        #user_prompt_base_multiple = self.read_in_prompt(multiple_planning_agent_user_prompt)    
#
        #judge_system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_system_prompt_judge.md"
        #judge_user_prompt = r"prompts\bottoms_up_prompts\finetuning_prompts\planning_agent_user_prompt_judge.md"
        #system_prompt_judge = self.read_in_prompt(judge_system_prompt_path)
        #user_prompt_base_judge = self.read_in_prompt(judge_user_prompt)    
        
        #entity_analysis = self.get_general_plan_for_task_with_env(instance, task)
        if task is None:
            generate_tasks = True
        else:
            generate_tasks = False
        for i in range(number_of_tasks):
            logs = []
            planning_output = ""
            current_step = 0
            traces = []
            success = False
            if generate_tasks:
                task = self.get_unsupervised_objective(instance)
            while "#objective completed" not in planning_output.lower() and current_step < episode_length:
                log_str = "\n\n".join(logs) if logs else "The agent has not yet interacted with the world"
                starting_inventory = instance.inspect_inventory()
                inventory_dict = self.get_inventory_dict(starting_inventory)
                mining_setup = get_mining_setup(instance)
                #outputs, message_traces = self.get_next_step(system_prompt, user_prompt_base, 
                #                                       task, starting_inventory, 
                #                                       mining_setup, plan, log_str,
                #                                       number_of_steps = 1)
                #full_output = outputs[0]
                #messages = message_traces[0]
                planner_output = self.get_next_step_judge(system_prompt, user_prompt_base, 
                                                       task, starting_inventory, 
                                                       mining_setup, plan, log_str)
                current_step += 1
                if planner_output["completion"]:
                    traces.append({"step_idx": current_step, "executor_output": {"success": True, "traces": []}, "step": planner_output["step"],
                                   "inventory_dict": inventory_dict, "mining_setup": mining_setup, "messages": planner_output["messages"],
                                   "meta": planner_output["meta"], "planning_output": planner_output["full_output"]})
                    success = True
                    break
                planning_output = planner_output["step"]
                pre_executor_mining_setup = instance.get_entities()
                output = self.run_supervised_episode(instance, executor_tries, planning_output, 
                                                     include_plan=True)
                post_executor_mining_setup = instance.get_entities()
                new_entities, removed_entities = self.get_changed_entities(pre_executor_mining_setup, post_executor_mining_setup)
                trace_logs = output["traces"][-1]["logs"]
                #trace_logs = []
                #for trace in output["traces"]:
                #    trace_logs+= trace["logs"]
                log_str = f"Step {current_step}: {planning_output}\nLogs from output\n{trace_logs}"
                if new_entities:
                    #new_entity_str_list = [f"{entity.name} at position {entity.position}" for entity in new_entities if entity.name != "transport-belt"]
                    new_entity_str_list = [f"{entity}" for entity in new_entities if entity.name != "transport-belt"]
                    new_entity_str_list = "\n".join(new_entity_str_list)
                    log_str += f"\nThe following entities have been added by the agent\n{new_entity_str_list}"
                if removed_entities:
                    #removed_entity_str_list = [f"{entity.name} at {entity.position}" for entity in removed_entities if entity.name != "transport-belt"]
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
                                                episode_type = "external_planning", task = None):
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
                    self.run_external_planning_episode(instance = instance, number_of_tasks= episode_length, task = task)
                else:
                    self.run_unsupervised_episode(instance, episode_length, include_plan)

def get_all_folders_in_path(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def sample_random_folders(folders, num_samples):
    return random.sample(folders, num_samples)


if __name__ == "__main__":
    unsupervised_model_path = r"ft:gpt-4o-2024-08-06:paperplane-ai:fact-self-gen-planning:AQzcPI91"
    supervised_model_path = r"ft:gpt-4o-2024-08-06:paperplane-ai:fact-instruct-1:ATSVGf4d:ckpt-step-214"
    #supervised_model_path = r"ft:gpt-4o-2024-08-06:paperplane-ai:fact-instruct-1:ATSVH9dT"
    evaluator = ModelEvaluator(executor_model = supervised_model_path, 
                               objective_model = unsupervised_model_path,
                               #r"prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_self_gen.md",
                               system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_supervised.md",
                               #system_prompt_path = r"prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_supervised_step.md",
                               save_path = r"datasetgen\finetuned_model_gen", # Where to save the traces
                               starting_scenarios_folder=r"skills\data_scenarios\starting_scenarios" # Where the starting scenarios are stored
                               )
    unsupervised_trace = True
    #evaluator.run_external_planning_episode(number_of_tasks = 2)
    #task = "Create a iron plate mine with burner drill feeding a furnace"
    #task = "Create a burner iron ore mine into a chest placed 10 spaces away"
    task = "Get 5 offshore pumps"
    task = "Create a electric iron ore mine into a chest placed 10 spaces away"
    task = "Create a electric generating setup"
    #task = None
    if unsupervised_trace:
        starting_scenarios = ["put_down_electricity_generator"]
        #starting_scenarios = get_all_folders_in_path(r"skills\data_scenarios\starting_scenarios")
        #starting_scenarios = ["multiple_entiti_environment"]
        evaluator.run_simulations_from_starting_scenarios(starting_scenarios, 2, 2, include_plan=True, task = task,
                                                          #episode_type="unsup"
                                                          )
    else:
       objective = "You need to manually mine 50 iron ore, 50 copper ore and 70 coal"
       evaluator.run_supervised_episode(5, task, include_plan=True)
