import math

from controllers._action import Action
from factorio_instance import PLAYER


class Nearest(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, type: str = 'coal', relative: bool = False, **kwargs):
        response, time_elapsed = self.execute(PLAYER, type.replace("_", "-"))

        if not response:
            raise Exception(f"No {type} found on the map")

        if not self.game_state.last_observed_player_location:
            self.game_state.last_observed_player_location = self.game_state.player_location

        if relative:
            return (-math.floor(response['x']) + self.game_state.last_observed_player_location[0],
                    -math.floor(response['y']) + self.game_state.last_observed_player_location[1])
        else:
            return (math.floor(response['x']), math.floor(response['y']))
