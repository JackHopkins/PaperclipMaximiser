import ast
import json
import re
import time
from datetime import date, datetime
from multiprocessing import freeze_support

import backoff
import regex

from bcolors import bcolors
from factorio_instance import FactorioInstance
from vocabulary import Vocabulary

#wait_duration(5); # Wait for 5 seconds
schema = \
"""
# Observe and describe the natural resources and landscape around you
inspect_resources() -> dict;

# Inspect entities within a 20-meter radius around you
inspect_entities(20) -> list;

# Examine the items currently in your inventory
inspect_inventory() -> dict;

# Move to (10, 5), laying transport belts as you go
move_to((10, 5), laying='transport-belt');

# Craft 1 iron chest
craft_item('iron-chest', quantity=1);

# Place an assembling machine facing up, at (1, 1)
entity_position = place_entity('assembling-machine-1', direction=UP, position=(1, 1));

# Place a burner drill facing down, on to the nearest coal resource
entity_position = place_entity('burner-mining-drill', direction=DOWN, position=nearest('coal'));

# Pick up coal near (-2, 0)
pickup_entity('coal', (-2, 0));

# Insert 1 coal from your inventory into the nearest mining drill for fuel
insert_item('coal', target_position=nearest('burner-mining-drill'), quantity=1);

# Extract 1 coal from the entity at (0, 1)
extract_item('coal', source_position=(0, 1), quantity=1);

# Extract 1 coal from the nearest iron chest in the map
extract_item('coal', source_position=nearest('iron-chest'), quantity=1);

# Set the recipe of the entity at (0, 1) to craft 'iron-chest'
set_entity_recipe((0, 1), recipe='iron-chest');

# Move to (0, -40)
move_to((0, -40));

# Move to the position of the nearest tree
move_to(nearest('tree'));

# Harvest or mine 5 of the resource located at (-2, 0)
harvest_resource((-2, 0), quantity=5);

# Rotate the entity at (0, 0)
rotate_entity((0, 0), direction=LEFT);

# Place a burner-mining-drill to the left of the existing stone furnace leaving a gap of 1 tile
entity_position = place_entity_next_to('burner-mining-drill', reference_position=stone_furnace_position, direction=LEFT, gap=1)

# Connect the burner-mining-drill's output to the stone-furnace's input using an inserter
connect_entities(source_position=(burner_drill_position[0]-2, burner_drill_position[1]), target_position=stone_furnace_position, connection_type='inserter')

"""

"""
nearest().get("burner-mining-drill").rotate(NORTH)
nearest().place("burner-mining-drill").rotate(EAST)
at(0,0).place("burner-mining-drill").rotate(NORTH)
at(0,0).get("burner-mining-drill").
inventory.get("burner-mining-drill").place(0,0).rotate(NORTH)
"""

brief = \
    f"""
You are an expert Factorio player. You have access to the following API.

```
{schema}
``` 
To play, you must only use the methods from this python API with basic logical flow, variable assignment and arithmetic.

Example:
```
# Place a burner-mining-drill
coal_position = nearest('coal')
move_to(coal_position)
place_entity('burner-mining-drill', direction=LEFT, position=(coal_position[0]-2, coal_position[1]))
# Check to ensure that burner-mining-drill has been placed 
inspect_entities(5) 
```
Instructions:
1. Automate resource extraction, processing and manufacturing to increase your score.
2. Start with a simple mining operation, smelting setup and basic power generating using coal-fired boilers and steam engines.
3. On the map, you are called 'player_character'.
4. Regularly inspect your inventory and surroundings to be sure of what's happening in the game.
5. '#' on what you are planning, before issuing your python command.

"""

import openai


class FactorioRunner:

    def __init__(self,
                 api_key,
                 model="gpt-4",
                 buffer_size=10,
                 beam=1,
                 fast=True,
                 trace=False):
        self.beam = beam
        self.buffer = {}
        self.model = model
        self.buffer_size = buffer_size
        openai.api_key = api_key
        self.log_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".log"
        self.trace_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".trace"
        self.max_sequential_exception_count = 3

        inventory = {
            'coal': 50,
            'copper-plate': 50,
            'iron-plate': 50,
            'iron-chest': 1,
            'burner-mining-drill': 1,
            'assembling-machine-1': 1,
            'stone-furnace': 1,
            'transport-belt': 50
        }
        freeze_support()
        vocabulary = Vocabulary()
        self.instance = FactorioInstance(address='localhost',
                                         vocabulary=vocabulary,
                                         bounding_box=200,
                                         tcp_port=27016,
                                         inventory=inventory)
        self.history = []
        self.program_generator = self._get_program_generator
        if not trace:
            pass
            #self._log_to_file("###NEW EPISODE###")
            #self._log_observation(self.instance.observe_nature())
            #self._log_comment("Lets start by checking my inventory.")
            #self._log_observation(self.instance.check_inventory())
        else:
            self.trace = trace

    def replay(self):
        with open(f"log/{self.trace}.trace", "r") as f:
            lines = f.readlines()
            for line in lines:
                print(line)
                if line[0] != "#":
                    try:
                        response = self.instance.eval(line.rstrip("\n;"))
                        print(response)
                    except Exception as e:
                        print(e)

    @backoff.on_exception(backoff.expo,
                          (openai.error.RateLimitError, openai.error.APIError))
    def _get_program_generator(self):
        messages = [{"role": "system", "content": brief}] + self.history[-self.buffer_size:]
        time.sleep(1.5)
        return openai.ChatCompletion.create(
            n=self.beam,
            model=self.model,  # "gpt-3.5-turbo",
            max_tokens=200,
            messages=messages,
            stop=["\n\n", "\n#"],
            stream=True
        )

    def _log_history(self, message, role, error=False):
        if isinstance(message, dict):
            message = json.dumps(message, indent = 4)

        if self.history and self.history[-1]['role'] == role and not error:
            self.history[-1]['content'] += f"\n{message}"
        else:
            self.history.append({
                "role": role, "content": message
            })

    def _log_to_file(self, message):
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def _log_to_trace(self, message):
        with open(self.trace_file, "a") as f:
            f.write(message + "\n")

    def _log_error(self, message):
        self.instance.sequential_exception_count += 1
        output = f"{bcolors.FAIL}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, "user", error=True)
        if self.instance.sequential_exception_count > self.max_sequential_exception_count:
            self.flush_history()
            self._log_to_file(f"{bcolors.FAIL} Too many sequential errors. Flushing memory.")

    def _log_command(self, message):
        output = f"{bcolors.OKBLUE}{message}"
        self._log_to_trace(message)
        self._log_to_file(output)
        print(output)
        self._log_history(message, "assistant")

    def _log_comment(self, message):
        comment = "# " + message.lstrip("# ")
        output = f"{bcolors.OKCYAN}{comment}"
        self._log_to_trace(comment)
        self._log_to_file(output)
        print(output)
        self._log_history(comment, "assistant")

    def _log_observation(self, message):
        output = f"{bcolors.OKGREEN}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, "user")

    def is_valid_python(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _replace_comments(self, code):
        # Regular expression pattern to match a single-line comment
        pattern = r'#(.*)'

        # Callback function to replace the comment with a method call
        def comment_replacer(match):
            comment_text = match.group(1).strip()
            return f'comment("{comment_text}")'

        # Replace comments in the code
        new_code = re.sub(pattern, comment_replacer, code)
        return new_code

    def __next__(self):
        #if self.buffer:
        #    self._log_comment(self.buffer)
        #    self.buffer = {
        #    }

        chunk_generator = self.program_generator()

        # Accumulate the entire content
        for chunk in chunk_generator:
            choice = chunk['choices'][0]
            chunk_message = choice['delta']
            if chunk_message.get('content'):
                content = chunk_message.get('content')
                if choice['index'] not in self.buffer:
                    self.buffer[choice['index']] = ""
                self.buffer[choice['index']] += content
                self.buffer[choice['index']] = self.buffer[choice['index']].lstrip()

        # Check if the entire buffer is syntactically valid Python code
        for index, buffer in self.buffer.items():
            if self.is_valid_python(buffer):
                self._execute_buffer(buffer)
            elif self.is_valid_python("# " + buffer):
                self.buffer = "# "+buffer
                #self._execute_buffer()
            else:
                self._log_command(buffer)
                self._log_error("The provided code is not syntactically valid Python. Only write valid python.")

            self.buffer[index] = ""

    def _execute_buffer(self, buffer):
        # Execute the buffer
        #if all([l.lstrip() and l.lstrip()[0] == "#" for l in self.buffer.split('\n')]):
            # if len(self.buffer.split('\n')) == 1 and self.buffer.lstrip()[0] == "#":
        #    self._log_comment(self.buffer)
        #else:
        buffer = self._replace_comments(buffer)
        try:
            self._log_command(buffer)
            result = self.instance.eval(buffer.strip())
            if result and isinstance(result, str):
                self._log_observation(result)

        except Exception as e:
            try:
                error, reason = e.args
                self._log_error(f"{error}. {str(reason).replace('_', ' ')}")
            except Exception as e1:
                self._log_error(f"You can't do that action. {str(e)}")

    def flush_history(self):
        self.instance.sequential_exception_count = 0
        self.history = []

    def __next__2(self):
        if self.buffer:
            self._log_comment(self.buffer)
            self.buffer = ""
        chunk_generator = self.program_generator()
        for chunk in chunk_generator:
            chunk_message = chunk['choices'][0]['delta']
            if chunk_message.get('content'):
                content = chunk_message.get('content')
                self.buffer += content
                self.buffer = self.buffer.lstrip()

                regex_pattern = r'\w+\([^;]*?\);'
                matches = re.findall(regex_pattern, self.buffer)
                if matches:
                    for line in matches:
                        if not line:
                            continue
                        index = self.buffer.find(line)
                        end = index + len(line)
                        snippet = self.buffer[:index]
                        comments = snippet.split("\n")
                        if len(comments):
                            comment = comments[0].lstrip("/#")
                            if comment:
                                self._log_comment(comment)
                                self.buffer = ""

                        try:
                            if not line.lstrip("# "):
                                continue
                            if line.find("\n") != -1:
                                line = line.split("\n")[-1]

                            self._log_command(line)
                            try:
                                result = self.instance.eval(line.rstrip(';'))
                            except SyntaxError as e:
                                raise

                            if result and isinstance(result, str):
                                self._log_observation(result)


                        except Exception as e:
                            try:
                                error, reason = e.args
                                self._log_error(f"{error}. {str(reason).replace('_', ' ')}")
                            except Exception as e1:
                                self._log_error(f"You can't do that action. {str(e)}")

                            return
                        finally:
                            self.buffer = ""
