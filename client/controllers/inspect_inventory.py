from typing import Tuple

from controllers._action import Action
from factorio_entities import Inventory
from factorio_instance import PLAYER


class InspectInventory(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, entity=None) -> Inventory:
        if entity:
            x, y = self.get_position(entity.position)
        else:
            x, y = 0, 0
        response, execution_time = self.execute(PLAYER, entity == None, x, y)
        return Inventory(**response)
