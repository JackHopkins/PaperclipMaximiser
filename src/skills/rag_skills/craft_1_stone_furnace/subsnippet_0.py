def craft_1_stone_furnace():
    """
    Objective: Craft 1 stone furnace. The final success should be checked by looking if the stone furnace is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for stone furnace
    # 2. Mine the required amount of stone (5 stone + extra for safety)
    # 3. Craft the stone furnace
    # 4. Verify that the stone furnace is in the inventory
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Check the recipe for stone furnace
    stone_furnace_recipe = get_prototype_recipe(Prototype.StoneFurnace)
    print(f"Stone Furnace recipe: {stone_furnace_recipe}")

    # Step 2: Mine the required amount of stone
    stone_to_mine = 7  # 5 required + 2 extra for safety
    stone_position = nearest(Resource.Stone)
    print(f"Moving to stone deposit at {stone_position}")
    move_to(stone_position)
    
    harvest_resource(stone_position, stone_to_mine)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Successfully mined {stone_count} stone")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 3: Craft the stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    
    # Step 4: Verify that the stone furnace is in the inventory
    final_inventory = inspect_inventory()
    stone_furnace_count = final_inventory[Prototype.StoneFurnace]
    assert stone_furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {stone_furnace_count}"
    
    print("Successfully crafted 1 stone furnace!")
    print(f"Final inventory: {final_inventory}")