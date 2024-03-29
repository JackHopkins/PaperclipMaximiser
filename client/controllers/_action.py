import os
import sys
import time
from typing import List, Tuple, Dict, Any, Union

from slpp import slpp as lua
from timeit import default_timer as timer

from factorio_entities import Position, Entity
from factorio_rcon_utils import _lua2python, _load_action

COMMAND = "/silent-command"

class Action:

    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        self.name = self.camel_to_snake(self.__class__.__name__)
        self.load()

    def get_position(self, position_or_entity: Union[Tuple, Position, Entity]):
        if isinstance(position_or_entity, tuple):
            x, y = position_or_entity
        elif isinstance(position_or_entity, Entity):
            x = position_or_entity.position.x
            y = position_or_entity.position.y
        else:
            x = position_or_entity.x
            y = position_or_entity.y

        return x, y

    def camel_to_snake(self, camel_str):
        snake_str = ""
        for index, char in enumerate(camel_str):
            if char.isupper():
                if index != 0:
                    snake_str += "_"
                snake_str += char.lower()
            else:
                snake_str += char
        return snake_str

    def load(self):
        script = _load_action(self.name)
        if not script:
            raise Exception(f"Could not load {self.name}")
        self.connection.send_command(f'{COMMAND} '+script)

    def _get_command(self, command, parameters=[], measured=True):
        if command in self.script_dict:
            script = f'{COMMAND} '+ self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command
        return script

    def execute(self, *args) -> Tuple[Dict, Any]:
        try:
            start = time.time()
            parameters = [lua.encode(arg) for arg in args]
            invocation = f"pcall(global.actions.{self.name}{(', ' if parameters else '') + ','.join(parameters)})"
            wrapped = f"{COMMAND} a, b = {invocation}; rcon.print(dump({{a=a, b=b}}))"
            lua_response = self.connection.send_command(wrapped)
            parsed, elapsed = _lua2python(invocation, lua_response, start=start)
            if not parsed['a'] and 'b' in parsed and isinstance(parsed['b'], str):
                parsed['b'] = parsed['b'].replace("!!", "\"")
            if not 'b' in parsed:
                return {}, elapsed
        except Exception as e:
            return None, -1
        return parsed['b'], elapsed

    def send(self, command, *parameters, trace=False) -> List[str]:
        start = timer()
        script = self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = self.connection.send_command(script)
        # print(lua_response)
        return _lua2python(command, lua_response, start=start)

