from controllers._action import Action
from typing import Tuple

from factorio_entities import Position
from factorio_instance import PLAYER
from factorio_types import Prototype


class PickupEntity(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, entity: Prototype, position: Position, relative=False) -> bool:
        x, y = self.get_position(position)
        name, _ = entity

        if relative:
            x += self.game_state.last_observed_player_location[0]
            y += self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, x, y, name)
        if response != 1 and response != {}:
            raise Exception("Could not pickup, did you intend to harvest?", response)
        return True
