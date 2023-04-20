from controllers._action import Action
from factorio_instance import PLAYER, NONE


class Move(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, x: int, y: int, trailing=None, leading=None) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        last_location = self.game_state.player_location
        if trailing:
            response, execution_time = self._send('move', PLAYER, x, y, trailing, 1)
        elif leading:
            response, execution_time = self._send('move', PLAYER, x, y, leading, 0)
        else:
            response, execution_time = self._send('move', PLAYER, x, y, NONE, NONE)

        if isinstance(response, int) and response == 0:
            raise Exception("Could not move.")

        if response == 'trailing' or response == 'leading':
            raise Exception("Could not lay entity, perhaps a typo?")

        if response:
            self.player_location = (response['x'], response['y'])
            movement_vector = (self.game_state.player_location[0] - last_location[0],
                                    self.game_state.player_location[1] - last_location[1])

            self.last_observed_player_location = (self.game_state.last_observed_player_location[0] + movement_vector[0],
                                                  self.game_state.last_observed_player_location[1] + movement_vector[1])
        return response, execution_time
