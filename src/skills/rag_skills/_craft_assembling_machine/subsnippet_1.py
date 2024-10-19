def mine_resources(iron_amount: int, copper_amount: int, stone_amount: int) -> None:
    """
    Mine iron ore, copper ore, and stone
    :param iron_amount: Amount of iron ore to mine
    :param copper_amount: Amount of copper ore to mine
    :param stone_amount: Amount of stone to mine
    :return: None
    """
    # [PLANNING]
    # 1. Find and mine iron ore
    # 2. Find and mine copper ore
    # 3. Find and mine stone
    # 4. Verify that we have mined the correct amounts
    # [END OF PLANNING]

    print(f"Starting mining operation. Target amounts - Iron: {iron_amount}, Copper: {copper_amount}, Stone: {stone_amount}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    print(f"Moving to iron ore patch at {iron_position}")
    iron_mined = harvest_resource(iron_position, iron_amount)
    print(f"Mined {iron_mined} iron ore")

    # Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    print(f"Moving to copper ore patch at {copper_position}")
    copper_mined = harvest_resource(copper_position, copper_amount)
    print(f"Mined {copper_mined} copper ore")

    # Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    print(f"Moving to stone patch at {stone_position}")
    stone_mined = harvest_resource(stone_position, stone_amount)
    print(f"Mined {stone_mined} stone")

    # Verify mined amounts
    inventory = inspect_inventory()
    iron_in_inventory = inventory.get(Resource.IronOre, 0)
    copper_in_inventory = inventory.get(Resource.CopperOre, 0)
    stone_in_inventory = inventory.get(Resource.Stone, 0)

    print(f"Final inventory: {inventory}")

    assert iron_in_inventory >= iron_amount, f"Failed to mine enough iron ore. Expected {iron_amount}, but got {iron_in_inventory}"
    assert copper_in_inventory >= copper_amount, f"Failed to mine enough copper ore. Expected {copper_amount}, but got {copper_in_inventory}"
    assert stone_in_inventory >= stone_amount, f"Failed to mine enough stone. Expected {stone_amount}, but got {stone_in_inventory}"

    print(f"Successfully mined {iron_in_inventory} iron ore, {copper_in_inventory} copper ore, and {stone_in_inventory} stone.")