import os
import json
from factorio_instance import FactorioInstance
from utilities.controller_loader import load_schema, load_definitions
SYSTEM_MESSAGE = """
You are an AI agent creating Python policy scripts to achieve Factorio game objectives. You are given an objective and will carry out steps to achieve that objective. You write programs that interact with the factorio world. Each program you write will be one step to achieve the objective given to you. In the programs you first think what is the next step you need to make in python comments. You then write the python executable script that carries out this single step. You also write assert statements after your steps to ensure the steps were carried out correctly. After every step the user will give you back the final response message and print statements from the factorio game. When you have successfully completed the objective, reply with ###OBJECTIVE COMPLETED. The API for factorio you need to use is the following {api_schema}
"""

def format_system_message():
    execution_path = os.path.dirname(os.path.realpath(__file__))
    entity_definitions = load_definitions(f'{execution_path}/../factorio_entities.py')
    folder_path = f'{execution_path}/../controllers'
    schema = load_schema(folder_path)
    api_schema = brief = f"""
You have access to the following Game API for use in your Python code:

Entities:
{entity_definitions}

Methods:
```
{schema}
"""
    return SYSTEM_MESSAGE.format(api_schema=api_schema).strip()
def create_skills_dataset(skills_folder = "skills"):
    
    default_inventory = {
        'iron-plate': 50,
        'coal': 100,
        'copper-plate': 50,
        'iron-chest': 2,
        'burner-mining-drill': 3,
        'electric-mining-drill': 1,
        'assembling-machine-1': 1,
        'stone-furnace': 9,
        'transport-belt': 500,
        'boiler': 1,
        'burner-inserter': 32,
        'pipe': 15,
        'steam-engine': 1,
        'small-electric-pole': 10,
        "wooden-chest": 1,
    }
    dataset = []
    # get all folders in skills folder
    skill_folders = [f for f in os.listdir(skills_folder) if os.path.isdir(os.path.join(skills_folder, f))]
    # get all snippets from each skill folder
    snippets = []
    for skill in skill_folders:
        skill_path = os.path.join(skills_folder, skill)
        if skill.startswith('_'):
            continue
        # read in the snippet.py files
        snippet_file = os.path.join(skill_path, 'snippet.py')
        with open(snippet_file, 'r') as f:
            snippet = f.read().replace("from factorio_instance import *", "")
        # read in deatils.json
        details_file = os.path.join(skill_path, 'details.json')
        with open(details_file, 'r') as f:
            details = json.load(f)
        if "inventory" not in details:
            details["inventory"] = default_inventory
        snippets.append((snippet, details))
    system_message = format_system_message()
    for snippet in snippets:
        trace = [{"system": system_message}]
        # split all by /n/n
        snippet_parts = snippet[0].split('\n\n')
        details = snippet[1]
        inventory = details["inventory"]
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)
        instance.reset()
        for part in snippet_parts:
            if part == "":
                continue
            part = part.strip()
            trace.append({"assistant": f"'''python\n{part}\n'''"})
            # evaluate the part
            score, goal, result = instance.eval_with_error(part, timeout=60)
            if 'error' in result.lower() or 'assertion' in result.lower():
                raise Exception(result)
            trace.append({"user": result})
        trace.append({"assistant": "###OBJECTIVE COMPLETED"})
        dataset.append(trace)


    return dataset

if __name__ == '__main__':
    dataset = create_skills_dataset()
    print(dataset[0])
