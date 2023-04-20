import os
import sys
import time
from typing import List

from slpp import slpp as lua
from timeit import default_timer as timer
from factorio_rcon_utils import _lua2python, _load_action


class Action:

    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        self.name = self.camel_to_snake(self.__class__.__name__)
        #self.load()

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
        self.connection.send_command('/c '+script)

    def _get_command(self, command, parameters=[], measured=True):
        prefix = "/c " if not measured else '/command '
        if command in self.script_dict:
            script = prefix + self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command
        return script

    def execute(self, *args):
        start = time.time()
        parameters = [lua.encode(arg) for arg in args]
        invocation = f"pcall(global.actions.{self.name} {',' if parameters else '' + ','.join(parameters)})"
        wrapped = f"/c rcon.print({invocation})"
        lua_response = self.connection.send_command(wrapped)
        return _lua2python(invocation, lua_response, start=start)

    def _send(self, command, *parameters, trace=False) -> List[str]:
        start = timer()
        script = self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = self.connection.send_command(script)
        # print(lua_response)
        return _lua2python(command, lua_response, start=start)

