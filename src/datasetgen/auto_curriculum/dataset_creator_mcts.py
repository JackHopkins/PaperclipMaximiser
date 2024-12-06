import re
import os
import ast
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from factorio_instance import FactorioInstance
import random
from skills.skill_postprocessor import SkillPostProcessor
from skills.bottoms_up_sampler import eval_program_with_result_trace, get_mining_setup
load_dotenv()
from datasetgen.mcts.conversation_formatter import StructurePreservingFormatter
from datasetgen.mcts.db_client import DBClient
import copy
from datasetgen.mcts.conversation import Message, Conversation
def is_valid_python(code_string: str) -> bool:
    try:
        ast.parse(code_string)
        return True
    except SyntaxError:
        return False

class SFTDatasetCreatorMCTS:
    def __init__(self):
        self.skills_db = DBClient(
        max_conversation_length=10,
        host=os.getenv("SKILLS_DB_HOST"),
        port=os.getenv("SKILLS_DB_PORT"),
        dbname=os.getenv("SKILLS_DB_NAME"),
        user=os.getenv("SKILLS_DB_USER"),
        password=os.getenv("SKILLS_DB_PASSWORD")
    )
        self.postprocessor = SkillPostProcessor()
        self.formatter = StructurePreservingFormatter()


    def programs_to_jsonl(self, programs: List[Dict], output_file: str) -> None:
        # check if the output file exists
        # if it does, we append to it
        with open(output_file, "w") as f:
                for program in programs:
                    f.write(json.dumps(program) + "\n")

    def get_programs_for_sft(self) -> List[Dict]:
        programs = self.skills_db.get_programs(limit = 1000, version = 8)
        return programs
    

    def check_for_eligibility(self, program):
        if self.check_for_errors(program):
            return False
        if program["reward"] > 0 or program["holdout_value"] > 0:
            return True
        return False
    
    def postprocess_mcts_programs(self, programs) -> None:
        program_dict = {}
        # postprocess the programs
        output_dict = {}
        programs_to_process = []
        for program in programs:
            meta = program["meta"]
            if meta and "candidate_steps" in meta:
                continue
            id = program["id"]
            program_dict[id] = program
            eligibility = self.check_for_eligibility(program)
            if eligibility:
                programs_to_process.append(id)
        unique_programs = []
        processed_programs = []
        while programs_to_process:
            id = programs_to_process.pop()
            if id in processed_programs:
                continue
            program = program_dict[id]
            parent_id = program["parent_id"]
            program_list = [program]
            if id not in unique_programs:
                unique_programs.append(id)
            processed_programs.append(id)
            while parent_id is not None:
                    new_program = program_dict[parent_id]
                    new_id = new_program["id"]
                    if new_id in output_dict:
                        program_list = output_dict[new_id] + program_list
                        output_dict.pop(new_id)
                        break
                    if new_id not in unique_programs:
                        unique_programs.append(new_id) 
                    parent_id = new_program["parent_id"]
                    program_list.insert(0, program_dict[new_id])
                    errors = self.check_for_errors(new_program)
                    if not errors and new_id not in output_dict.keys():
                        programs_to_process.append(new_id)
                    processed_programs.append(new_id)
            output_dict[id] = program_list
        print(f"Number of unique programs: {len(unique_programs)}")
        return {"eligible_programs": output_dict, "all_programs": program_dict, "unique_programs": unique_programs}    
    
    def check_for_errors(self, program):
        if "Error" in program["response"]:
            return True
        return False
    def convert_message_to_json(self, message: Message) -> Dict:
        if isinstance(message, dict):
            if "metadata" not in message or not message["metadata"]:
                message["metadata"] = {"error": False}
            return message
        return {"role": message.role, "content": message.content, "metadata": message.metadata if message.metadata else {"error": False}}
    def get_training_set(self, programs: dict):
        programs = programs["eligible_programs"]
        final_dataset = []
        for program in programs.values():

            input_messages = {"system": "", "conversation": []}
            if len(program) == 1:
                step = program[0]
                step_messages = step["conversation"]["messages"]
                input_messages["system"] = step_messages[0]
                input_messages["conversation"].append(step_messages[1])
                output = Message(role="assistant", content=step["code"], metadata = {"error": False})
            else:
                # get the input messages
                for step in program[:-1]:
                    step_messages = step["conversation"]["messages"]
                    if len(input_messages["conversation"]) == 0:
                        input_messages["system"] = step_messages[0]
                        input_messages["conversation"].append(step_messages[1])
                    error = self.check_for_errors(step)
                    assistant_message = Message(role="assistant", content=step["code"], metadata = {"error": error})
                    input_messages["conversation"].append(assistant_message)
                    user_message = Message(role="user", content=step["response"])
                    input_messages["conversation"].append(user_message)
                output = Message(role="assistant", content=program[-1]["code"], metadata = {"error": False})
            if len(input_messages["conversation"]) == 0:
                continue
            #formatted_messages = self.formatter.format_conversation(Conversation(messages=input_messages["conversation"]))
            input_messages["conversation"] = [self.convert_message_to_json(message) for message in input_messages["conversation"]]
            input_messages["system"] = self.convert_message_to_json(input_messages["system"])
            output = self.convert_message_to_json(output)
            final_dataset.append({"messages": [input_messages["system"]] + input_messages["conversation"] + [output]})
        
        return final_dataset
    

    def get_mcts_programs(self, output_jsonl_path, versions = [20]):
        message_datapoints = []
        for version in versions:
            print(f"Starting version {version}")
            programs = self.skills_db.get_programs(version = version)
            postprocessed_programs = self.postprocess_mcts_programs(programs)
            training_set = self.get_training_set(postprocessed_programs)
            message_datapoints.extend(training_set)
        # create the file if not exists
        with open(output_jsonl_path, "w") as f:
            for message_datapoint in message_datapoints:
                f.write(json.dumps(message_datapoint) + "\n")
        

    def get_objective_groups(self, programs: List[Dict]) -> List[str]:
        obj_groups = {}
        for program in programs:
            meta = program["meta"]
            objective = meta["objective"]
            if objective not in obj_groups:
                obj_groups[objective] = []
            obj_groups[objective].append(program)
        return obj_groups
    
    def create_jsonl_dataset_from_db_programs(self, output_file: str) -> None:
            # System prompt just insance system prompt!!!!
            all_programs = self.get_programs_for_sft()
            #obj_groups = self.get_objective_groups(all_programs)
            self.programs_to_jsonl(all_programs, output_file)



    
    def create_training_eval_dataset(self, full_dataset_path, training_dataset_path, eval_dataset_path, training_ratio=1):
        with open(full_dataset_path) as f:
            all_skills = [json.loads(line) for line in f.readlines()]
        random.shuffle(all_skills)
        training_skills = all_skills[:int(len(all_skills) * training_ratio)]
        eval_skills = all_skills[int(len(all_skills) * training_ratio):]
        training_skills = [{"messages": skill["trace"]} for skill in training_skills]
        eval_skills = [{"messages": skill["trace"]} for skill in eval_skills]
        with open(training_dataset_path, "w") as f:
            for skill in training_skills:
                f.write(json.dumps(skill) + "\n")
        with open(eval_dataset_path, "w") as f:
            for skill in eval_skills:
                f.write(json.dumps(skill) + "\n")

if __name__ == "__main__":
    dataloader = SFTDatasetCreatorMCTS()
    
    raw_db_jsonl_file = r"src\datasets\mcts\sft_dataset_raw_2.jsonl"
    versions = [i for i in range(20, 40)]
    dataloader.get_mcts_programs(raw_db_jsonl_file, versions=versions)