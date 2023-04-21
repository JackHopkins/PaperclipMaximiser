from typing import Optional, Tuple

from controllers._action import Action
from factorio_instance import PLAYER, NONE
from utilities.pathfinding import get_path


class MoveTo(Action):

    def __init__(self, connection, game_state):
        self.game_state = game_state
        super().__init__(connection, game_state)

    def _move(self, x: int, y: int, laying=None, leading=None) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        last_location = self.game_state.player_location
        if laying:
            response, execution_time = self.execute(PLAYER, x, y, laying, 1)
        elif leading:
            response, execution_time = self.execute(PLAYER, x, y, leading, 0)
        else:
            response, execution_time = self.execute(PLAYER, x, y, NONE, NONE)

        if isinstance(response, int) and response == 0:
            raise Exception("Could not move.")

        if response == 'trailing' or response == 'leading':
            raise Exception("Could not lay entity, perhaps a typo?")

        if response:
            self.game_state.player_location = (response['x'], response['y'])
            movement_vector = (self.game_state.player_location[0] - last_location[0],
                                    self.game_state.player_location[1] - last_location[1])

            self.last_observed_player_location = (self.game_state.last_observed_player_location[0] + movement_vector[0],
                                                  self.game_state.last_observed_player_location[1] + movement_vector[1])
        return response, execution_time

    def __call__(self,
                 absolute_position: Optional[Tuple[int, int]],
                 relative_position: Tuple[int, int] = (0, 0),
                 laying=None,
                 leading=None,
                 **kwargs):
        try:
            if absolute_position is not None:
                if not isinstance(absolute_position, Tuple):
                    raise Exception(
                        "You need to pass in a tuple like (x, y) for the absolute position. You passed in scalar.")
                start_x, start_y = self.game_state.player_location
                relative_position = (absolute_position[0] - start_x, absolute_position[1] - start_y)

            if not isinstance(relative_position, Tuple):
                raise Exception("You need to pass in a tuple like (x, y). You passed in scalar.")



            relative_end_x, relative_end_y = relative_position
            start_x, start_y = self.game_state.player_location
            offset_x = self.game_state.bounding_box // 2
            offset_y = self.game_state.bounding_box // 2
            last_observed_x = self.game_state.last_observed_player_location[0]
            last_observed_y = self.game_state.last_observed_player_location[1]

            end = (offset_x + relative_end_x,  # - last_observed_x,
                   offset_y + relative_end_y)  # - last_observed_y)

            path = get_path(end, self.game_state.collision_mask, start=(offset_x, offset_y))

            def direction_from_step(step, laying=None, leading=None):
                offset = self.game_state.bounding_box // 2
                return self._move(*((step - [offset, offset]) - self.game_state.player_location), laying=laying,
                                 leading=leading)

            task_queue = []
            task_queue.extend(
                [(lambda s: direction_from_step(s + (start_x, start_y), laying=laying, leading=leading))(s) for s in
                 path])
            #task_queue.extend([(lambda: self.observe())()])

            #self.tasks.append(iter(task_queue))
        except Exception as e:
            raise Exception("Could not move_to", e)
