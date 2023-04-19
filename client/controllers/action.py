import os
import sys
from typing import List

from slpp import slpp as lua
from timeit import default_timer as timer
from factorio_rcon_utils import _lua2python, _load_action


class Action:

    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        self.name = sys.modules[self.__module__].__file__.split("/")[-1].replace(".py", ".lua")

    def load(self):
        script = _load_action(self.name)
        self.connection.send_command(script)

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
        lua_response = self.connection.send_command(script)
        # print(lua_response)
        return _lua2python(command, lua_response, start=start)

