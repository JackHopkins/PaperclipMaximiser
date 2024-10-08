import pytest

from factorio_instance import Direction
from factorio_types import Prototype

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance
    instance.reset()

def test_rotate_boiler(game):
    # place the boiler next to the offshore pump
    from factorio_entities import Position
    boiler = game.place_entity_next_to(Prototype.Boiler,
                                       reference_position=Position(x=0, y=0),
                                       direction=Direction.RIGHT,
                                       spacing=2)
    # orthogonal direction to the boiler
    orthogonal_direction = Direction.UP

    # rotate the boiler to face the offshore pump
    boiler = game.rotate_entity(boiler, orthogonal_direction)

    # assert that the boiler is facing the offshore pump
    assert boiler.direction.value == orthogonal_direction.value

def test_rotate_transport_belt(game):
    # Place a transport belt
    transport_belt = game.place_entity(Prototype.TransportBelt, position=(0, 0), direction=Direction.UP)
    assert transport_belt.direction.value == Direction.UP.value
    rotate_entity(game, transport_belt)


def test_rotate_inserter(game):
    # Place a burner inserter
    inserter = game.place_entity(Prototype.BurnerInserter, position=(0, 0), direction=Direction.UP)
    assert inserter.direction.value == Direction.UP.value
    rotate_entity(game, inserter)

def test_rotate_transport_belt_output_and_input_position(game):
    belt = game.place_entity(Prototype.TransportBelt, position=(0, 0), direction=Direction.UP)
    assert belt.direction.value == Direction.UP.value

    rotated_belt = game.rotate_entity(belt, direction=Direction.DOWN)

    assert belt.output_position == rotated_belt.input_position
    assert belt.input_position == rotated_belt.output_position

def test_rotate_inserters_drop_and_pickup_position(game):
    inserter = game.place_entity(Prototype.BurnerInserter, position=(0, 0), direction=Direction.UP)
    assert inserter.direction.value == Direction.UP.value

    rotated_inserter = game.rotate_entity(inserter, direction=Direction.DOWN)

    assert inserter.pickup_position == rotated_inserter.drop_position
    assert inserter.drop_position == rotated_inserter.pickup_position



def rotate_entity(game, entity):
    # Rotate the transport belt right
    entity = game.rotate_entity(entity, direction=Direction.RIGHT)

    # Assert that the direction of the transport belt has been updated
    assert entity.direction.value == Direction.RIGHT.value

    entity = game.rotate_entity(entity, direction=Direction.LEFT)

    assert entity.direction.value == Direction.LEFT.value

    entity = game.rotate_entity(entity, direction=Direction.DOWN)

    assert entity.direction.value == Direction.DOWN.value

    entity = game.rotate_entity(entity, direction=Direction.UP)

    assert entity.direction.value == Direction.UP.value