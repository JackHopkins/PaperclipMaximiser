from typing import Tuple

from controllers._action import Action
from factorio_instance import PLAYER


class InsertItem(Action):

    def __init__(self, *args):
        Action.__init__(self, *args)

    def __call__(self, entity: str, target_position: Tuple[int, int] = (0, 0), quantity=5) -> int:
        x, y = target_position

        response, elapsed = self._send('insert',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       quantity,
                                       x,
                                       y)
        if response != 1:
            raise Exception("Could not insert", response)

        return True
