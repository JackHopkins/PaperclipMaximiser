import re
import time
from datetime import date, datetime
from multiprocessing import freeze_support

import backoff
import regex

from bcolors import bcolors
from factorio_instance import FactorioInstance
from vocabulary import Vocabulary

schema2 = \
    """
POSITION: (int, int) # x and y position
RELATIVE_POSITION: (int, int) # x and y position from you
ENTITY: str # factorio entity
ROTATION: int # cardinal directions between 0-3, ranging clockwise from east

nature() # describe what resources and natural obstacles there are
inspect() # inspect nearby player entities
inventory() # look to see what items you have
craft(ENTITY, count=1) #craft 1 ENTITY.
place(ENTITY, ROTATION, POSITION) # place ENTITY from inventory with ROTATION at POSITION
pickup(POSITION); #pickup at POSITION
wait(5) # wait 5 seconds.
insert(ENTITY, POSITION, count=1) # insert 1 into ENTITY at POSITION
extract(ENTITY, POSITION, count=1) # extract 1 ENTITY from the entity at POSITION
set_recipe(POSITION, ENTITY) # set recipe of nearby entity to craft ENTITY
goto(nearest(ENTITY) # move to the nearest ENTITY
goto(POSITION)
goto(POSITION, trailing=ENTITY) #move to POSITION trailing ENTITY behind you as you go. Useful for pipes and transport-belts.
harvest(RELATIVE_POSITION, count=5) # harvest/mine 5 of the entity at POSITION
rotate(POSITION, ROTATION) # rotate ENTITY at POSITION
"""
schema3 = \
    """
nature(); # look around and describe what resources and nature you see
inspect(20); # inspect the entities 20m around you in every direction
inventory(); # look to see what items you have
goto((10, 5), trailing='transport-belt'); #move 10m east, 5 south creating transport as you go.
craft('iron-chest', count=1); #craft 1 iron chest.
place('assembling-machine-1', 2, (1,1)); # places an assembling machine facing north, 1m north and east of you.
place('burner-drill', 2, nearest('coal')); # places an assembling machine facing north, 1m north and east of you.
pickup((-2, 0)); # pickup placed entity 2m west of you
wait(5); # wait 5 seconds.
insert('coal', (0, 0), count=1); # inserts 1 coal into nearby entity from inventory
extract('coal', (0, 1), count=1); # picks up 1 coal from the entity 1m to the south
extract('coal', nearest('iron-chest'), count=1); # picks up 1 coal from nearest iron chest
set_recipe((0, 1), 'iron-chest'); # set recipe of entity 1m south to craft 'iron-chest'
goto((0, -40)); # move north 40 metres
goto(nearest('tree')); # move to the nearest tree
harvest((-2, 0), count=5); # harvest or mine 5 of the entity 2m left of you.
rotate((0,0), 1); # rotate nearby entity to face west
"""
schema = \
"""
observe_nature(); # Observe and describe the natural resources and landscape around you
inspect_radius(20); # Inspect entities within a 20-meter radius around you
check_inventory(); # Examine the items currently in your inventory

move_to((10, 5), laying='transport-belt'); # Move 10 meters east and 5 meters south, laying transport belts as you go
craft_item('iron-chest', quantity=1); # Craft 1 iron chest
place_entity('assembling-machine-1', direction=2, position=(1, 1)); # Place an assembling machine facing north, 1 meter north and east of your current position
place_entity('burner-drill', direction=2, position=nearest('coal')); # Place a burner drill facing north, next to the nearest coal resource

pickup_entity((-2, 0)); # Pick up the entity placed 2 meters west of your current position
wait_duration(5); # Wait for 5 seconds

insert_item('coal', target_position=(0, 0), quantity=1); # Insert 1 coal from your inventory into the entity at your current position
extract_item('coal', source_position=(0, 1), quantity=1); # Extract 1 coal from the entity 1 meter south of your current position
extract_item('coal', source_position=nearest('iron-chest'), quantity=1); # Extract 1 coal from the nearest iron chest

set_entity_recipe((0, 1), recipe='iron-chest'); # Set the recipe of the entity 1 meter south of your position to craft 'iron-chest'
move_to((0, -40)); # Move 40 meters to the north
move_to(nearest('tree')); # Move to the position of the nearest tree

harvest_resource((-2, 0), quantity=5); # Harvest or mine 5 of the resource located 2 meters west of your current position
rotate_entity((0, 0), direction=1); # Rotate the entity at your current position to face west
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
You are playing Factorio. To play, submit programs with the following commands in them:

```
{schema}
``` 
- Gain score from building a higher production factory. 
- You can use '#' comments to help you think.
- A command will only execute if ended with a ';' character.
- Maximize your score.
"""

import openai


class FactorioRunner:

    def __init__(self,
                 api_key,
                 model="gpt-4",
                 buffer_size=25,
                 fast=True,
                 trace=False):
        self.buffer = ""
        self.model = model
        self.buffer_size = buffer_size
        openai.api_key = api_key
        self.log_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".log"
        self.trace_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".trace"
        inventory = {
            'coal': 50,
            'copper-plate': 50,
            'iron-plate': 50,
            'iron-chest': 1,
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
            #self._log_to_file("###NEW EPISODE###")
            self._log_observation(self.instance.observe_nature())
            self._log_comment("Lets start by checking my inventory.")
            self._log_observation(self.instance.check_inventory())
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
        time.sleep(3)
        return openai.ChatCompletion.create(
            model=self.model,  # "gpt-3.5-turbo",
            max_tokens=256,
            messages=messages,
            stop="\n\n#",
            stream=True
        )

    def _log_history(self, message, role, error=False):
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
        output = f"{bcolors.FAIL}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, "user", error=True)

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

    def __next__(self):
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
