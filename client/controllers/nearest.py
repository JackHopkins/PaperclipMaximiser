import math
from typing import Union

from controllers._action import Action
from factorio_entities import Position
from factorio_instance import PLAYER
from factorio_types import Prototype, Resource


class Nearest(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, type: Union[Prototype, Resource], relative: bool = False, **kwargs) -> Position:
        name, metaclass = type

        if not isinstance(name, str):
            raise Exception("'Nearest' must be called with an entity name as the first argument.")

        response, time_elapsed = self.execute(PLAYER, name)

        if response is None or response == {}:
            raise Exception(f"No {type} found on the map")

        if not self.game_state.last_observed_player_location:
            self.game_state.last_observed_player_location = self.game_state.player_location

        if relative:
            x = -math.floor(response['x']) + self.game_state.last_observed_player_location[0]
            y = -math.floor(response['y']) + self.game_state.last_observed_player_location[1]
        else:
            x = math.floor(response['x'])
            y = math.floor(response['y'])

        position = Position(x=x, y=y)

        return position