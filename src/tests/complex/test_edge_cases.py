import pytest
from time import sleep
from factorio_entities import Position, ResourcePatch
from factorio_instance import Direction
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.initial_inventory = {
        'stone-furnace': 10,
        'burner-mining-drill': 10,
        'electric-mining-drill': 5,
        'transport-belt': 200,
        'underground-belt': 20,
        'splitter': 10,
        'burner-inserter': 50,
        'fast-inserter': 20,
        'pipe': 100,
        'pipe-to-ground': 20,
        'offshore-pump': 5,
        'boiler': 5,
        'steam-engine': 10,
        'small-electric-pole': 50,
        'medium-electric-pole': 20,
        'assembling-machine-1': 10,
        'iron-chest': 20,
        'coal': 500,
        'iron-plate': 200,
        'copper-plate': 200,
    }
    instance.reset()
    yield instance


def test_edge_case_entity_placement(game):
    """Test placement of entities at the edge of the map and in tight spaces."""
    # Place entity at map edge
    edge_position = Position(x=game.bounding_box, y=game.bounding_box)
    with pytest.raises(Exception):
        game.place_entity(Prototype.StoneFurnace, position=edge_position)

    # Place entities in a tight space
    game.place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))
    game.place_entity(Prototype.StoneFurnace, position=Position(x=3, y=0))
    with pytest.raises(Exception):
        game.place_entity(Prototype.StoneFurnace, position=Position(x=1.5, y=0))


def test_complex_resource_patch_interaction(game):
    """Test interactions with resource patches of varying shapes and sizes."""
    iron_patch = game.get_resource_patch(Resource.IronOre, game.nearest(Resource.IronOre))
    assert isinstance(iron_patch, ResourcePatch)

    # Place multiple drills on the same resource patch
    drill_positions = [
        iron_patch.bounding_box.left_top,
        Position(x=iron_patch.bounding_box.left_top.x + 3, y=iron_patch.bounding_box.left_top.y),
        Position(x=iron_patch.bounding_box.left_top.x, y=iron_patch.bounding_box.left_top.y + 3),
    ]

    for pos in drill_positions:
        game.move_to(pos)
        drill = game.place_entity(Prototype.ElectricMiningDrill, position=pos)
        assert drill is not None

    # Verify that all drills are mining from the same patch
    for drill in game.inspect_entities(iron_patch.bounding_box.left_top, radius=10).entities:
        if drill.prototype == Prototype.ElectricMiningDrill:
            assert drill.mining_target == Resource.IronOre


def test_error_handling_and_invalid_inputs(game):
    """Test error handling for invalid inputs and operations."""
    # Try to place an entity of the wrong type
    with pytest.raises(ValueError):
        game.place_entity("invalid_entity", position=Position(x=0, y=0))

    # Try to set an invalid recipe
    assembler = game.place_entity(Prototype.AssemblingMachine1, position=Position(x=5, y=5))
    with pytest.raises(ValueError):
        game.set_entity_recipe(assembler, "invalid_recipe")


def test_performance_under_load(game):
    """Test performance when placing and manipulating many entities."""
    start_time = game.get_game_time()

    # Place a large number of transport belts
    belt_count = 1000
    for i in range(belt_count):
        game.place_entity(Prototype.TransportBelt, position=Position(x=i * 0.5, y=0))

    # Rotate all belts
    for belt in game.inspect_entities(Position(x=0, y=0), radius=belt_count).entities:
        if belt.prototype == Prototype.TransportBelt:
            game.rotate_entity(belt, Direction.LEFT)

    end_time = game.get_game_time()
    assert end_time - start_time < 60  # Ensure operation completed in less than 1 minute of game time


def test_entity_interactions(game):
    """Test complex interactions between different types of entities."""
    # Create a small power network
    water_pos = game.nearest(Resource.Water)
    game.move_to(water_pos)
    offshore_pump = game.place_entity(Prototype.OffshorePump, position=water_pos)
    boiler = game.place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.RIGHT, spacing=1)
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.RIGHT, spacing=1)
    game.connect_entities(offshore_pump, boiler, Prototype.Pipe)
    game.connect_entities(boiler, steam_engine, Prototype.Pipe)

    # Create an assembly line
    assembler = game.place_entity_next_to(Prototype.AssemblingMachine1, steam_engine.position, Direction.DOWN,
                                          spacing=5)
    game.set_entity_recipe(assembler, Prototype.IronGearWheel)

    input_chest = game.place_entity_next_to(Prototype.IronChest, assembler.position, Direction.LEFT, spacing=assembler.tile_dimensions.tile_width - 1)
    output_chest = game.place_entity_next_to(Prototype.IronChest, assembler.position, Direction.RIGHT, spacing=assembler.tile_dimensions.tile_width - 1)

    input_inserter = game.place_entity_next_to(Prototype.BurnerInserter, input_chest.position, Direction.RIGHT, spacing=0.5)
    output_inserter = game.place_entity_next_to(Prototype.BurnerInserter, output_chest.position, Direction.LEFT,
                                                spacing=0.5)

    # Connect power
    game.connect_entities(steam_engine, assembler, Prototype.SmallElectricPole)

    # Insert materials and run the assembly line
    game.insert_item(Prototype.IronPlate, input_chest, 50)
    game.insert_item(Prototype.Coal, boiler, 50)

    # Wait for production
    sleep(30)

    # Check if iron gear wheels were produced
    output_inventory = game.inspect_inventory(output_chest)
    assert output_inventory[Prototype.IronGearWheel] > 0, "No iron gear wheels were produced"


def test_blueprint_functionality(game):
    """Test creating, saving, and loading blueprints."""
    # Create a simple setup
    game.move_to(Position(x=0, y=0))
    furnace = game.place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))
    inserter = game.place_entity_next_to(Prototype.BurnerInserter, furnace.position, Direction.UP, spacing=1)
    chest = game.place_entity_next_to(Prototype.IronChest, inserter.position, Direction.UP, spacing=1)

    # Create a blueprint of the setup
    blueprint = game.create_blueprint([furnace, inserter, chest])
    assert blueprint is not None

    # Clear the area
    game.clear_area(Position(x=-5, y=-5), Position(x=5, y=5))

    # Load the blueprint at a different location
    game.load_blueprint(blueprint, Position(x=10, y=10))

    # Verify that entities were placed correctly
    placed_entities = game.inspect_entities(Position(x=10, y=10), radius=5)
    assert len(placed_entities.entities) == 3
    assert any(e.prototype == Prototype.StoneFurnace for e in placed_entities.entities)
    assert any(e.prototype == Prototype.BurnerInserter for e in placed_entities.entities)
    assert any(e.prototype == Prototype.IronChest for e in placed_entities.entities)

# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])