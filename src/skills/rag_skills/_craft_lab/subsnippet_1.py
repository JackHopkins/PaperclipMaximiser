def mine_raw_resources():
    """
    Objective: Mine the required raw resources for crafting a Lab
    Mining setup: No existing mining setup
    Inventory: Empty inventory
    :return: None (resources will be added to inventory)
    """
    # [PLANNING]
    # 1. Calculate the required resources for a Lab
    # 2. Mine iron ore (for iron plates, iron gear wheels, and electronic circuits)
    # 3. Mine copper ore (for electronic circuits)
    # 4. Mine stone (for stone furnaces to smelt the ores)
    # 5. Mine coal (for fuel)
    # 6. Verify that we have mined enough resources
    # [END OF PLANNING]

    # Calculate required resources
    iron_ore_needed = 36 + 5  # 36 for iron plates and gear wheels, 5 for extra
    copper_ore_needed = 15 + 5  # 15 for copper plates, 5 for extra
    stone_needed = 10 + 5  # 10 for two furnaces, 5 for extra
    coal_needed = 20  # Extra for fueling furnaces

    print(f"Starting to mine resources for Lab. Initial inventory: {inspect_inventory()}")

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, iron_ore_needed)
    print(f"Mined {iron_mined} iron ore")

    # Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    copper_mined = harvest_resource(copper_position, copper_ore_needed)
    print(f"Mined {copper_mined} copper ore")

    # Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    stone_mined = harvest_resource(stone_position, stone_needed)
    print(f"Mined {stone_mined} stone")

    # Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    coal_mined = harvest_resource(coal_position, coal_needed)
    print(f"Mined {coal_mined} coal")

    # Verify mined resources
    inventory = inspect_inventory()
    assert inventory[Resource.IronOre] >= iron_ore_needed, f"Not enough iron ore. Expected {iron_ore_needed}, got {inventory[Resource.IronOre]}"
    assert inventory[Resource.CopperOre] >= copper_ore_needed, f"Not enough copper ore. Expected {copper_ore_needed}, got {inventory[Resource.CopperOre]}"
    assert inventory[Resource.Stone] >= stone_needed, f"Not enough stone. Expected {stone_needed}, got {inventory[Resource.Stone]}"
    assert inventory[Resource.Coal] >= coal_needed, f"Not enough coal. Expected {coal_needed}, got {inventory[Resource.Coal]}"

    print(f"Successfully mined all required resources. Final inventory: {inventory}")
    print("Raw resource mining for Lab completed successfully!")