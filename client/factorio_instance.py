import ast
import concurrent
import importlib
import math
import os
import time
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Tuple, Optional

import numpy as np
from dotenv import load_dotenv
from slpp import slpp as lua

from client.factorio_rcon_utils import _load_actions, _load_init, _lua2python
from client.rcon.factorio_rcon import RCONClient
from models.game_state import GameState
from utilities.pathfinding import get_path
from vocabulary import Vocabulary
CHUNK_SIZE = 32
MAX_SAMPLES = 5000

load_dotenv()

PLAYER = 1
NONE = 'nil'

global var
var = {}


class FactorioInstance:

    def __init__(self, address=None, vocabulary: Vocabulary = None, bounding_box=20, tcp_port=27015, inventory={}):
        self.tcp_port = tcp_port
        self.rcon_client, self.address = self.connect_to_server(address, tcp_port)

        self.game_state = GameState().with_default(vocabulary)

        self.sequential_exception_count = 0
        self.script_dict = {**_load_actions()}#, **_load_init()}
        self.vocabulary = vocabulary

        self._load_actions(self.rcon_client, self.game_state)

        self.tasks = []

        initial_score, _ = self._send('score')
        self.initial_score = initial_score['player']

        mu, sigma = 0, CHUNK_SIZE * 20
        self.minimap_normal = s = np.random.normal(mu, sigma, MAX_SAMPLES)
        self.chunk_cursor = 0
        self.minimaps = self._initialise_minimaps()


        self.initialise(**inventory)

        self.UP = 0
        self.LEFT = 3
        self.RIGHT = 2
        self.DOWN = 1

    def connect_to_server(self, address, tcp_port):
        try:
            rcon_client = RCONClient(address, tcp_port, 'factorio')
            address = address
        except:
            rcon_client = RCONClient('localhost', tcp_port, 'factorio')
            address = 'localhost'

        try:
            rcon_client.connect()
            player_exists = rcon_client.send_command('/c rcon.print(game.players[1].position)')
            if not player_exists:
                raise Exception(
                    "Player hasn't been initialised into the game. Please log in once to make this node operational.")

            rcon_client.send_command('/c global.actions = {}')

        except Exception as e:
            raise ConnectionError(f"Could not connect to {address} at tcp/{tcp_port}: \n{e.args[0]}")

        print(f"Connected to {address} client at tcp/{tcp_port}.")
        return rcon_client, address

    def _load_actions(self, connection, game_state):
        # Define the directory containing the callable class files
        callable_classes_directory = "controllers"

        def snake_to_camel(snake_str):
            return "".join(word.capitalize() for word in snake_str.split("_"))

        # Loop through the files in the directory
        for file in os.listdir(callable_classes_directory):
            # Check if the file is a Python file and does not start with '_'
            if file.endswith(".py") and not file.startswith("_"):
                # Load the module
                module_name = Path(file).stem
                module_spec = importlib.util.spec_from_file_location(module_name,
                                                                     os.path.join(callable_classes_directory, file))
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                class_name = snake_to_camel(module_name)

                # Get the callable class
                callable_class = getattr(module, class_name)

                # Create an instance of the callable class
                try:
                    callable_instance = callable_class(connection, game_state)
                except Exception:
                    raise Exception(f"Could not instantiate {class_name}")
                # Add the instance as a member method
                setattr(self, module_name.lower(), callable_instance)

    def __getitem__(self, key):
        if key not in dir(self) or key.startswith('__'):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

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
        movement_field_x, movement_field_y = self.game_state.movement_vector[0], self.game_state.movement_vector[1]
        omit = kwargs
        response, execution_time = self._send('observe',
                                              PLAYER,
                                              chunk_x,
                                              chunk_y,
                                              self.game_state.bounding_box,
                                              movement_field_x,
                                              movement_field_y,
                                              self.game_state.bounding_box * 2,
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

