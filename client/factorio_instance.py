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

        self.max_sequential_exception_count = 2
        self.sequential_exception_count = 0
        self.actions = _load_actions()

        self.script_dict = {**self.actions, **_load_init()}
        self.vocabulary = vocabulary
        self.initialise(**inventory)

        #self.concat = "global.actions = {}\n\n"
        #for name, script in self.actions.items():
            #self.concat += f"--{name}\n{script}\n-------\n\n"
            #self.rcon_client.send_command("/c " + script)

        self._load_actions(self.rcon_client, self.game_state)
        self.observe_all()
        self.tasks = []

        self.initial_score = self.score()

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
            #rcon_client.send_command('/c global = {}')
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

                if self.sequential_exception_count == self.max_sequential_exception_count:
                    break

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

    def _set_walking(self, walking: bool):
        if walking:
            lua_response = self.rcon_client.send_command(
                '/c game.players[1].character.walking_state = {walking = true, direction = defines.direction.north}')
        else:
            lua_response = self.rcon_client.send_command(
                '/c game.players[1].character.walking_state = {walking = false, direction = defines.direction.north}')
        return lua_response

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

