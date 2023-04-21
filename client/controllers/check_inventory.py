from typing import Tuple

from controllers._action import Action
from factorio_instance import PLAYER
from models.zero_dict import ZeroDict


class CheckInventory(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self) -> dict:
        response, execution_time = self.execute(PLAYER)
        return ZeroDict(**response)
