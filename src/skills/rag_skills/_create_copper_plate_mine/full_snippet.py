from factorio_instance import *


def connect_furnace_to_chest(furnace: Entity, chest: Entity) -> None:
    """
    Objective: Connect the smelting furnace to the chest above it using transport belts and inserters
    Mining setup: We have a burner mining drill, a furnace smelting plates and an iron chest on the map
    Inventory: We have burner inserters and transport belts in our inventory
    :param furnace (Entity): The furnace entity
    :param chest (Entity): The iron chest entity
    :return: None
    :return: None
    """
    # [PLANNING]
    # 1. Place a burner inserter next to the chest
    # 2. Rotate the inserter to put items into the chest not take from it
    # 3. Fuel the inserter
    # 4. Add a inserter to take items from the furnace. This inserter does not need to be rotated as it takes not puts items
    # 5. Fuel the inserter
    # 6. Connect furnace inserter drop_position to chest inserter's pickup position with transport belts 
    #  [END OF PLANNING]

    print(f"Starting to connect furnace at {furnace.position} to chest at {chest.position}")
    
    # Place burner inserter next to the chest
    chest_inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.DOWN)
    assert chest_inserter, "Failed to place inserter next to chest"
    print(f"Placed chest inserter at {chest_inserter.position}")

    # Rotate the chest inserter to put items to the chest
    chest_inserter = rotate_entity(chest_inserter, Direction.UP)
    print(f"Rotated chest inserter to face the chest")

    # Fuel the chest inserter
    insert_item(Prototype.Coal, chest_inserter, quantity=5)
    print(f"Fueled chest inserter with coal")

    # Place burner inserter next to the furnace
    furnace_inserter = place_entity_next_to(Prototype.BurnerInserter, furnace.position, direction=Direction.UP)
    assert furnace_inserter, "Failed to place inserter next to furnace"
    print(f"Placed furnace inserter at {furnace_inserter.position}")

    # Fuel the chest inserter
    insert_item(Prototype.Coal, furnace_inserter, quantity=5)
    print(f"Fueled chest inserter with coal")

    # Connect the chest inserter to the furnace inserters drop position using transport belts
    belts = connect_entities(furnace_inserter.drop_position, chest_inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts"
    print(f"Connected chest inserter to furnace inserter with transport belts")

###FUNC SEP


def create_copper_plate_mine():
    """
    Objective: Create an automated copper plate mine that mines copper ore, smelts it to copper plates and puts them in a chest further away and up from it.
    The final setup should be checked by looking if the chest has any copper plates in it.
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
            "wooden-chest": 1
        }
    """
    # [PLANNING]
    # For this we need a burner mining drill, a chest, a furnace, transport belts and inserters
    # We already have all the required items in our inventory
    # 1. Find the nearest copper ore patch
    # 2. Place a burner mining drill on the copper ore patch
    # 3. Fuel the burner mining drill with coal
    # 4. Place a furnace with coal at the drill's drop position
    # 4. Place a chest further away and up from the mining drill
    # 5. Connect the furnace to the chest using transport belts and inserters
    # 6. Wait for some time to allow the system to produce copper ore
    # 7. Check if the chest contains copper ore
    # [END OF PLANNING]

    print("Starting to create an automated copper ore mine")
    print(f"Initial inventory: {inspect_inventory()}")

    # Find the nearest copper ore patch
    copper_position = nearest(Resource.CopperOre)
    assert copper_position, "No copper ore found nearby"
    move_to(copper_position)
    print(f"Moving to copper ore patch at {copper_position}")

    # Place a burner mining drill on the copper ore patch
    miner = place_entity(Prototype.BurnerMiningDrill, Direction.UP, copper_position)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed burner mining drill at {miner.position}")

    # Fuel the burner mining drill with coal
    miner_with_coal = insert_item(Prototype.Coal, miner, quantity=5)
    print(f"Fueled mining drill with coal: {miner_with_coal}")

    # Place a furnace with coal at the drill's drop position
    furnace = place_entity(Prototype.StoneFurnace, position = miner.drop_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # add coal to the furnace
    furnace_with_coal = insert_item(Prototype.Coal, furnace, quantity=5)
    print(f"Fueled furnace with coal: {furnace_with_coal}")

    # Place a chest further away and up from the mining drill
    chest_position = Position(x=miner.position.x, y=miner.position.y - 11)
    move_to(chest_position)
    chest = place_entity(Prototype.IronChest, Direction.UP, chest_position)
    assert chest, f"Failed to place iron chest at {chest_position}"
    print(f"Placed iron chest at {chest.position}")

    # """[SYNTHESISED]
    # Name: connect_furnace_to_chest
    # Objective: Connect the smelting furnace to the chest above it using transport belts and inserters
    # Mining setup: We have a burner mining drill, a furnace smelting plates and an iron chest on the map
    # Inventory: We have burner inserters and transport belts in our inventory
    # :param furnace (Entity): The furnace entity
    # :param chest (Entity): The iron chest entity
    # :return: None
    # [END OF SYNTHESISED]"""
    connect_furnace_to_chest(furnace=furnace_with_coal, chest=chest)
    print("Connected the mining drill to the chest")

    # Wait for some time to allow the system to produce copper plate
    print("Waiting for 30 seconds to allow copper plate production...")
    sleep(30)

    # Check if the chest contains copper plate
    chest_inventory = inspect_inventory(chest)
    copper_plate_count = chest_inventory.get(Prototype.CopperPlate, 0)
    assert copper_plate_count > 0, f"No copper plate found in the chest. Current inventory: {chest_inventory}"
    print(f"Success! Found {copper_plate_count} copper plate in the chest.")

    print("Automated copper plate mine created successfully!")



###FUNC SEP

create_copper_plate_mine()