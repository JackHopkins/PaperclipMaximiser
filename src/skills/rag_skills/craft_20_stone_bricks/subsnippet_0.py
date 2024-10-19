def smelt_stone_bricks(input_coal: int, input_stone: int, furnace: Entity):
    """
    Objective: Smelt stone into stone bricks using a furnace
    Mining setup: We have a furnace on the map that we can use to smelt stone
    Inventory: We have enough stone and coal in the inventory to smelt the stone bricks
    :param input_coal: The number of coal to insert into the furnace
    :param input_stone: The number of stone to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None as the stone bricks will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough stone and coal in the inventory
    # 2. Insert coal and stone into the furnace
    # 3. Wait for smelting to complete
    # 4. Extract stone bricks from the furnace
    # 5. Verify that we have the expected number of stone bricks in the inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough stone and coal in the inventory
    stone_in_inventory = inspect_inventory()[Prototype.Stone]
    coal_in_inventory = inspect_inventory()[Prototype.Coal]
    assert stone_in_inventory >= input_stone, f"Not enough stone in inventory. Expected {input_stone}, but got {stone_in_inventory}"
    assert coal_in_inventory >= input_coal, f"Not enough coal in inventory. Expected {input_coal}, but got {coal_in_inventory}"

    # Insert coal and stone into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.Stone, furnace, input_stone)
    print(f"Inserted {input_coal} coal and {input_stone} stone into the furnace")
    print(f"Inventory after inserting: {inspect_inventory()}")

    # Get the initial number of stone bricks in the inventory
    initial_stone_bricks = inspect_inventory()[Prototype.StoneBrick]

    # Wait for smelting to complete (2 stone per brick, 3.2 seconds per brick)
    smelting_time = (input_stone / 2) * 3.2
    sleep(smelting_time)

    # Extract stone bricks from the furnace
    expected_bricks = input_stone // 2  # 2 stone makes 1 brick
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.StoneBrick, furnace.position, expected_bricks)
        stone_bricks_in_inventory = inspect_inventory()[Prototype.StoneBrick]
        stone_bricks_smelted = stone_bricks_in_inventory - initial_stone_bricks
        if stone_bricks_smelted >= expected_bricks:
            break
        sleep(5)  # Wait a bit more if not all bricks are ready

    print(f"Extracted {stone_bricks_smelted} stone bricks from the furnace")
    print(f"Inventory after extracting: {inspect_inventory()}")

    # Verify that we have the expected number of stone bricks in the inventory
    final_stone_bricks = inspect_inventory()[Prototype.StoneBrick]
    assert final_stone_bricks >= initial_stone_bricks + expected_bricks, f"Failed to smelt enough stone bricks. Expected at least {initial_stone_bricks + expected_bricks}, but got {final_stone_bricks}"

    print(f"Successfully smelted {stone_bricks_smelted} stone bricks!")