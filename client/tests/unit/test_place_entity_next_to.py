import pytest

from factorio_types import Prototype

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

@pytest.fixture
def entity_prototype():
    return Prototype.Boiler

@pytest.fixture
def surrounding_entity_prototype():
    return Prototype.TransportBelt


def test_place_entity_next_to(game, entity_prototype, surrounding_entity_prototype):
    """
    Place an entity next to another entity in all four directions, with a variety of spacing.
    :param game:
    :param entity_prototype:
    :param surrounding_entity_prototype:
    :return:
    """
    for spacing in range(0, 10):
        entities_in_inventory = game.inspect_inventory()[entity_prototype]
        surrounding_entities_in_inventory = game.inspect_inventory()[surrounding_entity_prototype]
        entity = game.place_entity(entity_prototype, position=(0, 0))
        assert entity

        directions = [game.RIGHT, game.DOWN, game.LEFT, game.UP]
        surrounding_entities = []

        for direction in directions:
            surrounding_entity = game.place_entity_next_to(surrounding_entity_prototype,
                                                           reference_position=entity.position,
                                                           direction_from=direction,
                                                           spacing=spacing)
            assert surrounding_entity
            surrounding_entities.append(surrounding_entity)

        assert entities_in_inventory - 1 == game.inspect_inventory()[entity_prototype]
        assert surrounding_entities_in_inventory - len(directions) == game.inspect_inventory()[surrounding_entity_prototype]

        for i, surrounding_entity in enumerate(surrounding_entities):
            if i == 0:  # RIGHT
                assert surrounding_entity.position.x - entity.tile_dimensions.tile_width == spacing - 0.5
                assert surrounding_entity.position.y == 0.5
            elif i == 1:  # DOWN
                assert surrounding_entity.position.x == 0.5
                assert surrounding_entity.position.y - entity.tile_dimensions.tile_height == spacing - 0.5
            elif i == 2:  # LEFT
                # spacing == 0 / 1.5
                # spacing == 1 / 0.5
                assert surrounding_entity.position.x + entity.tile_dimensions.tile_width == 1.5 - spacing
                assert surrounding_entity.position.y == 0.5
            else:  # UP
                assert surrounding_entity.position.x == 0.5
                assert surrounding_entity.position.y + entity.tile_dimensions.tile_height == 0.5 - spacing

        game.reset()