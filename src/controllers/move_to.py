import math
from time import sleep

from controllers._action import Action
from controllers.get_path import GetPath
from controllers.observe_all import ObserveAll
from controllers.request_path import RequestPath
from factorio_entities import Position
from factorio_instance import PLAYER, NONE
from factorio_types import Prototype


class MoveTo(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.observe = ObserveAll(connection, game_state)
        self.request_path = RequestPath(connection, game_state)
        self.get_path = GetPath(connection, game_state)

    def __call__(self, position: Position, laying: Prototype = None, leading: Prototype = None) -> bool:
        """
        Move to a position.
        :param position: Position to move to.
        :param laying: Entity to lay down behind you as you move. e.g. 'Prototype.TransportBelt', facing away from you.
        :param leading: Entity to lay down in front of you as you move. e.g. 'Prototype.TransportBelt', facing towards you.
        :example move_to(nearest(Prototype.StoneFurnace), laying=Prototype.TransportBelt)
        :return:
        """
        X_OFFSET, Y_OFFSET = 0.5, 0

        x, y = math.floor(position.x*4)/4 + X_OFFSET, math.floor(position.y*4)/4 + Y_OFFSET
        nposition = Position(x=x, y=y)
        print(f"Moving to {x}, {y}")
        path_handle = self.request_path(start=Position(x=self.game_state.player_location[0],
                                                       y=self.game_state.player_location[1]), finish=nposition,
                                        allow_paths_through_own_entities=True)
        try:
            if laying is not None:
                entity_name = laying.value[0]
                response, execution_time = self.execute(PLAYER, path_handle, entity_name, 1)
            elif leading:
                entity_name = leading.value[0]
                response, execution_time = self.execute(PLAYER, path_handle, entity_name, 0)
            else:
                response, execution_time = self.execute(PLAYER, path_handle, NONE, NONE)

            if isinstance(response, int) and response == 0:
                raise Exception("Could not move.")

            if response == 'trailing' or response == 'leading':
                raise Exception("Could not lay entity, perhaps a typo?")

            if response and isinstance(response, dict):
                self.game_state.player_location = (response['x'], response['y'])

            # If `fast` is turned off - we need to long poll the game state to ensure the player has moved
            if not self.game_state.fast:
                remaining_steps = self.connection.send_command(f'/c rcon.print(global.actions.get_queue_length({PLAYER}))')
                while remaining_steps != '0':
                    sleep(0.5)
                    remaining_steps = self.connection.send_command(f'/c rcon.print(global.actions.get_queue_length({PLAYER}))')

            return response#, execution_time
        except Exception as e:
            raise Exception(f"Cannot move. {e}")
