import os

from dotenv import load_dotenv

from client.factorio_client import FactorioClient

load_dotenv()

factorio_client = FactorioClient(remote_address=os.getenv("REMOTE_ADDRESS"), remote_password="eSei2keed0aegai")

def give(entity:str, count: int) -> bool:
    factorio_client.send('give_item', '1', entity, count)


def interact(x: int, y: int) -> bool:
    """
    If there is an entity at local position (x, y), this action triggers an
    interaction as follows: If the item can be picked up, the agent picks up the item. If the
    item can be harvested, the agent harvests the item (resource). Here, the local position
    is the (x, y) position relative to the agent as the origin (0, 0). If there is no entity at
    (x, y), this action is a no-op.
    :param x: X position relative to the agent as the origin (0).
    :param y: Y position relative to the agent as the origin (0).
    :return: True if an action happened, False if no-op.
    """
    factorio_client.send('interact', x, y)

    return True


def fuel(amount=5, x: int = 0, y: int = 0) -> int:
    """
    If there is an entity at local position (x, y) that accepts a resource, the agent
    adds a default amount of resource to the entity. If there is no entity at (x, y), this action
    is a no-op.
    :param x: X position relative to the agent as the origin (0).
    :param y: Y position relative to the agent as the origin (0).
    :param amount: Amount of fuel to attempt to deposit
    :return: Amount of fuel deposited
    """
    factorio_client.send('fuel', '1', 'coal', amount)

    return True


def place(entity: str, direction: int, x: int = 0, y: int = 0) -> bool:
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
    cardinals = ['north', 'south', 'east', 'west']
    print(factorio_client.send('place', '1', entity, cardinals[direction]))

    return True


def toggle_placement(entity: str) -> bool:
    """
     The agent toggles placement mode, where an entity $e$ is placed
     at the local position $(x,y)$, and every subsequent position of the agent.
     Trail placement is toggled off once the agent runs out of resources,
     or if it chooses the action a second time with an \emph{empty} entity.
     Trail placement is switched if the agent performs the action again with a different resource.
     :param entity: The entity that is being toggled on.
    :return: Whether the action was carried out.
    """
    factorio_client.send('place', entity)

    return True


def move(direction: int) -> bool:
    """
    The agent moves in a cardinal direction.
    :param direction: Index between (0,3) inclusive.
    :return: Whether the movement was carried out.
    """
    cardinals = ['north', 'south', 'east', 'west']

    factorio_client.send('move', '1', cardinals[direction], 'true')
    factorio_client.send('move', '1', cardinals[direction], 'false')

    return True