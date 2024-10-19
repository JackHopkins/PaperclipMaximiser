from factorio_instance import *


def connect_miner_to_chest(miner: Entity, chest: Entity) -> None:
    """
    Objective: Connect a mining drill to a chest left from it using transport belts and burner inserters
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
    print(f"Placed chest inserter at {chest_inserter.position}")

    # Rotate the miner inserter to take items from the miner
    chest_inserter = rotate_entity(chest_inserter, Direction.UP)
    print(f"Rotated chest inserter to face the chest")

    # Connect the miners output to the chest inserter with transport belts
    belts = connect_entities(miner.drop_position, chest_inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts between inserters"
    print(f"Placed {len(belts)} transport belts to connect inserters")

    print("Successfully connected miner to chest using transport belts and inserters")


###FUNC SEP


def create_coal_mine():
    """
    Objective: Create an automated coal mine that mines coal to a chest further away and left from it using a burner drill.
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
    # For this we need a burner mining drill, a chest, transport belts and inserters
    # We already have all the required items in our inventory
    # 1. Find the nearest coal patch
    # 2. Place a burner mining drill on the coal patch
    # 3. Fuel the mining drill with coal
    # 4. Place a chest further away and to the left of the mining drill
    # 5. Connect the mining drill to the chest using transport belts and inserters
    # 6. Wait for some time to allow coal production
    # 7. Check if the chest contains coal
    # [END OF PLANNING]

    print("Starting to create an automated coal mine")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Find the nearest coal patch
    coal_position = nearest(Resource.Coal)
    assert coal_position, "No coal found nearby"
    move_to(coal_position)
    print(f"Moving to coal patch at {coal_position}")

    # Step 2: Place a burner mining drill on the coal patch
    coal_patch = get_resource_patch(Resource.Coal, coal_position, radius=10)
    assert coal_patch, "No coal patch found within radius"
    miner = place_entity(Prototype.BurnerMiningDrill, Direction.UP, coal_patch.bounding_box.center)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed mining drill at {miner.position}")

    # Step 3: Fuel the mining drill with coal
    miner_with_coal = insert_item(Prototype.Coal, miner, quantity=5)
    print(f"Fuelled mining drill with coal: {miner_with_coal}")

    # Step 4: Place a chest further away and to the left of the mining drill
    chest_pos = Position(x=miner.position.x - 5, y=miner.position.y - 5)
    move_to(chest_pos)
    chest = place_entity(Prototype.IronChest, Direction.UP, chest_pos)
    assert chest, f"Failed to place chest at {chest_pos}"
    print(f"Placed chest at {chest.position}")

    # Step 5: Connect the mining drill to the chest using transport belts and inserters
    """[SYNTHESISED]
    Name: connect_miner_to_chest
    Objective: Connect a mining drill to a chest left from it using transport belts and inserters
    Mining setup: We have a mining drill and a chest on the map
    Inventory: We have transport belts and inserters in our inventory
    :param miner (Entity): The mining drill entity
    :param chest (Entity): The chest entity
    :return: None
    [END OF SYNTHESISED]"""
    connect_miner_to_chest(miner=miner, chest=chest)
    print("Connected the mining drill to the chest")

    # Step 6: Wait for some time to allow coal production
    print("Waiting for 30 seconds to allow coal production...")
    sleep(30)

    # Step 7: Check if the chest contains coal
    chest_inventory = inspect_inventory(chest)
    coal_in_chest = chest_inventory.get(Prototype.Coal, 0)
    assert coal_in_chest > 0, f"No coal was produced. Coal in chest: {coal_in_chest}"
    print(f"Successfully produced {coal_in_chest} coal in the chest.")

    print("Automated coal mine created successfully!")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP

create_coal_mine()