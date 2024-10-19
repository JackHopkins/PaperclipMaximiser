from factorio_instance import *



def power_electric_mining_drill(electric_mining_drill: Entity) -> None:
    """
    Objective: We need to create a steam energy electricity generator to power the electric drill.
    Mining setup: There is an electric mining drill on the map
    Inventory: We have a boiler, offshore pump, steam engine and power poles in our inventory
    :param miner (Entity): The mining drill entity
    :return: None
    """
    # [PLANNING] To create this we need to first place the offshore pump, boiler and steam engine
    # Then we need to put a electric mining drill on copper patch
    # Then we need to connect the offshore pump to the boiler with pipes
    # Then we need to power the boiler with coal and check the warning of engine to ensure it generates electricity using the boiler
    # Finally we need to connect the drill with engine with power poles and check the warning to ensure it is connected to the power network [END OF PLANNING]
    # We dont need to craft any resources for this task as all resources are present in inventory 
    
    # print out initial inventory
    initial_inventory = inspect_inventory()
    print(f"Inventory at starting: {initial_inventory}")
    
    # Get the nearest water source
    # We will place an offshore pump onto the water
    water_position = nearest(Resource.Water)
    assert water_position, "No water source found nearby"
    move_to(water_position)
    offshore_pump = place_entity(Prototype.OffshorePump, Direction.UP, water_position)
    assert offshore_pump, "Failed to place offshore pump"
    print(f"Offshore pump placed at {offshore_pump.position}")

    # Place boiler next to offshore pump
    boiler = place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.UP, spacing=2)
    assert boiler, "Failed to place boiler"
    print(f"Boiler placed at {boiler.position}")
    print(f"Current inventory: {inspect_inventory()}")

    # add coal to the boiler
    boiler_with_coal = insert_item(Prototype.Coal, boiler, quantity=5)
    print(f"Inventory after adding coal: {inspect_inventory()}")

    # Connect offshore pump to boiler with pipes
    pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)
    assert pipes, "Failed to connect offshore pump to boiler"
    print(f"Pipes placed between offshore pump and boiler")

    # Place steam engine next to boiler
    steam_engine = place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.UP, spacing=2)
    assert steam_engine, "Failed to place steam engine"
    print(f"Steam engine placed at {steam_engine.position}")

    # Connect boiler to steam engine with pipes
    pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)
    assert pipes, "Failed to connect boiler to steam engine"
    print(f"Pipes placed between boiler and steam engine")

    # wait 2 seconds for the boiler to start producing electricity
    sleep(2)

    # check if the boiler is receiving electricity
    # if it says not connected to power network, then it is working
    # it just isn't connected to any power poles
    inspected_steam_engine = inspect_entities(position=steam_engine.position, radius=1).get_entity(Prototype.SteamEngine)
    assert inspected_steam_engine.warning == 'not connected to power network', f"Steam engine not connected to power network. Warning: {inspected_steam_engine.warning}"
    print(f"Steam engine warning: {inspected_steam_engine.warning}")

    # Connect electric drill to steam engine with power poles
    poles = connect_entities(electric_mining_drill, steam_engine, Prototype.SmallElectricPole)
    assert poles, "Failed to connect drill to steam engine"
    print(f"Connected electric mining drill to steam engine with power poles")

    # verify that there is not warning for assmbling machine
    # if the warning is None, then it is connected to the power network
    inspected_drill = inspect_entities(position=electric_mining_drill.position, radius=1).get_entity(Prototype.ElectricMiningDrill)
    assert inspected_drill.warning is None, "Drill not connected to power network"

###FUNC SEP


def connect_miner_to_chest(miner: Entity, chest: Entity) -> None:
    """
    Objective: Connect a mining drill to a chest right from it using transport belts and burner inserters
    Mining setup: We have a mining drill and a chest on the map
    Inventory: We have transport belts and burner inserters in our inventory
    :param miner (Entity): The mining drill entity
    :param chest (Entity): The chest entity
    :return: None
    """
    # [PLANNING]
    # 1. Place an burner inserter next to the chest
    # 2. Rotate the burner inserter to put items to the chest
    # 3. Place transport belts from the drill's output to chest inserter's pickup position
    # [END OF PLANNING]

    print(f"Starting to connect miner at {miner.position} to chest at {chest.position}")

    # Place an inserter next to the miner's output
    chest_inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.DOWN, spacing=0)
    assert chest_inserter, "Failed to place inserter next to miner"
    print(f"Placed miner inserter at {chest_inserter.position}")

    # Rotate the miner inserter to take items from the miner
    chest_inserter = rotate_entity(chest_inserter, Direction.UP)
    print(f"Rotated miner inserter to face the miner")

    # Connect the miners output to the chest inserter with transport belts
    belts = connect_entities(miner.drop_position, chest_inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts between inserters"
    print(f"Placed {len(belts)} transport belts to connect inserters")

    print("Successfully connected miner to chest using transport belts and inserters")


###FUNC SEP

def create_electric_iron_mine():
    """
    Objective: Create an automated iron mine that mines iron ore to a chest further away and right from it using a electric drill.
    Mining setup: There are no entities on the map.
    Inventory: {
            "iron-plate": 50,
            "coal": 100,
            "copper-plate": 50,
            "iron-chest": 2,
            "burner-mining-drill": 3,
            "electric-mining-drill": 1,
            "assembling-machine-1": 1,
            "stone-furnace": 9,
            "transport-belt": 500,
            "boiler": 1,
            "burner-inserter": 32,
            "pipe": 15,
            "steam-engine": 1,
            "small-electric-pole": 10,
            "wooden-chest": 1,
            "offshore-pump": 1
        }
    """
    # [PLANNING]
    # To achieve this this objective we need the following:
    #  Electric mining drill for mining
    #  Iron chest for storage
    #  Transport belts for moving items between drill and chest
    #  Inserters for moving items between chest and transport belts
    #  Electricity to power the electric mining drill.
    #  For electricity we need a steam engine, boiler, pipes, offshore pump and power poles
    # We have all the required items in our inventory so we do not need to mine or craft anything
    # 1. Find the nearest iron patch
    # 2. Place a electric mining drill on the iron patch
    # 3. Power the electric mining drill with electricity
    # 4. Place a chest further away and to the right of the mining drill
    # 5. Connect the mining drill to the chest using transport belts and inserters
    # 6. Wait for some time to allow iron production
    # 7. Check if the chest contains iron
    # [END OF PLANNING]

    print("Starting to create an automated iron mine")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Find the nearest iron patch
    iron_position = nearest(Resource.IronOre)
    assert iron_position, "No iron found nearby"
    move_to(iron_position)
    print(f"Moving to iron patch at {iron_position}")

    # Step 2: Place a burner mining drill on the iron patch
    iron_patch = get_resource_patch(Resource.IronOre, iron_position, radius=10)
    assert iron_patch, "No iron patch found within radius"
    miner = place_entity(Prototype.ElectricMiningDrill, Direction.UP, iron_patch.bounding_box.center)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed mining drill at {miner.position}")

    # Step 3: Power the electric mining drill with electricity
    """[SYNTHESISED]
    Name: connect_miner_to_chest
    Objective: We need to create a steam energy electricity generator to power the electric drill.
    Mining setup: There is an electric mining drill on the map
    Inventory: We have a boiler, offshore pump, steam engine and power poles in our inventory
    :param miner (Entity): The mining drill entity
    :return: None
    [END OF SYNTHESISED]"""
    power_electric_mining_drill(electric_mining_drill=miner)


    # Step 4: Place a chest further away and to the right of the mining drill
    chest_pos = Position(x=miner.position.x + 5, y=miner.position.y - 5)
    move_to(chest_pos)
    chest = place_entity(Prototype.IronChest, Direction.UP, chest_pos)
    assert chest, f"Failed to place chest at {chest_pos}"
    print(f"Placed chest at {chest.position}")

    # Step 5: Connect the mining drill to the chest using transport belts and inserters
    """[SYNTHESISED]
    Name: connect_miner_to_chest
    Objective: Connect a mining drill to a chest right from it using transport belts and inserters
    Mining setup: We have a mining drill and a chest on the map. We also have electricity generator on the map
    Inventory: We have transport belts and inserters in our inventory
    :param miner (Entity): The mining drill entity
    :param chest (Entity): The chest entity
    :return: None
    [END OF SYNTHESISED]"""
    connect_miner_to_chest(miner=miner, chest=chest)
    print("Connected the mining drill to the chest")

    # Step 6: Wait for some time to allow iron production
    print("Waiting for 30 seconds to allow iron production...")
    sleep(30)

    # Step 7: Check if the chest contains iron
    chest_inventory = inspect_inventory(chest)
    iron_in_chest = chest_inventory.get(Prototype.IronOre, 0)
    assert iron_in_chest > 0, f"No iron was produced. iron in chest: {iron_in_chest}"
    print(f"Successfully produced {iron_in_chest} iron in the chest.")

    print("Automated iron mine created successfully!")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP

create_electric_iron_mine()