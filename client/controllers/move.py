from controllers.action import Action
from factorio_instance import PLAYER, NONE


class Move(Action):

    def __init__(self, connection):
        Action.__init__(self, connection)

    def __call__(self, x: int, y: int, trailing=None, leading=None) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        self.last_location = self.player_location
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
            self.movement_vector = (self.player_location[0] - self.last_location[0],
                                    self.player_location[1] - self.last_location[1])

            self.last_observed_player_location = (self.last_observed_player_location[0] + self.movement_vector[0],
                                                  self.last_observed_player_location[1] + self.movement_vector[1])
        return response, execution_time
