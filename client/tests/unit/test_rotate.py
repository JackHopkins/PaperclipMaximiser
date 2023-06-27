import pytest

from factorio_types import Prototype

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

def test_rotate_entity(game):
    # Place a transport belt
    transport_belt = game.place_entity(Prototype.TransportBelt, position=(0, 0), direction=game.UP)

    # Rotate the transport belt right
    game.rotate_entity(transport_belt, direction=game.RIGHT)

    # Assert that the direction of the transport belt has been updated
    assert transport_belt.direction == game.RIGHT

    game.rotate_entity(transport_belt, direction=game.DOWN)

    assert transport_belt.direction == game.DOWN

    game.rotate_entity(transport_belt, direction=game.LEFT)

    assert transport_belt.direction == game.LEFT

    game.rotate_entity(transport_belt, direction=game.UP)

    assert transport_belt.direction == game.UP

    game.reset()