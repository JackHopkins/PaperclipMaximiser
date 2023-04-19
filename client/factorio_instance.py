import ast
import concurrent
import math
import time
from timeit import default_timer as timer
from typing import List, Tuple, Optional

import numpy as np
import yaml
from dotenv import load_dotenv
from numpy import ndarray, zeros
from scipy import ndimage
from slpp import slpp as lua

from client.factorio_rcon_utils import _load_actions, _load_init, _lua2python
from client.rcon.factorio_rcon import RCONClient
from client.utils import stitch
from models.zero_dict import ZeroDict
from utilities.pathfinding import get_path
from vocabulary import Vocabulary

load_dotenv()

PLAYER = 1
NONE = 'nil'
CHUNK_SIZE = 32
MAX_SAMPLES = 5000
FIELDS = ['all', 'enemy', 'pollution', 'factory', 'water', 'iron-ore', 'uranium-ore', 'coal', 'stone',
          'copper-ore', 'crude-oil', 'trees']

global var
var = {}


class FactorioInstance:

    def __init__(self, address=None, vocabulary: Vocabulary = None, bounding_box=20, tcp_port=27015, inventory={}):
        self.tcp_port = tcp_port
        try:
            self.rcon_client = RCONClient(address, tcp_port, 'factorio')
            self.address = address
        except:
            self.rcon_client = RCONClient('localhost', tcp_port, 'factorio')
            self.address = 'localhost'

        self.sequential_exception_count = 0
        self.script_dict = {**_load_actions(), **_load_init()}
        self.vocabulary = vocabulary
        self.trail_state = {
            "trail_on": False,
            "trail_entity": None
        }
        self.tasks = []
        self.player_location = (0, 0)
        self.last_observed_player_location = (0, 0)
        self.last_location = (0, 0)
        self.movement_vector = (0, 0)
        self.last_direction = -1
        self.bounding_box = bounding_box
        self.grid_world = zeros((bounding_box, bounding_box))
        self.minimap_bounding_box = bounding_box * 4

        initial_score, _ = self._send('score')
        self.initial_score = initial_score['player']

        mu, sigma = 0, CHUNK_SIZE * 20
        self.minimap_normal = s = np.random.normal(mu, sigma, MAX_SAMPLES)
        self.chunk_cursor = 0
        self.minimaps = self._initialise_minimaps()

        self.connect()
        self.initialise(**inventory)

        self.UP = 0
        self.LEFT = 3
        self.RIGHT = 2
        self.DOWN = 1

    def __getitem__(self, key):
        if key not in dir(self) or key.startswith('__'):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    # def eval(self, code: str,):
    #    buffer = io.StringIO()
    #    with redirect_stdout(buffer):
    #        exec(code, {}, self)
    #    value = buffer.getvalue()
    #   return value

    def _eval_with_timeout(self, expr):
        tree = ast.parse(expr)
        results = []
        for node in tree.body:
            try:
                if isinstance(node, ast.Expr):
                    compiled = compile(ast.Expression(node.value), 'file', 'eval')
                    response = eval(compiled, {}, self)
                    if response != True and response:
                        results.append(response)
                        self.sequential_exception_count = 0
                else:
                    compiled = compile(ast.Module([node], type_ignores=[]), 'file', 'exec')
                    exec(compiled, {}, self)
                    results.append("Executed successfully")
            except Exception as e:
                self.sequential_exception_count += 1
                parts = list(e.args)
                sentences = ". ".join([str(part).replace("_", " ") for part in parts])
                results.append(f"Error: {sentences}")
                break

        return '\n'.join([f"Line {i + 1}: {str(r)}" for i, r in enumerate(results)] + [f"Score: {self.score()}"])

    def eval(self, expr, timeout=15):
        "Evaluate several lines of input, returning the result of the last line with a timeout"
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._eval_with_timeout, expr)
                result = future.result(timeout)
                return result
        except concurrent.futures.TimeoutError:
            return "Error: Evaluation timed out"
        except Exception as e:
            trace = e.__traceback__
            return f"Error: {str(e)}"

    def run_tasks(self):
        for task in self.tasks:
            try:
                next(task)()
            except StopIteration:
                self.observe()

    def wait_duration(self, seconds: int):
        if seconds > 2:
            time.sleep(seconds - 2)
        nearby = self.inspect_entities(20)
        if not nearby:
            nearby = "No entities within 20m."
        # inventory = self.inventory()
        return f"While you wait, you look around. \n{nearby}"


    def inspect_entities(self, distance: int, relative: bool = False):
        response, time_elapsed = self._send('inspect', PLAYER, distance)
        entities = []
        try:
            if isinstance(response, dict):
                entity_list = list(response.values())
                for entity in entity_list:
                    position = tuple(entity["position"].values())

                    if not relative:
                        position = (position[0] + self.last_observed_player_location[0],
                                    position[1] + self.last_observed_player_location[1])

                    entity_dict = {
                        "type": entity["name"],
                        "direction": entity["direction"],
                        "position": position
                    }

                    if "path_ends" in entity:
                        if len(entity["path_ends"]) > 1:
                            start = position
                            end = None
                            for _, path_end in entity["path_ends"].items():
                                if path_end["unit_number"] == min(
                                        [e["unit_number"] for e in entity["path_ends"].values()]):
                                    end = tuple(path_end["position"].values())
                                    break

                            entity_dict["start_position"] = start
                            entity_dict["end_position"] = end
                            entity_dict["quantity"] = len(entity["path_ends"])

                    if "warnings" in entity:
                        entity_dict["warning"] = ". ".join(
                            [val.replace("_", " ") for val in entity['warnings'].values()]) + "."

                    if "contents" in entity and entity['contents']:
                        entity_dict["contents"] = {k: v for k, v in entity['contents'].items()}

                    elif "crafted_items" in entity:
                        contains = {}
                        if entity['crafted_items']:
                            contains.update({k: v for k, v in entity['crafted_items'].items()})
                        if entity['ingredients']:
                            contains.update({k: v for k, v in entity['ingredients'].items()})
                        if contains:
                            entity_dict["contents"] = contains

                    if "status" not in entity_dict:
                        entity_dict["status"] = "empty" if "contents" not in entity_dict else "not empty"

                    entities.append(entity_dict)

            response_dict = {"entities": entities}
            #response = yaml.dump(response_dict)

            self.last_observed_player_location = (0, 0)
        except Exception as e:
            print(e)
            response = {}

        return response_dict

    def inspect_radius_natural(self, distance: int):
        response, time_elapsed = self._send('inspect', PLAYER, distance)
        descriptions = []
        try:
            if isinstance(response, dict):
                entity_list = list(response.values())
                for entity in entity_list:
                    position = tuple(entity["position"].values())
                    if "path_ends" in entity:
                        if len(entity["path_ends"]) > 1:
                            # Find the start and end points of the path
                            start = tuple(entity["position"].values())
                            end = None
                            for _, path_end in entity["path_ends"].items():
                                if path_end["unit_number"] == min(
                                        [e["unit_number"] for e in entity["path_ends"].values()]):
                                    end = tuple(path_end["position"].values())
                                    break

                            # Calculate the number of entities in the path
                            num_entities = len(entity["path_ends"])

                            # Describe the path
                            description = f"A line of {num_entities} {entity['name']}s going {entity['direction']}, starting from {start} and ending at {end}"
                            descriptions.append(description)
                        else:
                            description = f"A {entity['name']} facing {entity['direction']}, at {position}."
                            descriptions.append(description)
                    else:
                        warnings = (". ".join([val.replace("_", " ") for val in entity['warnings'].values()]) + ".") \
                            if "warnings" in entity else ""

                        if "contents" in entity and entity['contents']:
                            contents = ", ".join([f"{v}x {k}" for k, v in entity['contents'].items()])
                            description = f"An {entity['name']} facing {entity['direction']} at {position} containing {contents}. {warnings}"
                        elif "crafted_items" in entity:
                            contains = []
                            if entity['crafted_items']:
                                contains.extend([f"{v}x {k}" for k, v in entity['crafted_items'].items()])
                            if entity['ingredients']:
                                contains.extend([f"{v}x {k}" for k, v in entity['ingredients'].items()])
                            contents = ("containing " + ", ".join(contains)) if contains else ""
                            description = f"An {'empty ' if not contents else ''}{entity['name']} facing {entity['direction']} at {position} {contents}. {warnings}"

                        else:
                            description = f"An empty {entity['name']} facing {entity['direction']}, at {position}. {warnings}"
                        descriptions.append(description)
            if descriptions:
                response = "You see:\n- " + "\n- ".join(descriptions)
            else:
                response = "No entities nearby."
            self.last_observed_player_location = (0, 0)
        except Exception as e:
            print(e)
            response = {}

        return response


    def nearest(self, type: str = 'coal', relative: bool = False, **kwargs):
        response, time_elapsed = self._send('find', PLAYER, type.replace("_", "-"))

        if not response:
            raise Exception(f"No {type} found on the map")

        if not self.last_observed_player_location:
            self.last_observed_player_location = self.player_location

        if relative:
            return (-math.floor(response['x']) + self.last_observed_player_location[0],
                    -math.floor(response['y']) + self.last_observed_player_location[1])
        else:
            return (math.floor(response['x']), math.floor(response['y']))

    def place_entity_next_to(self, entity: str, reference_position: Tuple = (0,0), direction: int = 1, gap: int =0, relative=False):
        x, y = reference_position

        if relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('place_entity_next_to', PLAYER, entity, x, y, direction, gap)
        if not isinstance(response, dict):
            raise Exception(f"Could not place {entity} at {reference_position}.", response)
        return response['x'], response['y']

    def connect_entities(self,
                         source_position:Tuple=(0,0),
                         target_position:Tuple=(0,0),
                         connection_type='burner-inserter',
                         relative = False):

        source_x, source_y = source_position
        target_x, target_y = target_position

        if relative:
            source_x -= self.last_observed_player_location[0]
            target_x -= self.last_observed_player_location[0]
            source_y -= self.last_observed_player_location[1]
            target_y -= self.last_observed_player_location[1]

        response, elapsed = self._send('connect_entities',
                                       PLAYER,
                                       source_x,
                                       source_y,
                                       target_x,
                                       target_y,
                                       connection_type)
        if response != 1:
            raise Exception(f"Could not connect {(source_x, source_y)} to {(target_x, target_y)}.", response)
        return True


    def move_to(self,
                absolute_position: Optional[Tuple[int, int]],
                relative_position: Tuple[int, int] = (0, 0),
                laying=None,
                leading=None):
        try:
            if absolute_position is not None:
                if not isinstance(absolute_position, Tuple):
                    raise Exception(
                        "You need to pass in a tuple like (x, y) for the absolute position. You passed in scalar.")
                start_x, start_y = self.player_location
                relative_position = (absolute_position[0] - start_x, absolute_position[1] - start_y)

            if not isinstance(relative_position, Tuple):
                raise Exception("You need to pass in a tuple like (x, y). You passed in scalar.")
            relative_end_x, relative_end_y = relative_position
            start_x, start_y = self.player_location
            offset_x = self.bounding_box // 2
            offset_y = self.bounding_box // 2
            last_observed_x = self.last_observed_player_location[0]
            last_observed_y = self.last_observed_player_location[1]

            end = (offset_x + relative_end_x,  # - last_observed_x,
                   offset_y + relative_end_y)  # - last_observed_y)

            path = get_path(end, self.collision_mask, start=(offset_x, offset_y))

            def direction_from_step(step, trailing=None, leading=None):
                offset = self.bounding_box // 2
                return self.move(*((step - [offset, offset]) - self.player_location), trailing=trailing,
                                 leading=leading)

            task_queue = []
            task_queue.extend(
                [(lambda s: direction_from_step(s + (start_x, start_y), trailing=laying, leading=leading))(s) for s in
                 path])
            task_queue.extend([(lambda: self.observe())()])

            self.tasks.append(iter(task_queue))
        except Exception as e:
            raise Exception("Could not goto", e)

    def move_to2(self,
                 relative_position: Tuple[int, int] = (0, 0),
                 laying=None,
                 leading=None):
        try:
            if not isinstance(relative_position, Tuple):
                raise Exception("You need to pass in a tuple like (x, y). You passed in scalar.")
            relative_end_x, relative_end_y = relative_position
            start_x, start_y = self.player_location
            offset_x = self.bounding_box // 2  # - self.last_observed_player_location[0]
            offset_y = self.bounding_box // 2  # - self.last_observed_player_location[1]
            last_observed_x = self.last_observed_player_location[0]
            last_observed_y = self.last_observed_player_location[1]

            end = (offset_x + relative_end_x - last_observed_x,
                   offset_y + relative_end_y - last_observed_y)

            path = get_path(end, self.collision_mask, start=(offset_x, offset_y))

            def direction_from_step(step, trailing=None, leading=None):
                offset = self.bounding_box // 2
                return self.move(*((step - [offset, offset]) - self.player_location), trailing=trailing,
                                 leading=leading)

            task_queue = []  # (lambda: self._set_walking(True))()]
            task_queue.extend(
                [(lambda s: direction_from_step(s + (start_x, start_y), trailing=laying, leading=leading))(s) for s in
                 path])
            task_queue.extend([(lambda: self.observe())()])  # , (lambda: self._set_walking(False))()])

            self.tasks.append(iter(task_queue))
        except Exception as e:
            raise Exception("Could not goto", e)

    def _initialise_minimaps(self):
        bounding_box = self.minimap_bounding_box
        # minimaps = {field: zeros((bounding_box, bounding_box)) for field in fields}

        return np.zeros((len(FIELDS), bounding_box, bounding_box))

    def reset(self, seed=None):
        pass

    def close(self):
        pass

    def _get_command(self, command, parameters=[], measured=True):
        prefix = "/c " if not measured else '/command '
        if command in self.script_dict:
            script = prefix + self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command
        return script

    def _send(self, command, *parameters, trace=False) -> List[str]:
        start = timer()
        script = self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = self.rcon_client.send_command(script)
        # print(lua_response)
        return _lua2python(command, lua_response, start=start)

    def connect(self):
        try:
            self.rcon_client.connect()
            player_exists, time_elapsed = self._send('/c rcon.print(game.players[1].position)', PLAYER)
            if not player_exists:
                raise Exception(
                    "Player hasn't been initialised into the game. Please log in once to make this node operational.")

        except Exception as e:
            raise ConnectionError(f"Could not connect to {self.address} at tcp/{self.tcp_port}: \n{e.args[0]}")

        print(f"Connected to {self.address} client at tcp/{self.tcp_port}.")

    def initialise(self, **kwargs):

        self._send('initialise', PLAYER)
        self._send('util')
        self._send('production_score')
        # self.factorio_client.send('new_world', PLAYER)
        self._send('clear_inventory', PLAYER)
        self._send('reset_position', PLAYER, 0, 0)

        for entity, count in kwargs.items():
            self._send('give_item', PLAYER, entity, count)

        try:
            results = self.observe(trace=True)
        except Exception as e:
            # print(e)
            raise Exception(f"Could not initialise server at port {self.tcp_port}")

        return results

    def _set_walking(self, walking: bool):
        if walking:
            lua_response = self.rcon_client.send_command(
                '/c game.players[1].character.walking_state = {walking = true, direction = defines.direction.north}')
        else:
            lua_response = self.rcon_client.send_command(
                '/c game.players[1].character.walking_state = {walking = false, direction = defines.direction.north}')
        return lua_response

    def rotate_entity2(self, position: Tuple[int, int], direction=1):
        x, y = position
        response, elapsed = self._send('rotate', PLAYER, x, y, direction)
        if not response:
            raise Exception("Could not rotate.", response)
        return True

    def rotate_entity(self, position: Tuple[int, int], direction=1, relative: bool = False) -> bool:
        """
        Rotates an entity at the specified position (x, y) in the given direction.
        By default, the position is absolute. If the 'relative' flag is set to True,
        the position will be treated as relative to the agent as the origin (0, 0).
        :param position: (x, y) position of the entity.
        :param direction: The direction to rotate the entity (default: 1).
        :param relative: If True, treats the position as relative to the agent (default: False).
        :return: True if the entity was rotated, False if no-op.
        """
        x, y = position

        if not relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('rotate', PLAYER, x, y, direction)
        if not response:
            raise Exception("Could not rotate.", response)
        return True

    def harvest_resource(self, position: Tuple[int, int], quantity=1, relative: bool = False) -> bool:
        """
        If there is an entity at the specified position (x, y), this action triggers an
        interaction as follows: If the item can be picked up, the agent picks up the item. If the
        item can be harvested, the agent harvests the item (resource). By default, the position
        is absolute. If the 'relative' flag is set to True, the position will be treated as relative
        to the agent as the origin (0, 0). If there is no entity at (x, y), this action is a no-op.
        :param position: (x, y) position of the entity.
        :param quantity: The quantity to be harvested (default: 1).
        :param relative: If True, treats the position as relative to the agent (default: False).
        :return: True if an action happened, False if no-op.
        """
        x, y = position

        if not relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('harvest', PLAYER, x, y, quantity)
        if response != 1:
            raise Exception("Could not harvest.", response)
        return True

    def harvest_resource2(self, position: Tuple[int, int], quantity=1) -> bool:
        """
        If there is an entity at local position (x, y), this action triggers an
        interaction as follows: If the item can be picked up, the agent picks up the item. If the
        item can be harvested, the agent harvests the item (resource). Here, the local position
        is the (x, y) position relative to the agent as the origin (0, 0). If there is no entity at
        (x, y), this action is a no-op.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :return: True if an action happened, False if no-op.
        """
        x, y = position
        response, elapsed = self._send('harvest', PLAYER, x, y, quantity)
        if response != 1:
            raise Exception("Could not harvest.", response)
        return True

    def pickup_entity(self, name: str, position: Tuple[int, int], relative=False) -> bool:
        """
        If there is an entity at local position (x, y), this action triggers an
        interaction as follows: If the item can be picked up, the agent picks up the item. If the
        item can be harvested, the agent harvests the item (resource). Here, the local position
        is the (x, y) position relative to the agent as the origin (0, 0). If there is no entity at
        (x, y), this action is a no-op.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :return: True if an action happened, False if no-op.
        """
        x, y = position

        if relative:
            x += self.last_observed_player_location[0]
            y += self.last_observed_player_location[1]

        response, elapsed = self._send('pickup', PLAYER, x, y, name)
        if response != 1:
            raise Exception("Could not pickup, did you intend to harvest?", response)
        return True

    def insert_item(self, entity: str, target_position: Tuple[int, int] = (0, 0), quantity=5) -> int:
        x, y = target_position
        """
        If there is an entity at local position (x, y) that accepts a resource, the agent
        adds a default amount of resource to the entity. If there is no entity at (x, y), this action
        is a no-op.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param amount: Amount of fuel to attempt to deposit
        :return: Amount of fuel deposited
        """
        response, elapsed = self._send('insert',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       quantity,
                                       x,
                                       y)
        if response != 1:
            raise Exception("Could not insert", response)

        return True

    def extract_item(self, entity: str, source_position: Tuple[int, int], quantity=5, relative=False) -> int:
        x, y = source_position

        if not relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('extract',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       quantity,
                                       x,
                                       y)
        if response != 1:
            raise Exception("Could not extract.", response)

        return True

    def craft_item(self, entity: str, quantity: int = 1) -> bool:
        """
        The agent places an entity e at local position (x, y) if the agent has
        enough resources. If the agent chooses to place an empty entity at (x, y), any entity at
        (x, y) is removed. If the agent chooses to place an entity where there is already one,
        the previous entity is first removed and the new entity replaces it.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param entity: Entity to place from inventory
        :param direction: Cardinal direction to place entity
        :return: True if action carried out, False if no-op
        """
        success, elapsed = self._send('craft', PLAYER, entity.replace("_", "-"), quantity)
        if success != 1:
            if success is None:
                raise Exception(f"Could not craft a {entity}", "Ingredients cannot be crafted by hand.")
            else:
                raise Exception(f"Could not craft a {entity}", success)
        return "Crafting successful"

    def place_entity(self, entity: str, direction=0, position: tuple[int, int] = (0, 0), relative=False) -> Optional[Tuple]:
        """
        The agent places an entity e at local position (x, y) if the agent has
        enough resources. If the agent chooses to place an empty entity at (x, y), any entity at
        (x, y) is removed. If the agent chooses to place an entity where there is already one,
        the previous entity is first removed and the new entity replaces it.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param entity: Entity to place from inventory
        :param direction: Cardinal direction to place entity
        :return: True if action carried out, False if no-op
        """
        x, y = position

        if direction > 3 or direction < 0:
            raise Exception("Directions are between 0-3")

        if relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('place',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       direction + 1,
                                       x,
                                       y
                                       )
        if not isinstance(response, dict):
            raise Exception(f"Could not place {entity}", response.replace("___", ", ").replace("_", " "))

        return (response['x'], response['y'])

    def set_entity_recipe(self, position: Tuple[int, int], recipe: str, relative=False) -> bool:
        x, y = position

        if not relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('recipe', PLAYER, recipe, x, y)

        if response != 1:
            raise Exception(f"Could not set recipe to {recipe}", response)
        return True

    def trail(self, entity: str) -> bool:
        """
        The agent toggles placement mode, where an entity e is placed at the
        local position (x, y), and every subsequent position of the agent. Trail placement is
        toggled off once the agent runs out of resources, or if it chooses the action a second
        time with an empty entity. Trail placement is switched if the agent performs the action
        again with a different resource
         :param entity: The entity that is being toggled on.
        :return: Whether the action was carried out.
        """
        if entity:
            self.trail_state["trail_on"] = True
            self.trail_state["trail_entity"] = entity
        else:
            self.trail_state["trail_on"] = False
            self.trail_state["trail_entity"] = None

        return True

    def inspect_resources(self, relative=False):
        def get_direction(y_offset, x_offset):
            angle = (np.arctan2(-y_offset, -x_offset) * 180 / np.pi) - 90

            if angle < 0:
                angle += 360

            directions = [
                (348.75, 360, "north"),
                (0, 11.25, "north"),
                (11.25, 33.75, "north-northeast"),
                (33.75, 56.25, "northeast"),
                (56.25, 78.75, "east-northeast"),
                (78.75, 101.25, "east"),
                (101.25, 123.75, "east-southeast"),
                (123.75, 146.25, "southeast"),
                (146.25, 168.75, "south-southeast"),
                (168.75, 191.25, "south"),
                (191.25, 213.75, "south-southwest"),
                (213.75, 236.25, "southwest"),
                (236.25, 258.75, "west-southwest"),
                (258.75, 281.25, "west"),
                (281.25, 303.75, "west-northwest"),
                (303.75, 326.25, "northwest"),
                (326.25, 348.75, "north-northwest"),
            ]

            for start, end, direction in directions:
                if angle >= start and angle < end:
                    return direction

            return "north"

        vocabulary = self.vocabulary.i_vocabulary
        grid_world = self.grid_world
        unique_objects = np.unique(grid_world)

        groups = {}
        small_groups = {}

        for obj in unique_objects:
            if obj == 0:
                continue

            binary_array = (grid_world == obj).astype(int)
            connected_components, num_labels = ndimage.measurements.label(binary_array)

            for label in range(1, num_labels + 1):
                if obj == -1:
                    continue
                item = vocabulary[obj]
                if item == "character":
                    continue

                group_indices = np.where(connected_components == label)
                group_size = len(group_indices[0])

                y_offset = int(np.mean(group_indices[0])) - (self.bounding_box // 2)
                x_offset = int(np.mean(group_indices[1])) - (self.bounding_box // 2)

                if not relative:
                    y_offset += self.last_observed_player_location[1]
                    x_offset += self.last_observed_player_location[0]

                y_max = int(np.max(group_indices[0])) - (self.bounding_box // 2)
                x_max = int(np.max(group_indices[1])) - (self.bounding_box // 2)

                y_min = int(np.min(group_indices[0])) - (self.bounding_box // 2)
                x_min = int(np.min(group_indices[1])) - (self.bounding_box // 2)
                named_dir = get_direction(y_offset, x_offset)
                direction = {
                    "offset": abs(y_offset),
                    "named_direction": named_dir,
                    "min_coordinates": (x_min, y_min),
                    "max_coordinates": (x_max, y_max)
                }

                if group_size < 50:
                    if item not in small_groups:
                        small_groups[item] = {"count": 0, "directions": {}}
                    small_groups[item]["count"] += group_size
                    small_groups[item]["directions"][named_dir] = small_groups[item]["directions"].get(named_dir,
                                                                                                       0) + abs(
                        y_offset)
                else:
                    if item not in groups:
                        groups[item] = []

                    group_description = {
                        "size": group_size,
                        "direction": direction
                    }
                    groups[item] =  group_description

        for item, data in small_groups.items():
            count = data["count"]
            cardinals = [
                {"distance": (value if value < 1000 else math.floor(value / 1000)),
                 "unit": "metres" if value < 1000 else "km",
                 "direction": direction}
                for direction, value in data["directions"].items()
            ]
            if not cardinals:
                continue

            #if count > 1000:
            #    count_str = math.floor((float(count) / 100)) / 10

            if item not in groups:
                groups[item] = []

            group_description = {
                "size": count,
                "directions": cardinals,
                "scattered": True
            }
            groups[item] = group_description

        return groups

    def inspect_resources2(self, relative=False):
        def get_direction(y_offset, x_offset):
            angle = (np.arctan2(-y_offset, -x_offset) * 180 / np.pi) - 90

            if angle < 0:
                angle += 360

            directions = [
                (348.75, 360, "north"),
                (0, 11.25, "north"),
                (11.25, 33.75, "north-northeast"),
                (33.75, 56.25, "northeast"),
                (56.25, 78.75, "east-northeast"),
                (78.75, 101.25, "east"),
                (101.25, 123.75, "east-southeast"),
                (123.75, 146.25, "southeast"),
                (146.25, 168.75, "south-southeast"),
                (168.75, 191.25, "south"),
                (191.25, 213.75, "south-southwest"),
                (213.75, 236.25, "southwest"),
                (236.25, 258.75, "west-southwest"),
                (258.75, 281.25, "west"),
                (281.25, 303.75, "west-northwest"),
                (303.75, 326.25, "northwest"),
                (326.25, 348.75, "north-northwest"),
            ]

            for start, end, direction in directions:
                if angle >= start and angle < end:
                    return direction

            return "north"

        vocabulary = self.vocabulary.i_vocabulary
        grid_world = self.grid_world
        unique_objects = np.unique(grid_world)

        groups = []
        small_groups = {}

        for obj in unique_objects:
            if obj == 0:
                continue

            binary_array = (grid_world == obj).astype(int)
            connected_components, num_labels = ndimage.measurements.label(binary_array)

            for label in range(1, num_labels + 1):
                if obj == -1:
                    continue
                item = vocabulary[obj]
                if item == "character":
                    continue

                group_indices = np.where(connected_components == label)
                group_size = len(group_indices[0])

                y_offset = int(np.mean(group_indices[0])) - (self.bounding_box // 2)
                x_offset = int(np.mean(group_indices[1])) - (self.bounding_box // 2)

                if not relative:
                    y_offset += self.last_observed_player_location[1]
                    x_offset += self.last_observed_player_location[0]

                y_max = int(np.max(group_indices[0])) - (self.bounding_box // 2)
                x_max = int(np.max(group_indices[1])) - (self.bounding_box // 2)

                y_min = int(np.min(group_indices[0])) - (self.bounding_box // 2)
                x_min = int(np.min(group_indices[1])) - (self.bounding_box // 2)
                named_dir = get_direction(y_offset, x_offset)
                direction = f"{abs(y_offset)} metres " \
                            f"{named_dir} " \
                            f"({x_min}, {y_min}) x ({x_max}, {y_max})"

                if group_size < 50:
                    if item not in small_groups:
                        small_groups[item] = {"count": 0, "direction": {}}
                    small_groups[item]["count"] += group_size
                    small_groups[item]["direction"][named_dir] = small_groups[item]["direction"].get(named_dir,
                                                                                                     0) + abs(y_offset)
                else:
                    group_description = f"{group_size}x {item} {direction}"
                    groups.append((group_size, group_description))

        for item, data in small_groups.items():
            count = data["count"]
            cardinals = [f"{(str(value) + ' metres') if value < 1000 else (str(math.floor(value / 1000))) + 'km'} " \
                         f"{direction}"
                         for direction, value in data["direction"].items()]
            if not cardinals:
                continue
            if len(cardinals) > 1:
                direction = f"scattered {', '.join(cardinals[:-1])}, and {cardinals[-1]} "
            else:
                direction = f"scattered {cardinals[0]} "

            if count > 1000:
                count_str = str(math.floor((float(count) / 100)) / 10) + "k"
            group_description = f"There are {count_str} {item}s {direction}"
            groups.append((count, group_description))

        # Sort groups by size and return the result
        groups.sort(reverse=True, key=lambda x: x[0])

        # self.last_observed_player_location = (0,0)
        return "\n- ".join([group[1] for group in groups])

    def observe_nature2(self):
        def get_direction(y_offset, x_offset):
            angle = (np.arctan2(-y_offset, -x_offset) * 180 / np.pi) - 90

            if angle < 0:
                angle += 360

            directions = [
                (348.75, 360, "north"),
                (0, 11.25, "north"),
                (11.25, 33.75, "north-northeast"),
                (33.75, 56.25, "northeast"),
                (56.25, 78.75, "east-northeast"),
                (78.75, 101.25, "east"),
                (101.25, 123.75, "east-southeast"),
                (123.75, 146.25, "southeast"),
                (146.25, 168.75, "south-southeast"),
                (168.75, 191.25, "south"),
                (191.25, 213.75, "south-southwest"),
                (213.75, 236.25, "southwest"),
                (236.25, 258.75, "west-southwest"),
                (258.75, 281.25, "west"),
                (281.25, 303.75, "west-northwest"),
                (303.75, 326.25, "northwest"),
                (326.25, 348.75, "north-northwest"),
            ]

            for start, end, direction in directions:
                if angle >= start and angle < end:
                    return direction

            return "north"

        vocabulary = self.vocabulary.i_vocabulary
        grid_world = self.grid_world
        unique_objects = np.unique(grid_world)

        groups = []
        small_groups = {}

        for obj in unique_objects:
            if obj == 0:
                continue

            binary_array = (grid_world == obj).astype(int)
            connected_components, num_labels = ndimage.measurements.label(binary_array)

            for label in range(1, num_labels + 1):
                if obj == -1:
                    continue
                item = vocabulary[obj]
                if item == "character":
                    continue

                group_indices = np.where(connected_components == label)
                group_size = len(group_indices[0])

                y_offset = int(np.mean(group_indices[0])) - (self.bounding_box // 2)
                x_offset = int(np.mean(group_indices[1])) - (self.bounding_box // 2)

                y_max = int(np.max(group_indices[0])) - (self.bounding_box // 2)
                x_max = int(np.max(group_indices[1])) - (self.bounding_box // 2)

                y_min = int(np.min(group_indices[0])) - (self.bounding_box // 2)
                x_min = int(np.min(group_indices[1])) - (self.bounding_box // 2)
                named_dir = get_direction(y_offset, x_offset)
                direction = f"{abs(y_offset)} metres " \
                            f"{named_dir} " \
                            f"({x_min}, {y_min}) x ({x_max}, {y_max})"

                if group_size < 50:
                    if item not in small_groups:
                        small_groups[item] = {"count": 0, "direction": {}}
                    small_groups[item]["count"] += group_size
                    small_groups[item]["direction"][named_dir] = small_groups[item]["direction"].get(named_dir,
                                                                                                     0) + abs(y_offset)
                else:
                    group_description = f"{group_size}x {item} {direction}"
                    groups.append((group_size, group_description))

        for item, data in small_groups.items():
            count = data["count"]
            cardinals = [f"{(str(value) + ' metres') if value < 1000 else (str(math.floor(value / 1000))) + 'km'} " \
                         f"{direction}"
                         for direction, value in data["direction"].items()]
            if not cardinals:
                continue
            if len(cardinals) > 1:
                direction = f"scattered {', '.join(cardinals[:-1])}, and {cardinals[-1]} "
            else:
                direction = f"scattered {cardinals[0]} "

            if count > 1000:
                count_str = str(math.floor((float(count) / 100)) / 10) + "k"
            group_description = f"There are {count_str} {item}s {direction}"
            groups.append((count, group_description))

        # Sort groups by size and return the result
        groups.sort(reverse=True, key=lambda x: x[0])

        self.last_observed_player_location = (0, 0)
        return "\n- ".join([group[1] for group in groups])

    def score(self):
        response, execution_time = self._send('score')
        if self.initial_score:
            response['player'] -= self.initial_score
        return response['player']

    def check_inventory(self):
        response, execution_time = self._send('inventory',
                                              PLAYER,
                                              )
        return ZeroDict(**response)

    def observe(self, trace=False, **kwargs):
        """

        -Chunks: At each time t, the agent receives details of a chunks of 32 x 32 tiles sampled from the environment.
        Each chunk contains a density map of resources, enemies, water, player factory.

        -Local Environment: At each time t, the agent receives all entities in a 100 × 100 grid centered on the agent’s position p. Each entity type is
        represented by a unique integer index.

        -Position: At each time t, the agent receives the agent’s current absolute position p.

        -Points of interest: At each time t, the agent receives the relative positions of the nearest points of interest.

        :param trace:
        :param kwargs:
        :return:
        """
        chunk_x, chunk_y, index_x, index_y = self._sample_chunk()
        movement_field_x, movement_field_y = self.movement_vector[0], self.movement_vector[1]
        omit = kwargs
        response, execution_time = self._send('observe',
                                              PLAYER,
                                              chunk_x,
                                              chunk_y,
                                              self.bounding_box,
                                              movement_field_x,
                                              movement_field_y,
                                              self.bounding_box * 2,
                                              trace,
                                              omit
                                              )

        if response['local_environment']:
            pass

        if not response:
            return

        try:
            if 'chunk' in response:
                self._index_chunk(response['chunk'], index_x, index_y)
        except IndexError as e:
            raise Exception("Cannot move further", str(e.args))

        try:
            if 'local_environment' in response:
                self._convert_sparse_local_into_gridworld(response['local_environment'],
                                                          movement_field_x,
                                                          movement_field_y)
        except IndexError as e:
            raise Exception("Cannot move further", str(e.args))

        try:
            if 'points_of_interest' in response:
                points_x, points_y, poi_time = self._convert_sparse_coordinates_into_tensors(
                    response['points_of_interest'])
        except IndexError as e:
            raise Exception("Cannot move further", str(e.args))

        try:
            if 'distance_to_points_of_interest' in response:
                distance_to_points_of_interest, dpoi_time = self._convert_sparse_continuous_into_tensor(
                    response['distance_to_points_of_interest'], init=100000)
        except IndexError as e:
            raise Exception("Cannot move further", str(e.args))

        if 'buildable' in response:
            buildable, build_time = self._convert_sparse_continuous_into_tensor(response['buildable'])

        try:
            if "collision" in response:
                collision_mask = self._collision_mask(response['collision'])
        except IndexError as e:
            raise Exception("Cannot move further", str(e.args))

        if 'statistics' in response:
            statistics = response['statistics']

        if 'score' in response:
            score = response['score']
        # if 'objective' in response:
        #    objective, obj_time = await self._convert_sparse_continuous_into_tensor(response['objective'])

        observation = {
            "local": self.grid_world,
            "minimap": self.minimaps,  # Do not do this during observation - it is expensive!
            "compass": np.stack([points_x, points_y], axis=1),
            "buildable": buildable,
            "collision_mask": collision_mask,
            "statistics": statistics,
            "score": score
        }
        self.last_observation = observation

        return observation

    def observe_statistics(self):
        """
        At each time t, statistics on the factory are returned
        :return:
        """
        response, execution_time = self._send('observe_performance', PLAYER)
        return response, execution_time

    def observe_position(self):
        """
        At each time t, the agent receives the agent’s current absolute position p.
        :return:
        """
        return self._send('observe_position', PLAYER)

    def observe_nearest_points_of_interest(self):
        """
        At each time t, the agent receives the positions of the nearest points of interest.
        :return:
        """
        return self._send('observe_points_of_interest', PLAYER, 200)

    def _convert_sparse_continuous_into_tensor(self, local_counts: dict, init=0):
        start = timer()
        one_hot = np.full((256), init)  # zeros(256)

        for key, value in local_counts.items():
            index = self.vocabulary._update_vocabulary(key)
            one_hot[index] = value

        return np.reshape(one_hot, one_hot.shape + (1,)), timer() - start

    def _convert_sparse_coordinates_into_tensors(self, local_counts: dict):
        start = timer()
        one_hot_x = zeros(256)
        one_hot_y = zeros(256)

        for key, value in local_counts.items():
            lua_key = key.replace('_', '-')
            index = self.vocabulary._update_vocabulary(lua_key)
            one_hot_x[index] = value['x']
            one_hot_y[index] = value['y']
        end = timer() - start
        return np.reshape(one_hot_x, one_hot_x.shape + (1,)), np.reshape(one_hot_y, one_hot_y.shape + (1,)), end

    def _convert_sparse_local_into_gridworld(self, local_environment_sparse, new_field_x, new_field_y):
        # print(new_field_x, new_field_y)
        new_field_x = new_field_y = False
        range_x = math.floor(new_field_x) if new_field_x else self.bounding_box
        range_y = math.floor(abs(new_field_y)) if new_field_y else self.bounding_box

        try:
            local_environment_dense, elapsed = self._get_dense_environment(range_x, range_y, local_environment_sparse)
        except IndexError as e:
            pass

        y, x = np.where(local_environment_dense == -2)

        new_field_y = new_field_y = False
        # If moving vertically
        if new_field_y and not new_field_x:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, self.bounding_box))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (0, new_field_y))
        # If moving horizontally
        elif new_field_x and not new_field_y:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, self.bounding_box))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (new_field_x, 0))
        else:
            self.grid_world = np.reshape(local_environment_dense, (range_x, range_y))

        # plt.imshow(np.array(self.grid_world, dtype="float"), cmap='gray', interpolation='nearest')
        # plt.show()

    def _sample_chunk_from_normal(self, player_offset):
        normal = self.minimap_normal[self.chunk_cursor % MAX_SAMPLES]
        offset = normal + player_offset
        self.chunk_cursor += 1
        return offset // CHUNK_SIZE

    def _sample_chunk(self):
        x = self._sample_chunk_from_normal(self.player_location[0])
        y = self._sample_chunk_from_normal(self.player_location[1])
        index_x = x + int(self.minimap_bounding_box / 2)
        index_y = y + int(self.minimap_bounding_box / 2)

        return int(x), int(y), int(index_x), int(index_y)

    def _index_chunk(self, chunk_map, index_x, index_y):
        if not chunk_map:
            raise Exception("Anonymous error from the server")

        if index_x >= self.minimap_bounding_box or index_y >= self.minimap_bounding_box or index_x < 0 or index_y < 0:
            return 0
        for type, count in chunk_map.items():
            if count == 0:
                continue
            self.minimaps[self._get_type_index(type)][index_x, index_y] = count
        return chunk_map

    def _get_type_index(self, type):
        return FIELDS.index(type)

    def _get_dense_environment(self, range_x, range_y, local_environment_sparse):
        local_environment_dense = []
        start = timer()

        dense_array = np.full((range_y, range_x), -1, dtype=object)

        # Populate the dense array using the sparse dictionary
        for key, value in local_environment_sparse.items():
            if key > range_y * range_x:
                break

            row = math.floor(key // range_y)
            col = math.floor(key % range_y)
            if row >= self.bounding_box or col >= self.bounding_box or row < 0 or col < 0:
                continue
            dense_array[row, col] = self.vocabulary._update_vocabulary(value)
        end = timer()
        diff = (end - start)

        return dense_array, diff

    def _move(self, direction: int):
        return self._send('move',
                          PLAYER,
                          direction,
                          self.trail_state['trail_entity'])

    def _collision_mask(self, sparse_collision_mask):

        dense_array = np.full((self.bounding_box, self.bounding_box), 1, dtype=object)

        # Populate the dense array using the sparse dictionary
        for key, value in sparse_collision_mask.items():
            # key = key - (self.bounding_box)*(self.bounding_box/2)
            col = math.floor((key // self.bounding_box)) - self.player_location[1]
            row = math.floor((key % self.bounding_box)) - self.player_location[0]
            d = self.player_location
            if row >= self.bounding_box or col >= self.bounding_box or col <= 0 or row <= 0:
                pass
            try:
                dense_array[col, row] = value
            except Exception as e:
                pass

        # plt.imshow(np.array(dense_array, dtype="float"), cmap='gray', interpolation='nearest')
        # plt.show()
        # dense_array = np.flipud(dense_array)
        self.collision_mask = dense_array
        return dense_array

    def move(self, x: int, y: int, trailing=None, leading=None) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        self.last_location = self.player_location
        if trailing:
            response, execution_time = self._send('move',
                                                  PLAYER,
                                                  x,
                                                  y,
                                                  trailing,
                                                  1)
            # if new_position is 0:
            #    self.trail(None)
        elif leading:
            response, execution_time = self._send('move',
                                                  PLAYER,
                                                  x,
                                                  y,
                                                  leading,
                                                  0)
        else:
            response, execution_time = self._send('move',
                                                  PLAYER,
                                                  x,
                                                  y,
                                                  NONE,
                                                  NONE)

        if isinstance(response, int) and response == 0:
            raise Exception("Could not move.")

        if response == 'trailing' or response == 'leading':
            raise Exception("Could not lay entity, perhaps a typo?")
        if response:
            self.player_location = (response['x'], response['y'])
            # self.last_direction = direction
            self.movement_vector = (self.player_location[0] - self.last_location[0],
                                    self.player_location[1] - self.last_location[1])

            self.last_observed_player_location = (self.last_observed_player_location[0] + self.movement_vector[0],
                                                  self.last_observed_player_location[1] + self.movement_vector[1])
        return response, execution_time
