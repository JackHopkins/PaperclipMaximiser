from typing import Tuple

from controllers._action import Action
from factorio_instance import PLAYER
from factorio_types import Prototype


class ExtractItem(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, entity: Prototype, source_position: Tuple[int, int], quantity=5, relative=False) -> int:
        x, y = self.get_position(source_position)
        name, _ = entity

        if not relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(
                                       PLAYER,
                                       name,
                                       quantity,
                                       x,
                                       y)
        if response != 1:
            raise Exception("Could not extract.", response)

        return True
