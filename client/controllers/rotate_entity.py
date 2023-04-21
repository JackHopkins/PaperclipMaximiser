from controllers._action import Action
from typing import Tuple

from factorio_instance import PLAYER


class RotateEntity(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, position: Tuple[int, int], direction=1, relative: bool = False) -> bool:
        x, y = position

        if not relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, x, y, direction)
        if not response:
            raise Exception("Could not rotate.", response)
        return True
