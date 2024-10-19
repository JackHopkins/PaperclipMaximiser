def craft_3_stone_furnace():
    """
    Objective: Craft 3 stone furnaces. The final success should be checked by looking if 3 stone furnaces are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for Stone Furnace
    # 2. Mine the required amount of stone (15 for 3 furnaces, plus extra for safety)
    # 3. Craft the Stone Furnaces
    # 4. Verify that we have 3 Stone Furnaces in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    furnace_recipe = get_prototype_recipe(Prototype.StoneFurnace)
    print(f"Stone Furnace recipe: {furnace_recipe}")

    # Step 1: Mine stone
    stone_needed = 15  # 5 stone per furnace * 3 furnaces
    extra_stone = 5  # Mine extra to be safe
    total_stone_to_mine = stone_needed + extra_stone

    stone_position = nearest(Resource.Stone)
    print(f"Moving to stone deposit at {stone_position}")
    move_to(stone_position)

    print(f"Mining {total_stone_to_mine} stone")
    harvest_resource(stone_position, total_stone_to_mine)

    # Check if we have enough stone
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= stone_needed, f"Failed to mine enough stone. Expected at least {stone_needed}, but got {stone_count}"
    print(f"Successfully mined {stone_count} stone")

    # Step 2: Craft Stone Furnaces
    print("Crafting 3 Stone Furnaces")
    craft_item(Prototype.StoneFurnace, 3)

    # Step 3: Verify crafting success
    inventory = inspect_inventory()
    furnace_count = inventory[Prototype.StoneFurnace]
    assert furnace_count == 3, f"Failed to craft 3 Stone Furnaces. Crafted {furnace_count} instead."

    print(f"Final inventory: {inventory}")
    print("Successfully crafted 3 Stone Furnaces!")