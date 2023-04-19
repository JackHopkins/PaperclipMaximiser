from controllers.action import Action
from typing import Tuple

from factorio_instance import PLAYER


class ConnectEntities(Action):

    def __init__(self, connection, last_observed_player_location = (0,0)):
        Action.__init__(self, connection)
        self.last_observed_player_location = last_observed_player_location

    def __call__(self, source_position: Tuple = (0, 0), target_position: Tuple = (0, 0),
                 connection_type='burner-inserter', relative=False):

        source_x, source_y = source_position
        target_x, target_y = target_position

        if relative:
            source_x -= self.last_observed_player_location[0]
            target_x -= self.last_observed_player_location[0]
            source_y -= self.last_observed_player_location[1]
            target_y -= self.last_observed_player_location[1]

        response, elapsed = self._send('connect_entities',
                                       PLAYER,
                                       source_x,
                                       source_y,
                                       target_x,
                                       target_y,
                                       connection_type)
        if response != 1:
            raise Exception(f"Could not connect {(source_x, source_y)} to {(target_x, target_y)}.", response)
        return True