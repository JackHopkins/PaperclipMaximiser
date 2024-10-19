def mine_resources(iron_amount: int, stone_amount: int) -> None:
    """
    Objective: Mine iron ore and stone
    Mining setup: No entities on the map
    Inventory: Empty
    :param iron_amount: Amount of iron ore to mine
    :param stone_amount: Amount of stone to mine
    :return: None
    """
    # [PLANNING]
    # 1. Find and move to the nearest iron ore patch
    # 2. Mine the required amount of iron ore
    # 3. Find and move to the nearest stone patch
    # 4. Mine the required amount of stone
    # 5. Verify that we have mined the correct amounts
    # [END OF PLANNING]

    print(f"Starting to mine resources. Target: {iron_amount} iron ore, {stone_amount} stone")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Find and move to the nearest iron ore patch
    iron_position = nearest(Resource.IronOre)
    assert iron_position, "No iron ore found nearby"
    move_to(iron_position)
    print(f"Moved to iron ore patch at {iron_position}")

    # Step 2: Mine the required amount of iron ore
    iron_mined = harvest_resource(iron_position, iron_amount)
    print(f"Mined {iron_mined} iron ore")

    # Step 3: Find and move to the nearest stone patch
    stone_position = nearest(Resource.Stone)
    assert stone_position, "No stone found nearby"
    move_to(stone_position)
    print(f"Moved to stone patch at {stone_position}")

    # Step 4: Mine the required amount of stone
    stone_mined = harvest_resource(stone_position, stone_amount)
    print(f"Mined {stone_mined} stone")

    # Step 5: Verify that we have mined the correct amounts
    inventory = inspect_inventory()
    iron_in_inventory = inventory.get(Resource.IronOre, 0)
    stone_in_inventory = inventory.get(Resource.Stone, 0)

    print(f"Final inventory: {inventory}")

    assert iron_in_inventory >= iron_amount, f"Failed to mine enough iron ore. Expected {iron_amount}, but got {iron_in_inventory}"
    assert stone_in_inventory >= stone_amount, f"Failed to mine enough stone. Expected {stone_amount}, but got {stone_in_inventory}"

    print(f"Successfully mined {iron_in_inventory} iron ore and {stone_in_inventory} stone")