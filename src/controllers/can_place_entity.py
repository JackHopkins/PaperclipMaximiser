from controllers.__action import Action
from typing import Optional, Tuple

from factorio_entities import Position, Entity
from factorio_instance import PLAYER, Direction
from factorio_types import Prototype


class CanPlaceEntity(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self,
                 entity: Prototype,
                 direction: Direction = Direction.UP,
                 position: Position = Position(x=0, y=0),
                 ) -> bool:
        """
        Tests to see if an entity can be placed at a given position
        :param entity: Entity to place from inventory
        :param direction: Cardinal direction to place entity
        :param position: Position to place entity
        :return: True if entity can be placed at position, else False
        """

        assert isinstance(entity, Prototype)
        assert isinstance(direction, Direction)

        # If position is a tuple, cast it to a Position object:
        if isinstance(position, tuple):
            position = Position(x=position[0], y=position[1])

        assert isinstance(position, Position)

        x, y = self.get_position(position)
        name, metaclass = entity.value

        response, elapsed = self.execute(PLAYER, name, direction.value + 1, x, y)

        if not isinstance(response, dict):
            if isinstance(response, bool):
                return response
            if isinstance(response, str) and "cannot" in response.lower():
                return False
        return True
