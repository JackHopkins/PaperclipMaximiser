import pytest

from factorio_types import Resource

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

def test_harvest_resource(game):
    """
    Find the nearest coal resource patch and harvest 5 coal from it.
    :param game:
    :return:
    """
    inventory = game.inspect_inventory()
    # Check initial inventory
    initial_coal = inventory[Resource.Coal]
    # Find nearest coal resource
    nearest_coal = game.nearest(Resource.Coal)
    # Move to the coal resource
    game.move_to(nearest_coal)
    # Harvest coal
    game.harvest_resource(nearest_coal, quantity=5)  # Assuming there is a coal resource at (10, 10)
    # Check the inventory after harvesting
    final_coal = game.inspect_inventory()[Resource.Coal]
    # Assert that the coal has been added to the inventory
    assert initial_coal + 5 == final_coal