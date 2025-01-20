import time

from controllers.__action import Action
from factorio_entities import Position
from factorio_instance import PLAYER


class RequestPath(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)

    def __call__(self, start: Position, finish: Position, max_attempts: int = 10, allow_paths_through_own_entities=False, radius=0) -> int:
        """
        Asynchronously request a path from start to finish from the game.
        """
        assert isinstance(start, Position)
        assert isinstance(finish, Position)

        try:
            start_x, start_y = self.get_position(start)
            goal_x, goal_y = finish.x, finish.y


            walltime_start = time.time()
            response, elapsed = self.execute(PLAYER, start_x, start_y, goal_x, goal_y, radius, allow_paths_through_own_entities)

            if response is None or response == {} or isinstance(response, str):
                raise Exception("Could not request path", response)

            path_handle = int(response)

            return path_handle

        except Exception as e:
            raise Exception(f"Could not get path from {start} to {finish}", e)