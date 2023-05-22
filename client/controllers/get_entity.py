from typing import Tuple

from controllers._action import Action
from factorio_entities import Position

from factorio_instance import PLAYER
from factorio_types import Prototype


class GetEntity(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, entity: Prototype, position: Position, relative=False) -> dict:
        if isinstance(position, tuple):
            x, y = position
        else:
            x = position.x
            y = position.y

        name, metaclass = entity
        if relative:
            x += self.game_state.last_observed_player_location[0]
            y += self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, name, x, y)

        if response is None or response == {}:
            raise Exception("Could not get entity, does it exist at the specified position?", response)

        for key, value in response.items():
            if isinstance(value, dict):
                if 1 in value.keys():
                    response[key] = []
                    for sub_key, sub_value in value.items():
                        response[key].append(sub_value)

        try:
            object = metaclass(**response)
        except Exception as e:
            raise Exception(f"Could not create {name} object from response: {response}", e)
        return object
