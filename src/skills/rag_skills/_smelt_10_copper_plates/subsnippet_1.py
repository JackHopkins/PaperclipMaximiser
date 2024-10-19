def craft_stone_furnace():
    """
    Objective: Craft a stone furnace
    Mining setup: There are no entities on the map
    Inventory: We should have enough stone to craft a furnace
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough stone in the inventory
    # 2. If we don't have enough stone, mine more
    # 3. Craft the stone furnace
    # 4. Verify that the stone furnace was crafted successfully
    # [END OF PLANNING]

    # Step 1: Check if we have enough stone in the inventory
    inventory = inspect_inventory()
    stone_count = inventory.get(Resource.Stone, 0)
    required_stone = 5  # Stone furnace requires 5 stone

    print(f"Current inventory: {inventory}")
    print(f"Stone count: {stone_count}")

    # Step 2: If we don't have enough stone, mine more
    if stone_count < required_stone:
        stone_to_mine = required_stone - stone_count
        stone_position = nearest(Resource.Stone)
        move_to(stone_position)
        print(f"Moving to stone deposit at {stone_position}")
        
        harvest_resource(stone_position, stone_to_mine)
        print(f"Mined {stone_to_mine} stone")
        
        # Verify that we now have enough stone
        updated_inventory = inspect_inventory()
        updated_stone_count = updated_inventory.get(Resource.Stone, 0)
        assert updated_stone_count >= required_stone, f"Failed to mine enough stone. Expected at least {required_stone}, but got {updated_stone_count}"
        print(f"Updated inventory: {updated_inventory}")

    # Step 3: Craft the stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    print("Crafted 1 stone furnace")

    # Step 4: Verify that the stone furnace was crafted successfully
    final_inventory = inspect_inventory()
    crafted_furnace_count = final_inventory.get(Prototype.StoneFurnace, 0)
    assert crafted_furnace_count >= 1, f"Failed to craft stone furnace. Expected at least 1, but got {crafted_furnace_count}"

    print(f"Final inventory: {final_inventory}")
    print("Successfully crafted a stone furnace!")