import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")

import ast
import json
import os
import textwrap
from itertools import cycle
from typing import List, Dict, Any
from dotenv import load_dotenv

from factorio_instance import FactorioInstance
from llm_factory import LLMFactory
from utilities.controller_loader import load_schema, load_definitions

load_dotenv()

def is_valid_python(code_string: str) -> bool:
    try:
        ast.parse(code_string)
        return True
    except SyntaxError:
        return False

class FactorioLLMSampler:
    def __init__(self, prompt_path: str = "prompts", model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.llm_factory = LLMFactory(model)
        self.api_schema, self.entities = self._get_base_api_schema_prompt()
        self.objective_context = []
        self.token_count = 0
        self.cost = 0
        self.prompt_path = prompt_path

    def _get_base_api_schema_prompt(self):
        execution_path = os.path.dirname(os.path.realpath(__file__))
        folder_path = f'{execution_path}/../controllers'
        schema = load_schema(folder_path)
        type_definitions = load_definitions(f'{execution_path}/../factorio_types.py')
        entity_definitions = load_definitions(f'{execution_path}/../factorio_entities.py')
        brief = f"""
You have access to the following Game API for use in your Python code:

Entities:
{entity_definitions}

            Methods:
            ```
            {schema}
            """
        return brief, entity_definitions

    def _call_api(self, system_prompt: str, user_message: str, **kwargs) -> str:
        max_tokens = kwargs.get('max_tokens', 1200)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        try:
            response = self.llm_factory.call(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs
            )

            try:
                self.token_count += response.usage.input_tokens + response.usage.output_tokens
                self.cost += response.usage.input_tokens * 0.0000003 + response.usage.output_tokens * 0.0000015
            except:
                self.token_count += response.usage.total_tokens
                self.cost += response.usage.prompt_tokens * 0.0000003 + response.usage.completion_tokens * 0.0000015

            if hasattr(response, 'choices'):
                return response.choices[0].message.content
            elif hasattr(response, 'content'):
                return response.content[0].text
            else:
                raise ValueError("Unexpected response structure")
        except Exception as e:
            print(f"API call failed: {e}")
            raise

    def load_existing_state(self, snippet_name: str) -> Dict[str, Any]:
        folder_path = f"../skills/_{snippet_name}"
        if os.path.exists(folder_path):
            with open(f"{folder_path}/details.json", "r") as f:
                details = json.load(f)
            self.token_count = details.get("token_count", 0)
            self.cost = details.get("cost", 0)
            return details
        return None

    def load_objectives(self, file_path: str) -> List[str]:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def remove_objective(self, file_path: str, objective: str):
        with open(file_path, 'r') as f:
            objectives = f.readlines()
        with open(file_path, 'w') as f:
            for obj in objectives:
                if obj.strip() != objective:
                    f.write(obj)

    def generate_objective(self) -> str:
        system_prompt = "You are an AI assistant creating beginner objectives for a Factorio game curriculum. Generate a single, clear objective for the next task in the game."
        curriculum_examples = '\n'.join([
            "Mine 100 iron ore into your inventory",
            "Gather resources and smelt 10 iron plates in a stone furnace",
            "Chop down trees and make a wooden chest to store items",
        ])
        context = "\n".join(self.objective_context)
        interstitial = ", set objectives that do one thing at a time"
        if context:
            interstitial += f", considering the following context of previous objectives:\n\n{context}\n"
        user_message = f"Generate a new objective for the Factorio curriculum{interstitial}\nEnsure the new objective is different from these. Example objectives:\n{curriculum_examples}"
        new_objective = self._call_api(system_prompt, user_message)
        self.objective_context.append(new_objective)
        if len(self.objective_context) > 5:
            self.objective_context.pop(0)
        return new_objective

    def generate_plan(self, objective):
        specific_prompt_path = f"{self.prompt_path}/planning"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        user_message = user_message.format(objective=objective)
        return self._call_api(system_prompt, user_message)

    def generate_verification_function(self, objective: str) -> str:
        specific_prompt_path = f"{self.prompt_path}/outcome_test"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        user_message = user_message.format(objective=objective)
        response = self._call_api(system_prompt, user_message)
        try:
            program = response.replace('```python', '```')
            program = program.split('```')[1]

            return program
        except:
            return response


    def generate_policy_function(self, objective: str, steps: str) -> str:
        specific_prompt_path = f"{self.prompt_path}/steps_to_script"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        user_message = user_message.format(steps=steps, objective=objective)
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        response = self._call_api(system_prompt, user_message)
        try:
            program = response.replace('```python', '```')
            program = program.split('```')[1]
            return program
        except:
            return response

    def generate_snippet_name(self, objective: str) -> str:
        system_prompt = f"You are an AI assistant creating Python snippet names for Factorio game objectives."
        user_message = (f"Provide a name for a snippet to achieve the objective: '{objective}'. "
                        f"Only write between ``` blocks. "
                        f"e.g '```place_furnace_next_to_coal```'")
        response = self._call_api(system_prompt, user_message, temperature=0)
        parsed = response.split('```')[1].replace(' ', '_').lower().strip()
        return parsed

    def correct_policy_function(self, objective: str, steps, last_executed_policy: str,
                                error_message: str, correction_history: List[Dict[str, str]]) -> str:
        specific_prompt_path = f"{self.prompt_path}/self_correct_script_process"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)


        history_str = "\n\n".join([
            f"Attempt {i + 1}:\nSnippet:\n```python\n{attempt['snippet']}\n```\nError: {attempt['error']}"
            for i, attempt in enumerate(correction_history)
        ]) if correction_history else "No history of attempts yet."

        user_message = user_message.format(
            objective=objective,
            steps=steps,
            last_executed_policy=last_executed_policy,
            error_message=error_message,
            error_history=history_str)
        return self._call_api(system_prompt, user_message)

    def correct_test(self, objective: str, correction_history: List[Dict[str, str]]) -> str:
        system_prompt = (
            f"You are an AI assistant correcting Python verification tests for Factorio game objectives. "
            f"Only write in python in ``` blocks"
            f"If the test fails, the function should raise an uncaught exception. "
            f"The game API is available for use by passing in the `game` parameter, which exposes: \n\n{self.api_schema}"
        )

        history_str = "\n\n".join([
            f"Attempt {i + 1}:\nPolicy:\n```python\n{attempt['policy']}\n```\nError: {attempt['error']}"
            for i, attempt in enumerate(correction_history)
        ])

        user_message = (
            f"The following integration test for the Factorio objective '{objective}' has failed multiple times. "
            f"Here's the history of attempts and errors:\n\n{history_str}\n\n"
            f"Please correct the verification code to fix these errors and successfully test the policy function. "
            f"Consider all previous attempts and their errors when making your correction."
            "Do not define any functions, only correct the inline code."
        )
        return self._call_api(system_prompt, user_message)

    def stream_curriculum(self, num_objectives: int = 5):
        for _ in range(num_objectives):
            #objective = self.generate_objective()
            objective = "Craft one burner mining drill"
            #steps = self.generate_plan(objective)
            #policy = self.generate_policy_function(objective, steps)
            #test = self.generate_verification_function(objective)
            steps = "SUMMARY:\nTo craft one burner mining drill, we need to create several components and gather resources. The main components required are:\n- 3 iron gear wheels\n- 3 iron plates\n- 1 stone furnace\n\nWe'll need to mine iron ore and stone, smelt iron ore into iron plates, craft iron gear wheels, and craft a stone furnace. Here's a breakdown of the resources and crafting steps:\n\nResources needed:\n- 9 iron ore (3 for direct use, 6 for iron gear wheels)\n- 5 stone (for stone furnace)\n- Coal (for smelting)\n\nCrafting steps:\n1. Craft stone furnace (requires 5 stone)\n2. Smelt 9 iron ore into 9 iron plates\n3. Craft 3 iron gear wheels (each requires 2 iron plates)\n4. Craft 1 burner mining drill\n\nSTEPS:\n1. Mine 5 stone\n2. Craft a stone furnace using the 5 stone\n3. Mine coal for fuel\n4. Mine 9 iron ore\n5. Place the stone furnace\n6. Smelt 9 iron ore into 9 iron plates using the stone furnace and coal\n7. Craft 3 iron gear wheels (each requires 2 iron plates, using 6 iron plates total)\n8. Craft another stone furnace using 5 more stone (mine if necessary)\n9. Craft the burner mining drill using:\n   - 3 iron gear wheels\n   - 3 iron plates\n   - 1 stone furnace\n\nHere's a detailed step-by-step plan using the game's API:\n\n1. Mine stone:\n   ```python\n   move_to(nearest(Resource.Stone))\n   harvest_resource(nearest(Resource.Stone), 5)\n   ```\n\n2. Craft stone furnace:\n   ```python\n   craft_item(Prototype.StoneFurnace, 1)\n   ```\n\n3. Mine coal:\n   ```python\n   move_to(nearest(Resource.Coal))\n   harvest_resource(nearest(Resource.Coal), 10)\n   ```\n\n4. Mine iron ore:\n   ```python\n   move_to(nearest(Resource.IronOre))\n   harvest_resource(nearest(Resource.IronOre), 9)\n   ```\n\n5. Place stone furnace:\n   ```python\n   furnace_pos = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))\n   ```\n\n6. Smelt iron ore into iron plates:\n   ```python\n   insert_item(Prototype.Coal, get_entity(Prototype.StoneFurnace, furnace_pos), 5)\n   insert_item(Prototype.IronOre, get_entity(Prototype.StoneFurnace, furnace_pos), 9)\n   sleep(10)  # Wait for smelting to complete\n   extract_item(Prototype.IronPlate, furnace_pos, 9)\n   ```\n\n7. Craft iron gear wheels:\n   ```python\n   craft_item(Prototype.IronGearWheel, 3)\n   ```\n\n8. Mine more stone and craft another stone furnace:\n   ```python\n   move_to(nearest(Resource.Stone))\n   harvest_resource(nearest(Resource.Stone), 5)\n   craft_item(Prototype.StoneFurnace, 1)\n   ```\n\n9. Craft burner mining drill:\n   ```python\n   craft_item(Prototype.BurnerMiningDrill, 1)\n   ```\n\nThis plan ensures that we have all the necessary components to craft one burner mining drill, including the additional stone furnace required for the recipe."
            policy = '\nfrom factorio_instance import *\n\n# 1. Mine 5 stone\nstone_pos = nearest(Resource.Stone)\nmove_to(stone_pos)\nharvest_resource(stone_pos, 5)\nstone_count = inspect_inventory()[Resource.Stone]\nassert stone_count >= 5, f"Not enough stone mined. Expected at least 5, but got {stone_count}"\n\n# 2. Craft a stone furnace\ncraft_item(Prototype.StoneFurnace, 1)\nfurnace_count = inspect_inventory()[Prototype.StoneFurnace]\nassert furnace_count >= 1, f"Stone furnace not crafted. Expected at least 1, but got {furnace_count}"\n\n# 3. Mine coal for fuel\ncoal_pos = nearest(Resource.Coal)\nmove_to(coal_pos)\nharvest_resource(coal_pos, 9)\ncoal_count = inspect_inventory()[Resource.Coal]\nassert coal_count >= 9, f"Not enough coal mined. Expected at least 9, but got {coal_count}"\n\n# 4. Mine 9 iron ore\niron_ore_pos = nearest(Resource.IronOre)\nmove_to(iron_ore_pos)\nharvest_resource(iron_ore_pos, 9)\niron_ore_count = inspect_inventory()[Resource.IronOre]\nassert iron_ore_count >= 9, f"Not enough iron ore mined. Expected at least 9, but got {iron_ore_count}"\n\n# 5. Place the stone furnace\nfurnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))\n\n# 6. Smelt 9 iron ore into 9 iron plates\ninsert_item(Prototype.Coal, furnace, 5)\ninsert_item(Prototype.IronOre, furnace, 9)\nsleep(20)  # Wait for smelting to complete\nextract_item(Prototype.IronPlate, furnace.position, 9)\n\n# Check if we have 9 iron plates\niron_plate_count = inspect_inventory()[Prototype.IronPlate]\nif iron_plate_count < 9:\n    sleep(10)  # Wait a bit longer if smelting is not complete\n    extract_item(Prototype.IronPlate, furnace.position, 9 - iron_plate_count)\n    iron_plate_count = inspect_inventory()[Prototype.IronPlate]\n\nassert iron_plate_count >= 9, f"Not enough iron plates smelted. Expected at least 9, but got {iron_plate_count}"\n\n# 7. Craft 3 iron gear wheels\ncraft_item(Prototype.IronGearWheel, 3)\ngear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]\nassert gear_wheel_count >= 3, f"Not enough iron gear wheels crafted. Expected at least 3, but got {gear_wheel_count}"\n\n# 8. Mine more stone and craft another stone furnace\nmove_to(nearest(Resource.Stone))\nharvest_resource(nearest(Resource.Stone), 5)\ncraft_item(Prototype.StoneFurnace, 1)\nfurnace_count = inspect_inventory()[Prototype.StoneFurnace]\nassert furnace_count >= 1, f"Second stone furnace not crafted. Expected at least 1, but got {furnace_count}"\n\n# 9. Craft the burner mining drill\ncraft_item(Prototype.BurnerMiningDrill, 1)\nburner_drill_count = inspect_inventory()[Prototype.BurnerMiningDrill]\nassert burner_drill_count >= 1, f"Burner mining drill not crafted. Expected at least 1, but got {burner_drill_count}"\n\nprint("Successfully crafted one burner mining drill!")\n'
            test = '\n# Get the current inventory\ninventory = inspect_inventory()\n\n# Check if there\'s at least one burner mining drill in the inventory\nnumber_of_burner_mining_drills = inventory.get(Prototype.BurnerMiningDrill, 0)\n\n# Assert that we have at least one burner mining drill\nassert number_of_burner_mining_drills >= 1, f"Failed to craft a burner mining drill. Current count in inventory: {number_of_burner_mining_drills}"\n\n# If we want to be more specific and check for exactly one burner mining drill:\nassert number_of_burner_mining_drills == 1, f"Expected exactly 1 burner mining drill, but found {number_of_burner_mining_drills} in the inventory"\n\nprint("Success: One burner mining drill has been crafted!")\n'
            yield {
                "objective": objective,
                "snippet": snippet,
                "steps": steps,
            }

if __name__ == "__main__":
    #main()


    sampler = FactorioLLMSampler()

    inventory = {
        'iron-plate': 50,
        'coal': 50,
        'copper-plate': 50,
        'iron-chest': 2,
        'burner-mining-drill': 3,
        'electric-mining-drill': 1,
        'assembling-machine-1': 1,
        'stone-furnace': 9,
        'transport-belt': 50,
        'boiler': 1,
        'burner-inserter': 32,
        'pipe': 15,
        'steam-engine': 1,
        'small-electric-pole': 10
    }
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)
    #test_string = '\nfrom factorio_instance import *\n\ndef craft_transport_belts(self, num_belts: int = 2) -> bool:\n    # Step 1: Gather resources\n    self.harvest_resource(nearest(Resource.IronOre))\nself.craft_transport_belts(2)'
    #test_string = '\nfrom factorio_instance import *\n\n# Find the nearest iron patch\niron_patch = get_resource_patch(Resource.IronOre, nearest(Resource.IronOre))\n# Move to the center of the iron patch\nmove_to(iron_patch.bounding_box.left_top)\n# Step 3: Gather resources\nharvest_resource(nearest(Resource.IronOre))'
    test_string = """
from factorio_instance import *
# 1) mine 5 stone
# Find nearest stone resource
nearest_stone = nearest(Resource.Stone)
# Move to the stone resource
move_to(nearest_stone)
# Harvest stone
harvest_resource(nearest_stone, quantity=5) 
# test that the stone was harvested
assert inspect_inventory()[Resource.Stone] == 5

#2) Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)
# test that the stone furnace was crafted
assert inspect_inventory()[Prototype.StoneFurnace] == 1

#3) Mine coal for stone furnace
nearest_coal = nearest(Resource.Coal)
move_to(nearest_coal)
harvest_resource(nearest_coal, quantity=5)
# test that the coal was harvested
assert inspect_inventory()[Resource.Coal] == 5


#4) Move to copper ore
nearest_copper = nearest(Resource.IronOre)
move_to(nearest_copper)
#5) Place down stone furnace
stone_furnace = place_entity_next_to(Prototype.StoneFurnace,
                                                reference_position=nearest_copper,
                                                direction=UP,
                                                spacing=1)
#6) Mine copper ore
harvest_resource(nearest_copper, quantity=5)
# test that the copper ore was harvested
assert inspect_inventory()[Resource.CopperOre] == 5

#7) Place coal and copper ore to stone furnace
insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.CopperOre, stone_furnace, 5)
#8) Smelt copper ore for copper plates
# wait for smelting
sleep(10)
extract_item(Prototype.CopperPlate, stone_furnace, 5)
# test that the copper plates were smelted
# smelting make take longer, thus we need to check the inventory after a while
number_of_copper_plates = inspect_inventory()[Prototype.CopperPlate]
# if the copper plates are not there, wait for a while
if number_of_copper_plates < 5:
    sleep(10)
    # extract the copper plates again
    extract_item(Prototype.CopperPlate, stone_furnace, 5)
    number_of_copper_plates = inspect_inventory()[Prototype.CopperPlate]

inventory = inspect_inventory()
number_of_copper_plates = inventory.get(Prototype.CopperPlate, 0)
assert number_of_copper_plates == 6, f"Expected 6 copper plates, got {number_of_copper_plates}"
"""

#    test_string = """
#from factorio_instance import *\n\n# 1. Mine stone\nstone_position = nearest(Resource.Stone)\nmove_to(stone_position)\nharvest_resource(stone_position, quantity=5)\n\n# 2. Craft a stone furnace\ncraft_item(Prototype.StoneFurnace, quantity=1)\n\n# 3. Mine iron ore\niron_ore_position = nearest(Resource.IronOre)\nmove_to(iron_ore_position)\nharvest_resource(iron_ore_position, quantity=9)\n\n# 4. Mine coal\ncoal_position = nearest(Resource.Coal)\nmove_to(coal_position)\nharvest_resource(coal_position, quantity=10)\n\n# 5. Smelt iron plates\nfurnace = place_entity_next_to(Prototype.StoneFurnace, iron_ore_position, Direction.UP, spacing=1)\ninsert_item(Prototype.Coal, furnace, quantity=5)\ninsert_item(Prototype.IronOre, furnace, quantity=9)\n\n# Wait for smelting to complete\nsleep(15)\n\n# Extract iron plates\nextract_item(Prototype.IronPlate, furnace.position, quantity=9)\n\n# 6. Craft iron gear wheels\ncraft_item(Prototype.IronGearWheel, quantity=3)\n\n# 7. Craft the burner mining drill\ncraft_item(Prototype.BurnerMiningDrill, quantity=1)\n\n# 8. Confirm the burner mining drill is in the inventory\ninventory = inspect_inventory()\nif Prototype.BurnerMiningDrill in inventory and inventory[Prototype.BurnerMiningDrill] >= 1:\n    print("Successfully crafted one burner mining drill!")\nelse:\n    raise Exception("Failed to craft burner mining drill")\n
#"""
    #score, goal, result = instance.eval_with_error(test_string, timeout=60)
    # Load objectives from file
    objectives_file = "objectives.txt"
    if os.path.exists(objectives_file):
        objectives = sampler.load_objectives(objectives_file)
    else:
        print(f"Objectives file '{objectives_file}' not found. Please create it and add objectives.")
        exit(1)

    while objectives:
        for objective in objectives.copy():
            curriculum_item = next(sampler.stream_curriculum([objective]))
            snippet_name = curriculum_item['snippet_name']
            existing_state = sampler.load_existing_state(snippet_name)

            if existing_state:
                print(f"Resuming work on existing objective: {existing_state['objective']}")
                curriculum_item = existing_state
                correction_history = existing_state.get("corrections", [])
                with open(f"../skills/_{snippet_name}/snippet.py", "r") as f:
                    curriculum_item['snippet'] = f.read()
            else:
                correction_history = []

            print(f"Objective: {curriculum_item['objective']}")
            print("Snippet name: " + snippet_name)
            print("Plan:")
            print(curriculum_item["steps"])
            print("Snippet:")
            print(curriculum_item['snippet'])
            print("\n" + "=" * 50 + "\n")

            if not is_valid_python(curriculum_item['snippet']):
                continue

            snippet = curriculum_item['snippet']

            max_attempts = 4
            snippet_passed = False

            for attempt in range(max_attempts):
                instance._reset(**instance.initial_inventory if isinstance(instance.initial_inventory, dict) else instance.initial_inventory.__dict__)

                try:
                    score, goal, result = instance.eval_with_error(snippet, timeout=20)

                    if 'error' in result.lower() or 'assertion' in result.lower():
                        raise Exception(result)

                    snippet_passed = True
                    break
                except Exception as e:
                    correction_history.append({"snippet": snippet, "error": str(e)})
                    if attempt < max_attempts - 1:
                        print(f"Snippet failed on attempt {attempt + 1}. `{str(result)}` Attempting to correct...")
                        corrected_snippet = sampler.correct_policy_snippet(
                            curriculum_item['objective'],
                            snippet,
                            str(result),
                            correction_history
                        )
                        corrected_snippet = corrected_snippet.split("```")[1].lstrip('python\n')
                        snippet = textwrap.dedent(corrected_snippet)
                    else:
                        print(f"Snippet failed after {max_attempts} attempts. Moving to next objective.")

            # Save results and update files
            folder_name = snippet_name if snippet_passed else f"_{snippet_name}"
            folder_path = f"../skills/{folder_name.strip()}"
            os.makedirs(folder_path, exist_ok=True)

            with open(f"{folder_path}/snippet.py", "w") as f:
                f.write(curriculum_item['snippet'])

            details = {
                "instruction": objective,
                "objective": curriculum_item['objective'],
                "steps": curriculum_item['steps'],
                "corrections": correction_history,
                "token_count": sampler.token_count,
                "cost": sampler.cost,
                "snippet_passed": snippet_passed
            }
            with open(f"{folder_path}/details.json", "w") as f:
                json.dump(details, f, indent=2)

            if snippet_passed:
                print(f"Successfully wrote snippet file for objective: {curriculum_item['objective']}")
                # Remove the completed objective from objectives.txt
                sampler.remove_objective(objectives_file, objective)
            else:
                print(f"Failed to generate a working snippet for objective: {curriculum_item['objective']}")

            sampler.token_count = 0
            sampler.cost = 0

        if objectives:
            print("Completed a full cycle. Starting over with remaining objectives.")
        else:
            print("All objectives have been completed. Exiting the program.")

    print("All objectives have been completed. The program will now exit.")
