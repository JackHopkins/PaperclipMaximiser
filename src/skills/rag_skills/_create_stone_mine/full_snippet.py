from factorio_instance import *


def create_stone_mine():
    """
    Objective: We need create an automated stone mine that mines stone to a chest further away and right from it. 
    The final setup should be checked by looking if the chest has any stone in it.
    Mining setup: There are no entities on the map
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
    # To achieve this objective, we need to:
    # 1. Find the nearest stone patch
    # 2. Place a burner mining drill on the stone patch
    # 3. Fuel the mining drill with coal
    # 4. Place a wooden chest to the right and further away from the drill
    # 5. Place a burner inserter next to the drill to pick up the stone
    # 6. Connect the inserter to the chest using transport belts
    # 7. Fuel the inserter with coal
    # 8. Wait for some time to allow the system to mine stone
    # 9. Check if stone has been deposited in the chest
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Find the nearest stone patch
    stone_position = nearest(Resource.Stone)
    assert stone_position, "No stone found nearby"
    move_to(stone_position)
    print(f"Moving to stone patch at {stone_position}")

    # Get the stone patch details
    stone_patch = get_resource_patch(Resource.Stone, stone_position, radius=10)
    print(f"Stone patch details: {stone_patch}")
    assert stone_patch, "No stone patch found within radius"

    # Step 2: Place the burner mining drill on the stone patch
    miner = place_entity(Prototype.BurnerMiningDrill, Direction.RIGHT, stone_patch.bounding_box.center)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed burner mining drill at {miner.position}")

    # Step 3: Fuel the mining drill with coal
    miner_with_coal = insert_item(Prototype.Coal, miner, quantity=5)
    print(f"Fuelled mining drill with coal: {miner_with_coal}")

    # Step 4: Place a wooden chest to the right and further away from the drill
    chest_pos = Position(x=miner.position.x + 7, y=miner.position.y)
    move_to(chest_pos)
    chest = place_entity(Prototype.WoodenChest, Direction.RIGHT, chest_pos)
    assert chest, f"Failed to place wooden chest at {chest_pos}"
    print(f"Placed wooden chest at {chest.position}")

    # Step 5: Place a burner inserter next to the chest to put items into the chest
    inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.RIGHT, spacing=0)
    assert inserter, "Failed to place burner inserter"
    print(f"Placed burner inserter at {inserter.position}")

    # Rotate the inserter to face the chest to put items into it not take from it
    inserter = rotate_entity(inserter, Direction.LEFT)
    print(f"Rotated inserter to face right")

    # Step 6: Connect the inserter to the drills drop position using transport belts
    belts = connect_entities(miner_with_coal.drop_position, inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to connect inserter to chest with transport belts"
    print(f"Connected inserter to chest with {len(belts)} transport belts")

    # Step 7: Fuel the inserter with coal
    inserter_with_coal = insert_item(Prototype.Coal, inserter, quantity=5)
    print(f"Fuelled inserter with coal: {inserter_with_coal}")

    # Step 8: Wait for some time to allow the system to mine stone
    print("Waiting for 30 seconds to allow mining...")
    sleep(30)

    # Step 9: Check if stone has been deposited in the chest
    chest_inventory = inspect_inventory(chest)
    stone_in_chest = chest_inventory.get(Prototype.Stone, 0)
    assert stone_in_chest > 0, f"No stone was mined. Stone in chest: {stone_in_chest}"
    print(f"Successfully mined {stone_in_chest} stone!")

    print("Automated stone mine created successfully!")


###FUNC SEP

create_stone_mine()