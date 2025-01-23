from typing import Tuple, Union

from controllers.__action import Action
from factorio_entities import Position, Entity
from factorio_instance import PLAYER
from factorio_types import Prototype


class ExtractItem(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        #self.connection = connection
        #self.game_state = game_state

    def __call__(self, entity: Prototype, source: Union[Position, Entity], quantity=5) -> int:
        """
        Extract an item from an entity's inventory at position (x, y) if it exists on the world.
        :param entity: Entity prototype to extract, e.g Prototype.IronPlate
        :param source: Entity or position to extract from
        :param quantity: Quantity to extract
        :example extract_item(Prototype.IronPlate, stone_furnace.position, 5)
        :example extract_item(Prototype.CopperWire, stone_furnace, 5)
        :return The number of items extracted.
        """
        source_name = None
        if isinstance(source, Position):
            x, y = self.get_position(source)

        elif isinstance(source, Entity):
            x, y = self.get_position(source.position)
            source_name = source.name

        name, _ = entity.value

        response, elapsed = self.execute(PLAYER, name, quantity, x, y, source_name)
        if isinstance(response, str):
            msg = self.get_error_message(response)
            if source_name:
                raise Exception(f"Could not extract {name} from {source_name} at ({x}, {y}): {msg}")
            else:
                raise Exception(f"Could not extract {name} at ({x}, {y}): {msg}")

        if not response or response < 1:
            raise Exception("Could not extract.")

        return response
