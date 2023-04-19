from typing import Tuple

from controllers.action import Action
from factorio_instance import PLAYER


class ExtractItem(Action):

    def __init__(self, connection, last_observed_player_location=(0, 0)):
        Action.__init__(self, connection)
        self.last_observed_player_location = last_observed_player_location

    def __call__(self, entity: str, source_position: Tuple[int, int], quantity=5, relative=False) -> int:
        x, y = source_position

        if not relative:
            x -= self.last_observed_player_location[0]
            y -= self.last_observed_player_location[1]

        response, elapsed = self._send('extract',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       quantity,
                                       x,
                                       y)
        if response != 1:
            raise Exception("Could not extract.", response)

        return True
