import pytest
from time import sleep

from factorio_entities import Position
from factorio_instance import Direction
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.initial_inventory = {
        'burner-mining-drill': 2,
        'stone-furnace': 1,
        'burner-inserter': 5,
        'transport-belt': 100,
        'iron-chest': 1,
        'coal': 50,
    }
    instance.reset()
    yield instance


def test_auto_fueling_iron_smelting_factory(game):
    """
    Builds an auto-fueling iron smelting factory:
    - Mines coal and iron ore.
    - Uses transport belts to deliver coal to fuel the iron miner and furnace.
    - Smelts iron ore into iron plates.
    - Stores iron plates in an iron chest.
    """
    # Move to the nearest coal resource and place a burner mining drill
    coal_position = game.nearest(Resource.Coal)
    game.move_to(coal_position)
    coal_drill = game.place_entity(Prototype.BurnerMiningDrill, position=coal_position, direction=Direction.DOWN)

    # Find the nearest iron ore resource
    iron_position = game.nearest(Resource.IronOre)

    # Place the iron mining drill at iron_position, facing down
    move_to_iron = game.move_to(iron_position)
    iron_drill = game.place_entity(Prototype.BurnerMiningDrill, position=iron_position, direction=Direction.DOWN)

    # Place an inserter to fuel the iron drill from the coal belt
    inserter_position = Position(x=iron_drill.position.x + iron_drill.tile_dimensions.tile_width/2, y=iron_drill.position.y-1)
    iron_drill_fuel_inserter = game.place_entity(Prototype.BurnerInserter, position=inserter_position, direction=Direction.LEFT, exact=True)

    coal_belt = game.connect_entities(source=coal_drill, target=iron_drill_fuel_inserter, connection_type=Prototype.TransportBelt)

    # Extend coal belt to pass next to the furnace position
    furnace_position = Position(x=iron_drill.drop_position.x, y=iron_drill.drop_position.y + 1)

    # Place the furnace at the iron drill's drop position
    iron_furnace = game.place_entity(Prototype.StoneFurnace, position=furnace_position)

    # Place an inserter to fuel the furnace from the coal belt
    furnace_fuel_inserter_position = Position(x=iron_furnace.position.x + 1, y=iron_furnace.position.y)
    furnace_fuel_inserter = game.place_entity(Prototype.BurnerInserter, position=furnace_fuel_inserter_position, direction=Direction.LEFT)

    coal_belt_to_furnace = game.connect_entities(coal_belt[-1], furnace_fuel_inserter.pickup_position, connection_type=Prototype.TransportBelt)
    coal_belt.extend(coal_belt_to_furnace)

    furnace_to_chest_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                          reference_position=iron_furnace.position,
                                                          direction=Direction.DOWN,
                                                          spacing=0)
    # Place an iron chest to store iron plates
    iron_chest = game.place_entity_next_to(Prototype.IronChest,
                                           reference_position=iron_furnace.position,
                                           direction=Direction.DOWN,
                                           spacing=1)

    # Start the system by fueling the coal drill
    game.move_to(coal_position)
    game.insert_item(Prototype.Coal, coal_drill, quantity=10)

    # Wait for some time to let the system produce iron plates
    sleep(60)  # Wait for 60 seconds

    # Check the iron chest to see if iron plates have been produced
    chest_inventory = game.inspect_inventory(iron_chest)
    iron_plates_in_chest = chest_inventory.get(Prototype.IronPlate, 0)

    # Assert that some iron plates have been produced
    assert iron_plates_in_chest > 0, "No iron plates were produced"

    print(f"Successfully produced {iron_plates_in_chest} iron plates.")