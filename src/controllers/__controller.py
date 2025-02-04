import time
from timeit import default_timer as timer
from typing import List, Tuple, Dict, Any

from slpp import slpp as lua, ParseError

from factorio_entities import EntityStatus, Direction
from factorio_lua_script_manager import FactorioLuaScriptManager
from factorio_namespace import FactorioNamespace
from factorio_rcon_utils import _lua2python

COMMAND = "/silent-command"

class Controller:

    def __init__(self, lua_script_manager: 'FactorioLuaScriptManager', game_state: 'FactorioNamespace', *args, **kwargs):
        assert isinstance(lua_script_manager, FactorioLuaScriptManager), "Not correct"
        self.connection = lua_script_manager
        self.game_state = game_state
        self.name = self.camel_to_snake(self.__class__.__name__)
        self.lua_script_manager = lua_script_manager

    def clean_response(self, response):
        def is_lua_list(d):
            """Check if dictionary represents a Lua-style list (keys are consecutive numbers from 1)"""
            if not isinstance(d, dict) or not d:
                return False
            keys = set(str(k) for k in d.keys())
            return all(str(i) in keys for i in range(1, len(d) + 1))

        def clean_value(value):
            """Recursively clean a value"""
            if isinstance(value, dict):
                # Handle Lua-style lists
                if is_lua_list(value):
                    # Sort by numeric key and take only the values
                    sorted_items = sorted(value.items(), key=lambda x: int(str(x[0])))
                    return [clean_value(v) for k, v in sorted_items]

                # Handle inventory special case
                if any(isinstance(k, int) for k in value.keys()) and \
                        all(isinstance(v, dict) and 'name' in v and 'count' in v for v in value.values()):
                    cleaned_dict = {}
                    for v in value.values():
                        cleaned_dict[v['name']] = v['count']
                    return cleaned_dict

                # Regular dictionary
                return {k: clean_value(v) for k, v in value.items()}

            elif isinstance(value, list):
                return [clean_value(v) for v in value]

            return value

        cleaned_response = {}



        if not hasattr(response, 'items'):
            pass

        for key, value in response.items():
            if key == 'status' and isinstance(value, str):
                cleaned_response[key] = EntityStatus.from_string(value)
            elif key == 'direction' and isinstance(value, str):
                cleaned_response[key] = Direction.from_string(value)
            elif not value and key == 'warnings':
                cleaned_response[key] = []
            else:
                cleaned_response[key] = clean_value(value)

        return cleaned_response

    # def clean_response_deprecated(self, response):
    #     cleaned_response = {}
    #     for key, value in response.items():
    #         if key == 'status' and isinstance(value, str):
    #             cleaned_response[key] = EntityStatus.from_string(value)
    #             continue
    #         # We handle warnings separately, as they are not always present and should be an empty list rather than
    #         # an empty dict
    #         if not value and key == 'warnings':
    #             cleaned_response[key] = []
    #             continue
    #         if isinstance(value, dict):
    #             if 1 in value.keys():
    #                 if 'inventory' in key:
    #                     cleaned_response[key] = {}
    #                     values = list(value.values())
    #                     for val in values:
    #                         cleaned_response[key][val['name']] = val['count']
    #                 else:
    #                     cleaned_response[key] = []
    #                     for sub_key, sub_value in value.items():
    #                         cleaned_response[key].append(sub_value)
    #             else:
    #                 cleaned_response[key] = value
    #         else:
    #             cleaned_response[key] = value
    #     return cleaned_response

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


    def _get_command(self, command, parameters=[], measured=True):
        if command in self.script_dict:
            script = f'{COMMAND} '+ self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command
        return script

    def execute(self, *args) -> Tuple[Dict, Any]:
        lua_response = ""
        try:
            start = time.time()
            parameters = [lua.encode(arg) for arg in args]
            invocation = f"pcall(global.actions.{self.name}{(', ' if parameters else '') + ','.join(parameters)})"
            wrapped = f"{COMMAND} a, b = {invocation}; rcon.print(dump({{a=a, b=b}}))"
            lua_response = self.connection.rcon_client.send_command(wrapped)
            parsed, elapsed = _lua2python(invocation, lua_response, start=start)
            if not parsed['a'] and 'b' in parsed and isinstance(parsed['b'], str):
                parts = lua_response.split("[\"b\"] = ")
                parts[1] = f"{parts[1][:-2]}" if parts[1][-1] == "}" else parts[1]
                parsed['b'] = parts[1].replace("!!", "\"")
            if not 'b' in parsed:
                return {}, elapsed
        except ParseError as e:
            # If a non-string gets passed back from the Lua script, it will raise a ParseError
            # Split by `["b"] = ` and take the second part, which is the returned value
            try:
                parts = lua_response.split('["b"] = ')
                return parts[1][:-2], -1
            except IndexError:
                return e.args[0], -1
            return lua_response, -1
        except TypeError as e:
            return lua_response, -1
        except Exception as e:
            return lua_response, -1
        return parsed['b'], elapsed

    def send(self, command, *parameters, trace=False) -> List[str]:
        start = timer()
        script = self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = self.connection.send_command(script)
        # print(lua_response)
        return _lua2python(command, lua_response, start=start)

