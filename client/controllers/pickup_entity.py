from controllers._action import Action
from typing import Tuple

from factorio_instance import PLAYER


class PickupEntity(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, name: str, position: Tuple[int, int], relative=False) -> bool:
        x, y = position

        if relative:
            x += self.game_state.last_observed_player_location[0]
            y += self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, x, y, name)
        if response != 1 and response != {}:
            raise Exception("Could not pickup, did you intend to harvest?", response)
        return True
