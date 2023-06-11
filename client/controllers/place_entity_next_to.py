from controllers._action import Action
from typing import Tuple

from factorio_entities import Position, Entity
from factorio_instance import PLAYER
from factorio_types import Prototype


class PlaceEntityNextTo(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self,
                 entity: Entity,
                 reference_position: Position = Position(x=0, y=0),
                 direction_from: int = 1,
                 spacing: int = 0,
                 relative=False) -> Entity:

        name, metaclass = entity
        x, y = reference_position.x, reference_position.y

        if relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, name, x, y, direction_from+1, spacing-0.5)

        if not isinstance(response, dict) or response == {}:
            raise Exception(f"Could not place {name} at {reference_position}.", response)

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
