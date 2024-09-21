from typing import Tuple

import pydantic

from controllers._action import Action
from factorio_entities import Entity
from factorio_instance import PLAYER
from factorio_types import Prototype


class InsertItem(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
    def __call__(self, entity: Prototype, target: Entity, quantity=5) -> int:
        """
        The agent inserts an item into an target entity's inventory
        :param entity: Entity type to insert from inventory
        :param target: Entity to insert into
        :param quantity: Quantity to insert
        :example: insert_item(Prototype.IronPlate, nearest(Prototype.IronChest), 5)
        :return: The entity inserted into
        """
        assert isinstance(entity, Prototype)
        assert isinstance(target, Entity)

        if quantity > 50:
            raise Exception("Cannot insert more than 50 items at a time")

        x, y = self.get_position(target.position)
        name, _ = entity.value

        response, elapsed = self.execute(PLAYER,
                                         name,
                                         quantity,
                                         x,
                                         y)

        if isinstance(response, str):
            raise Exception("Could not insert", response)

        cleaned_response = self.clean_response(response)

        if isinstance(cleaned_response, dict):
            prototype = Prototype._value2member_map_[(target.name, type(target))]
            target = type(target)(prototype=prototype, **cleaned_response)

        return target
