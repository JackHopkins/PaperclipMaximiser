from typing import List

import pytest

from client.factorio_types import Prototype
from factorio_entities import Entity


@pytest.fixture
def game():

    from client.factorio_instance import FactorioInstance
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27016,
                                inventory={
                                    'coal': 50,
                                    'copper-plate': 50,
                                    'iron-plate': 50,
                                    'iron-chest': 1,
                                    'burner-mining-drill': 1,
                                    'electric-mining-drill': 1,
                                    'assembling-machine-1': 1,
                                    'stone-furnace': 1,
                                    'transport-belt': 50,
                                    'boiler': 1,
                                    'burner-inserter': 1,
                                    'pipe': 15,
                                    'steam-engine': 1,
                                })
    instance.reset()
    yield instance

@pytest.fixture
def entity_prototype():
    return Prototype.Boiler

@pytest.fixture
def surrounding_entity_prototype():
    return Prototype.TransportBelt

def test_place(game):
    boilers_in_inventory = game.inspect_inventory()[Prototype.Boiler]
    game.place_entity(Prototype.Boiler, position=(0, 0))
    assert boilers_in_inventory - 1 == game.inspect_inventory()[Prototype.Boiler]


def test_place_entity_next_to(game, entity_prototype, surrounding_entity_prototype):
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

def test_connect_steam_engines_to_boilers_using_pipes(game):
    boilers_in_inventory = game.inspect_inventory()[Prototype.Boiler]
    steam_engines_in_inventory = game.inspect_inventory()[Prototype.SteamEngine]
    pipes_in_inventory = game.inspect_inventory()[Prototype.Pipe]

    # Define the offsets for the four cardinal directions
    offsets = [(0, -10), (10, 0), (-10, 0)]  # Up, Right, Down, Left

    for offset in offsets:
        boiler: Entity = game.place_entity(Prototype.Boiler, position=(0, 0))
        steam_engine: Entity = game.place_entity(Prototype.SteamEngine, position=offset)

        connection: List[Entity] = game.connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)

        assert boilers_in_inventory - 1 == game.inspect_inventory()[Prototype.Boiler]
        assert steam_engines_in_inventory - 1 == game.inspect_inventory()[Prototype.SteamEngine]

        current_pipes_in_inventory = game.inspect_inventory()[Prototype.Pipe]
        spent_pipes = (pipes_in_inventory - current_pipes_in_inventory)
        assert spent_pipes == len(connection)

        game.reset()  # Reset the game state after each iteration

    boiler: Entity = game.place_entity(Prototype.Boiler, position=(0, 0))
    steam_engine: Entity = game.place_entity(Prototype.SteamEngine, position=(0, 10))

    try:
        connection: List[Entity] = game.connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)
        assert False
    except Exception:
        assert True


def test_connect_entities2(game, entity_prototype):
    # Place two entities
    entity1 = game.place_entity(entity_prototype, position=(0, 0))
    entity2 = game.place_entity(entity_prototype, position=(10, 10))

    # Connect the entities
    game.connect_entities(source_position=entity1.position, target_position=entity2.position, connection_type=Prototype.TransportBelt)

    # Inspect the entities to check if they are connected
    entity1_inspected = game.inspect_entities(radius=10, position=entity1.position)[0]
    entity2_inspected = game.inspect_entities(radius=10, position=entity2.position)[0]

    # Assert that the entities are connected
    assert entity1_inspected.connected_entities == entity2_inspected


#if __name__ == '__main__':
#    freeze_support()