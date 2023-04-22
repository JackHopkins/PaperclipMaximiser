from typing import Tuple

from controllers._action import Action
from factorio_instance import PLAYER


class InsertItem(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, entity: str, target_position: Tuple[int, int] = (0, 0), quantity=5) -> int:
        x, y = target_position

        response, elapsed = self.execute(
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       quantity,
                                       x,
                                       y)
        if response != {} and response != 1:
            raise Exception("Could not insert", response)

        return True
