import json
from datetime import datetime
from typing import List, Union

from bcolors import bcolors
from models.event import Event
from models.event_type import EventType
from models.insufficient_score_exception import InsufficientScoreException
from models.role_type import RoleType
from models.slot import Slot

schema = \
"""
# Observe and describe the natural resources and landscape around you
inspect_resources() -> dict;

# Inspect entities within a 20-meter radius around you
inspect_entities(radius=20) -> list;

# Examine the items currently in your inventory
inspect_inventory() -> dict;

# Move to (10, 5), laying transport belts as you go
move_to((10, 5), laying='transport-belt');

# Craft 1 iron chest
craft_item('iron-chest', quantity=1);

# Place an assembling machine facing up, at (1, 1)
entity_position = place_entity('assembling-machine-1', direction=UP, position=(1, 1));

# Place a burner drill facing down, on to the nearest buildable position
entity_position = place_entity('burner-mining-drill', direction=DOWN, exact=False, position=(0,0));

# Pick up coal near (-2, 0)
pickup_entity('coal', (-2, 0));

# Insert 1 coal from your inventory into the nearest mining drill for fuel
insert_item('coal', target_position=nearest('burner-mining-drill'), quantity=1);

# Extract 1 coal from the entity at (0, 1)
extract_item('coal', source_position=(0, 1), quantity=1);

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

brief = \
    f"""
You are an expert Factorio player. You have access to the following API.

```
{schema}
``` 
To play, you must only use the methods from this python API with basic logical flow, variable assignment and arithmetic.

Example:
```
# Place a burner-mining-drill and a furnace next to its drop point
stone_position = nearest("stone")
drill_position = place_entity('burner-mining-drill', position=stone_position, direction=UP)
furnace_position = place_entity_next_to('stone-furnace', reference_position=ore, direction=UP, gap=0)

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

class Memory(object):

    def __init__(self, size=10, max_history=16, ignore_members=[]):
        self._ignore_members = ignore_members
        self.history: List[Event] = []
        self.max_size = max_history
        self.brief = brief
        self.size = size
        self.log_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".log"
        self.trace_file = "log/" + datetime.now().strftime("%H-%M-%d-%m-%Y") + ".trace"
        self.variables = {}
        self._score = []
        self.current_score = 0

    def __iter__(self, *args, **kwargs) -> List[Slot]:
        """
        Get a frame of messages to pass to GPT.
        :param args:
        :param kwargs:
        :return:
        """

    def log_variables(self, instance):
        members = [attr for attr in dir(instance) if not callable(getattr(instance, attr)) and not attr.startswith("__") and attr not in self._ignore_members]

        variable_string = ""
        for member in members:
            self.variables[member] = instance.__dict__[member]
            variable_string += f'\n{member} = {str(instance.__dict__[member])}'

        self._log_history(variable_string.strip(), type=EventType.VARIABLE)

    def log_warnings(self, alerts):
        alert_string = "Warning: " + "\nWarning: ".join(alerts)
        self._log_history(alert_string, type=EventType.WARNING)

    def log_error(self, message, line=0):
        output = f"{bcolors.FAIL}{message}"

        # If the previous command caused the error, truncate it to omit the code that wasn't run.
        last_commands = self.get_last_events(EventType.COMMAND)
        if last_commands:
            last_command = last_commands[0]
            lines = last_command.message.split("\n")
            last_command_lines = lines[:line + 1]
            rewritten_last_message = "\n".join(last_command_lines)
            last_command.message = rewritten_last_message

        self._log_to_file(output)
        print(output)
        self._log_history(message, type=EventType.ERROR)

    def log_command(self, message):
        output = f"{bcolors.OKBLUE}{message}"
        self._log_to_trace(message)
        self._log_to_file(output)
        print(output)
        self._log_history(message, type=EventType.COMMAND)

    def log_score(self, score):
        self._score = self._score[-self.max_size:]
        self._score.append(score)
        self.current_score = self._score[-1] - self._score[0]
        if self._score[0] == self._score[-1] and len(self._score) == self.max_size+1:
            raise InsufficientScoreException("Insufficient score. Resetting.")
        print("Score: ",score)

    def log_observation(self, message):
        output = f"{bcolors.OKGREEN}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, type=EventType.OBSERVATION)

    def get_last_events(self, types: Union[EventType, List[EventType]], number: int = 1):
        if isinstance(types, int):
            types = [types]
        matching_events = [event for event in reversed(self.history) if event.type in types]
        if not matching_events:
            return []
        subset = matching_events[:number]
        subset.reverse()
        return subset

    def _log_to_trace(self, message):
        with open(self.trace_file, "a") as f:
            f.write(message + "\n")

    def _log_to_file(self, message):
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def _log_history(self, message, type:EventType = EventType.COMMAND):
        if isinstance(message, dict):
            message = json.dumps(message, indent = 4)

        # The commands are what the agent makes, everything else is what the system makes.
        if type == EventType.OBSERVATION \
                or type == EventType.WARNING \
                or type == EventType.ERROR \
                or type == EventType.VARIABLE:
            role = RoleType.USER
        elif type == EventType.COMMAND:
            role = RoleType.ASSISTANT

        self.history.append(Event(role=role, message = message, type=type))

        #if self.history and self.history[-1]['role'] == role and type != "error" and type != "warning":
        #    self.history[-1]['content'] += f"\n{message}"
        #else:
        #    self.history.append({
        #        "role": role, "content": message
        #    })
