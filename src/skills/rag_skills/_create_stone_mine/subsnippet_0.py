def create_stone_mine():
    """
    Objective: We need create an automated stone mine that mines stone to a chest further away and right from it. 
    The final setup should be checked by looking if the chest has any stone in it.
    Mining setup: There are no entities on the map
    Inventory: We have all the required mining items in our inventory including burner mining drills, 
    burner inserters, transport belts, and a wooden chest.
    """
    # [PLANNING]
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

    # Step 5: Place a burner inserter next to the drill to pick up the stone
    inserter = place_entity_next_to(Prototype.BurnerInserter, miner.position, direction=Direction.RIGHT, spacing=0)
    assert inserter, "Failed to place burner inserter"
    print(f"Placed burner inserter at {inserter.position}")

    # Rotate the inserter to face the transport belt (which will be placed next)
    inserter = rotate_entity(inserter, Direction.RIGHT)
    print(f"Rotated inserter to face right")

    # Step 6: Connect the inserter to the chest using transport belts
    belts = connect_entities(inserter.drop_position, chest.position, Prototype.TransportBelt)
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