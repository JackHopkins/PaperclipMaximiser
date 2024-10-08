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
import numpy as np
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
        max_tokens = kwargs.get('max_tokens', 2048)
        tempreature = kwargs.get('tempreature', 0.3)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        try:
            response = self.llm_factory.call(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=tempreature,
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

    def generate_plan(self, objective, inventory: Dict[str, int]) -> str:
        specific_prompt_path = f"{self.prompt_path}/planning"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        user_message = user_message.format(objective=objective, inventory=str(inventory))
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


    def generate_policy_function(self, objective: str, steps: str, inventory: Dict[str, int]) -> str:
        specific_prompt_path = f"{self.prompt_path}/steps_to_script"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        user_message = user_message.format(steps=steps, objective=objective, inventory=str(inventory))
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

    def correct_policy_snippet(self, objective: str, steps, last_executed_policy: str,
                                error_message: str, correction_history: List[Dict[str, str]],
                                inventory: Dict[str, int]) -> str:
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
            error_history=history_str,
            inventory=str(inventory))
        return self._call_api(system_prompt, user_message)


    def stream_curriculum(self, objectives: List[str], inventory: Dict[str, int]):
         for objective in objectives:
            steps = self.generate_plan(objective, inventory)
            policy = self.generate_policy_function(objective, steps, inventory)
            yield {
                "snippet_name": objective,
                "snippet": policy,
                "steps": steps,
                #"test": test,
            }

if __name__ == "__main__":
    #main()


    sampler = FactorioLLMSampler()

    inventory = {
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

    inventory = {
        'iron-plate': 20,
        'coal': 20,
        'copper-plate': 20,
        'stone-furnace': 3,
    }
    #inventory = {}
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)


    test_string = """
from factorio_instance import *

# Check initial inventory
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 10, f"Not enough iron plates in inventory. Expected at least 10, but found {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, but found {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected at least 3, but found {initial_inventory[Prototype.StoneFurnace]}"

# 1. Place a stone furnace
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))
assert stone_furnace is not None, "Failed to place stone furnace"

# 2. Smelt steel plates using resources from inventory
insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.IronPlate, stone_furnace, 10)

# 3. Wait for the smelting process
sleep(10)
# Extract steel plates
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.SteelPlate, stone_furnace.position, 10)
    steel_plates_extracted = inspect_inventory()[Prototype.SteelPlate]
    if steel_plates_extracted >= 2:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# 4. Confirm the steel plates in inventory
steel_plates = inspect_inventory()[Prototype.SteelPlate]
assert steel_plates >= 2, f"Failed to craft 2 steel plates. Only found {steel_plates} in inventory"

print(f"Successfully crafted {steel_plates} steel plates")


"""

    score, goal, result = instance.eval_with_error(test_string, timeout=60)
    # Load objectives from file
    objectives_file = "skills\objectives.txt"
    if os.path.exists(objectives_file):
        objectives = sampler.load_objectives(objectives_file)
    else:
        print(f"Objectives file '{objectives_file}' not found. Please create it and add objectives.")
        exit(1)

    for obj_idx, objective in enumerate(objectives):
            inventory = {
                        'iron-plate': np.random.randint(5, 30),
                        'coal': np.random.randint(5, 30),
                        'copper-plate': np.random.randint(5, 30),
                        'stone-furnace': np.random.randint(1, 10),
                    }
            
            instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)
            
            curriculum_item = next(sampler.stream_curriculum([objective], inventory))
            snippet_name = curriculum_item['snippet_name']
            if "EXPLANATION:" in snippet_name:
                # get everything before the explanation
                snippet_name = snippet_name.split("EXPLANATION:")[0].strip().replace("NAME:", "")
            existing_state = sampler.load_existing_state(snippet_name)

            if existing_state:
                print(f"Resuming work on existing objective: {existing_state['objective']}")
                curriculum_item = existing_state
                correction_history = existing_state.get("corrections", [])
                with open(f"../skills/_{snippet_name}/snippet.py", "r") as f:
                    curriculum_item['snippet'] = f.read()
            else:
                correction_history = []

            print(f"Objective: {curriculum_item['snippet_name']}")
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
                    score, goal, result = instance.eval_with_error(snippet, timeout=240)

                    if 'error' in result.lower() or 'assertion' in result.lower():
                        raise Exception(result)

                    snippet_passed = True
                    break
                except Exception as e:
                    print(e)
                    if attempt < max_attempts - 1:
                        print(f"Snippet failed on attempt {attempt + 1}. `{str(result)}` Attempting to correct...")
                        corrected_snippet = sampler.correct_policy_snippet(
                            curriculum_item['snippet_name'],
                            curriculum_item["steps"],
                            snippet,
                            str(result),
                            correction_history,
                            inventory
                        )
                        corrected_snippet = corrected_snippet.split("```")[1].lstrip('python\n')
                        snippet = textwrap.dedent(corrected_snippet)
                        correction_history.append({"snippet": snippet, "error": str(e)})
                    else:
                        print(f"Snippet failed after {max_attempts} attempts. Moving to next objective.")

            # Save results and update files
            folder_name = snippet_name if snippet_passed else f"_{snippet_name}"
            folder_path = f"skills/{folder_name.strip()}"
            os.makedirs(folder_path, exist_ok=True)

            with open(f"{folder_path}/snippet.py", "w") as f:
                f.write(snippet)

            details = {
                "instruction": objective,
                "objective": curriculum_item['snippet_name'],
                "steps": curriculum_item['steps'],
                "corrections": correction_history,
                "token_count": sampler.token_count,
                "cost": sampler.cost,
                "snippet_passed": snippet_passed,
                "inventory": inventory
            }
            with open(f"{folder_path}/details.json", "w") as f:
                json.dump(details, f, indent=2)

            if snippet_passed:
                print(f"Successfully wrote snippet file for objective: {curriculum_item['snippet_name']}")
                # Remove the completed objective from objectives.txt
                #sampler.remove_objective(objectives_file, objective)
            else:
                print(f"Failed to generate a working snippet for objective: {curriculum_item['snippet_name']}")

            sampler.token_count = 0
            sampler.cost = 0

    print("All objectives have been completed. The program will now exit.")
