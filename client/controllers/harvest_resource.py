from typing import Tuple

from controllers._action import Action
from factorio_instance import PLAYER


class HarvestResource(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, position: Tuple[int, int], quantity=1, relative: bool = False, **kwargs) -> bool:
        x, y = position

        if not relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, x, y, quantity)
        if response != {} and response != 1:
            raise Exception("Could not harvest.", response)
        return response
