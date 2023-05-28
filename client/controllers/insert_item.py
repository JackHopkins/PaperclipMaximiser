from typing import Tuple

from controllers._action import Action
from factorio_entities import Entity
from factorio_instance import PLAYER
from factorio_types import Prototype


class InsertItem(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, entity: Prototype, target: Entity, quantity=5) -> int:
        x, y = self.get_position(target.position)
        name, _ = entity

        response, elapsed = self.execute(
                                       PLAYER,
                                       name,
                                       quantity,
                                       x,
                                       y)

        if response != {} and response != 1:
            raise Exception("Could not insert", response)

        return True
