import pytest

from factorio_entities import Entity, Position, EntityStatus
from factorio_instance import Direction
from factorio_types import Prototype, Resource, PrototypeName


@pytest.fixture()
def game(instance):
    instance.initial_inventory = {
        **instance.initial_inventory,
        'stone-furnace': 10,
        'burner-inserter': 50,
        'offshore-pump': 4,
        'pipe': 100,
        'small-electric-pole': 50,
        'transport-belt': 200,
        'coal': 100,
        'wooden-chest': 1,
        'assembling-machine-1': 10,
    }
    instance.reset()
    yield instance.namespace
    #instance.reset()
def test_connect_steam_engine_to_assembler_with_electricity_poles(game):
    """
    Place a steam engine and an assembling machine next to each other.
    Connect them with electricity poles.
    :param game:
    :return:
    """
    steam_engine = game.place_entity(Prototype.SteamEngine, position=Position(x=0, y=0))
    assembler = game.place_entity_next_to(Prototype.AssemblingMachine1, reference_position=steam_engine.position,
                                          direction=game.RIGHT, spacing=10)
    game.move_to(Position(x=5, y=5))
    diagonal_assembler = game.place_entity(Prototype.AssemblingMachine1, position=Position(x=10, y=10))

    # check to see if the assemblers are connected to the electricity network
    inspected_assemblers = game.get_entities({Prototype.AssemblingMachine1}, position=diagonal_assembler.position)

    for a in inspected_assemblers:
        assert a.warnings == ['not connected to power network']

    poles_in_inventory = game.inspect_inventory()[Prototype.SmallElectricPole]

    poles = game.connect_entities(steam_engine, assembler, connection_type=Prototype.SmallElectricPole)
    poles2 = game.connect_entities(steam_engine, diagonal_assembler, connection_type=Prototype.SmallElectricPole)

    current_poles_in_inventory = game.inspect_inventory()[Prototype.SmallElectricPole]
    spent_poles = (poles_in_inventory - current_poles_in_inventory)

    assert spent_poles == len(poles2.poles)

    # check to see if the assemblers are connected to the electricity network
    assemblers = game.get_entities({Prototype.AssemblingMachine1})
    for assembler in assemblers:
        assert assembler.status == EntityStatus.NO_POWER

def test_connect_power_poles_without_blocking_mining_drill(game):
    coal_position = game.nearest(Resource.Coal)
    coal_patch = game.get_resource_patch(Resource.Coal, coal_position, radius=10)
    assert coal_patch, "No coal patch found within radius"
    game.move_to(coal_patch.bounding_box.center())
    miner = game.place_entity(Prototype.ElectricMiningDrill, Direction.UP, coal_patch.bounding_box.center())

    # print out initial inventory
    initial_inventory = game.inspect_inventory()
    print(f"Inventory at starting: {initial_inventory}")

    # Get the nearest water source
    # We will place an offshore pump onto the water
    water_position = game.nearest(Resource.Water)
    assert water_position, "No water source found nearby"
    game.move_to(water_position)
    offshore_pump = game.place_entity(Prototype.OffshorePump, Direction.UP, water_position)
    assert offshore_pump, "Failed to place offshore pump"
    print(f"Offshore pump placed at {offshore_pump.position}")

    # Place boiler next to offshore pump
    boiler = game.place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.UP, spacing=2)
    assert boiler, "Failed to place boiler"
    print(f"Boiler placed at {boiler.position}")
    print(f"Current inventory: {game.inspect_inventory()}")

    # add coal to the boiler
    boiler_with_coal = game.insert_item(Prototype.Coal, boiler, quantity=5)
    print(f"Inventory after adding coal: {game.inspect_inventory()}")

    # Connect offshore pump to boiler with pipes
    pipes = game.connect_entities(offshore_pump, boiler, Prototype.Pipe)
    assert pipes, "Failed to connect offshore pump to boiler"
    print(f"Pipes placed between offshore pump and boiler")

    # Place steam engine next to boiler
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.UP, spacing=2)
    assert steam_engine, "Failed to place steam engine"
    print(f"Steam engine placed at {steam_engine.position}")

    # Connect boiler to steam engine with pipes
    pipes = game.connect_entities(boiler, steam_engine, Prototype.Pipe)
    assert pipes, "Failed to connect boiler to steam engine"

    # Connect electric drill to steam engine with power poles
    poles = game.connect_entities(miner, steam_engine, Prototype.SmallElectricPole)
    assert poles, "Failed to connect drill to steam engine"
    print(f"Connected electric mining drill to steam engine with power poles")

    # Get the mining drill status
    drill = game.get_entity(Prototype.ElectricMiningDrill, miner.position)
    assert drill, "Failed to get mining drill"
    assert drill.status.value == EntityStatus.WORKING.value

def test_pole_to_generator(game):
    game.move_to(Position(x=1, y=1))

    # Place offshore pump near water
    water = game.get_resource_patch(Resource.Water, game.nearest(Resource.Water))
    water_position = water.bounding_box.right_bottom

    assert water_position, "No water source found nearby"
    game.move_to(water_position)
    offshore_pump = game.place_entity(Prototype.OffshorePump, Direction.DOWN, water_position)
    assert offshore_pump, "Failed to place offshore pump"

    # Place boiler next to offshore pump
    # Important: The boiler needs to be placed with a spacing of 2 to allow for pipe connections
    boiler = game.place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.DOWN, spacing=2)
    assert boiler, "Failed to place boiler"

    # add coal to the boiler
    # need to update the boiler var after insert
    boiler = game.insert_item(Prototype.Coal, boiler, quantity=5)

    # Connect offshore pump to boiler with pipes
    pipes = game.connect_entities(offshore_pump, boiler, Prototype.Pipe)
    assert pipes, "Failed to connect offshore pump to boiler"

    # Place steam engine next to boiler
    # Important: The steam engine needs to be placed with a spacing of 2 to allow for pipe connections
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.LEFT, spacing=2)
    assert steam_engine, "Failed to place steam engine"

    # Connect boiler to steam engine with pipes
    pipes = game.connect_entities(boiler, steam_engine, Prototype.Pipe)
    assert pipes, "Failed to connect boiler to steam engine"

    # check if the boiler is receiving electricity
    # if it says not connected to power network, then it is working
    # it just isn't connected to any power poles
    inspected_steam_engine = game.get_entities({Prototype.SteamEngine}, position=steam_engine.position)[0]
    assert inspected_steam_engine.status == EntityStatus.NOT_PLUGGED_IN_ELECTRIC_NETWORK

    """
    Step 1: Place electric mining drill. We need to find a stone patch and place the electric mining drill on it.
    """
    # Inventory at the start of step {'small-electric-pole': 20, 'pipe': 10, 'electric-mining-drill': 1}
    # Step Execution

    # Find the nearest stone patch
    stone_patch_position = game.nearest(Resource.Stone)
    print(f"Nearest stone patch found at: {stone_patch_position}")

    # Move to the stone patch location
    game.move_to(stone_patch_position)
    print(f"Moved to stone patch at: {stone_patch_position}")

    # Place the electric mining drill on the stone patch
    drill = game.place_entity(Prototype.ElectricMiningDrill, Direction.UP, stone_patch_position)
    print(f"Placed electric mining drill at: {drill.position}")

    print("Electric mining drill successfully placed on stone patch")
    print(f"Current inventory: {game.inspect_inventory()}")

    ###SEP
    """
    Step 2: Connect power to the drill. We need to create a power line from the steam engine to the electric mining drill using small electric poles.
    """
    # get the steam engine entity, first get all entities
    entities = game.get_entities({Prototype.SteamEngine})
    # get all steam engines by looking at the prototype
    steam_engines = [x for x in entities if x.prototype is Prototype.SteamEngine]
    # get the first one as we only have one
    steam_engine = steam_engines[0]

    connection = game.connect_entities(steam_engine, drill, Prototype.SmallElectricPole)
    assert connection, "Failed to connect electric mining drill to power"
    print("Electric mining drill connected to power")

    """
    Step 3: Verify power connection. We need to check if the electric mining drill is powered by examining its status.
    - Wait for a few seconds to allow the power to stabilize
    - Check the status of the electric mining drill to confirm it has power
    """
    # sleep for a few seconds to allow power to stabilize
    game.sleep(5)

    # update the drill entity to get the powered one
    drill = game.get_entity(Prototype.ElectricMiningDrill, drill.position)
    # Check the status of the electric mining drill
    drill_status = drill.status
    assert drill_status != EntityStatus.NO_POWER, "Electric mining drill is not powered"
    print("Electric mining drill is powered and working")

def test_connect_steam_engine_mining_drill(game):
    pos = game.nearest(Resource.Water)
    game.move_to(pos)
    pump = game.place_entity(Prototype.OffshorePump, position=pos)
    boiler = game.place_entity_next_to(Prototype.Boiler, reference_position=pump.position, spacing=2, direction=Direction.UP)
    game.connect_entities(pump, boiler, Prototype.Pipe)
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine, reference_position=boiler.position, spacing=2,
                                        direction=Direction.UP)
    game.connect_entities(boiler, steam_engine, Prototype.Pipe)
    game.insert_item(Prototype.Coal, boiler, 2)
    game.sleep(2)
    pos = game.nearest(Resource.IronOre)
    game.move_to(pos)
    drill = game.place_entity(Prototype.ElectricMiningDrill, position=pos)
    game.connect_entities(drill, steam_engine, Prototype.SmallElectricPole)
    game.sleep(2)
    drill = game.get_entity(Prototype.ElectricMiningDrill, position=pos)
    assert drill.status == EntityStatus.WORKING

def test_pole_groups(game):
    water_position = game.nearest(Resource.Water)
    game.move_to(water_position)
    offshore_pump = game.place_entity(Prototype.OffshorePump, position=water_position)
    print(offshore_pump)
    boiler = game.place_entity_next_to(Prototype.Boiler, reference_position=offshore_pump.position, spacing=3)
    boiler = game.insert_item(Prototype.Coal, boiler, 10)
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine, reference_position=boiler.position, spacing=3)
    print(f"Placed steam_engine at {steam_engine.position}")  # Position(x=4, y = -21)
    water_pipes = game.connect_entities(offshore_pump, boiler, Prototype.Pipe)
    steam_pipes = game.connect_entities(boiler, steam_engine, Prototype.Pipe)
    game.sleep(5)
    print(steam_engine)
    outp = game.connect_entities(steam_engine.position, Position(x=4, y=-20), Prototype.SmallElectricPole)
    entities = game.get_entities()
    assert len(entities) == 6