from controllers._action import Action
from typing import Tuple

from factorio_entities import Position, Entity
from factorio_instance import PLAYER


class RotateEntity(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, entity: Entity, direction=1, relative: bool = False) -> bool:
        x, y = self.get_position(entity.position)
        name, metaclass, *a = entity

        if relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        if direction == 3:
            dir = 3
        elif direction == 1:
            dir = 2
        elif direction == 2:
            dir = 3
        elif direction == 0:
            dir = 1
        response, elapsed = self.execute(PLAYER, x, y, dir)
        if not response:
            raise Exception("Could not rotate.", response)

        response_direction = response["direction"] / 2
        if response_direction == 1:
            entity.direction = 3
        elif response_direction == 2:
            entity.direction = 1
        elif response_direction == 3:
            entity.direction = 2
        elif response_direction == 0:
            entity.direction = 0

        return entity
