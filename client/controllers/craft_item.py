from controllers._action import Action
from factorio_instance import PLAYER


class CraftItem(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, entity: str, quantity: int = 1) -> bool:
        """
        The agent places an entity e at local position (x, y) if the agent has
        enough resources. If the agent chooses to place an empty entity at (x, y), any entity at
        (x, y) is removed. If the agent chooses to place an entity where there is already one,
        the previous entity is first removed and the new entity replaces it.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param entity: Entity to place from inventory
        :param direction: Cardinal direction to place entity
        :return: True if action carried out, False if no-op
        """
        success, elapsed = self.execute(PLAYER, entity.replace("_", "-"), quantity)
        if success != {} and success != 1:
            if success is None:
                raise Exception(f"Could not craft a {entity}", "Ingredients cannot be crafted by hand.")
            else:
                raise Exception(f"Could not craft a {entity}", success)
        return "Crafting successful"
