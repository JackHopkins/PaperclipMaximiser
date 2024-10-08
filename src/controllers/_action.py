import os
import sys
import time
from typing import List, Tuple, Dict, Any, Union

from slpp import slpp as lua, ParseError
from timeit import default_timer as timer

from controllers._controller import Controller
from factorio_entities import Position, Entity


class Action(Controller):

    def __init__(self, lua_script_manager: 'FactorioLuaScriptManager', game_state: 'FactorioInstance', *args, **kwargs):
        super().__init__(lua_script_manager, game_state)
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

    def load(self):
        self.lua_script_manager.load_action_into_game(self.name)
        # script = _load_action(self.name)
        # if not script:
        #     raise Exception(f"Could not load {self.name}")
        # self.connection.send_command(f'{COMMAND} '+script)
