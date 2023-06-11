from controllers._action import Action
from typing import Optional, Tuple

from factorio_entities import Position, Entity
from factorio_instance import PLAYER
from factorio_types import Prototype


class PlaceEntity(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self,
                 entity: Prototype,
                 direction=0,
                 position: Position = Position(x=0, y=0),
                 exact: bool = False,
                 relative=False) -> Entity:
        x, y = self.get_position(position)
        name, metaclass, *a = entity

        if direction > 3 or direction < 0:
            raise Exception("Directions are between 0-3")

        if relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        if exact:
            pass

        response, elapsed = self.execute(
                                       PLAYER,
                                       name,
                                       direction + 1,
                                       x,
                                       y,
                                       exact
                                       )
        if exact:
            pass
        if not isinstance(response, dict):
            message = response.split(":")[-1]
            raise Exception(f"Could not place {name} at ({x}, {y})", message.lstrip())

        cleaned_response = {}
        for key, value in response.items():
            if isinstance(value, dict):
                if not value:
                    continue
                if 1 in value.keys():
                    cleaned_response[key] = []
                    for sub_key, sub_value in value.items():
                        cleaned_response[key].append(sub_value)
                else:
                    cleaned_response[key] = value
            else:
                cleaned_response[key] = value

        try:
            object = metaclass(**cleaned_response)
        except Exception as e:
            raise Exception(f"Could not create {name} object from response: {cleaned_response}", e)
        return object
