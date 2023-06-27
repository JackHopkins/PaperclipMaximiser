from typing import Tuple

from controllers._action import Action
from factorio_entities import Inventory
from factorio_instance import PLAYER
from factorio_types import Prototype, PrototypeName, ResourceName
from models.zero_dict import ZeroDict


class InspectInventory(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, entity=None) -> Inventory:
        response, execution_time = self.execute(PLAYER)
        return Inventory(**response)
