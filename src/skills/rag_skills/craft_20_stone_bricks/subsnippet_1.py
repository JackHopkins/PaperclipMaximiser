def craft_20_stone_bricks():
    """
    Objective: Craft 20 stone bricks. The final success should be checked by looking if 20 stone bricks are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Mine stone (we need at least 40 stone, but let's mine 50 to be safe)
    # 2. Craft a stone furnace (requires 5 stone)
    # 3. Mine some coal for fuel (let's mine 10 to be safe)
    # 4. Place the stone furnace
    # 5. Smelt the stone into stone bricks
    # 6. Check if we have 20 stone bricks in the inventory
    # [END OF PLANNING]

    print("Starting to craft 20 stone bricks")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 50)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 50, f"Failed to mine enough stone. Expected 50, but got {stone_count}"
    print(f"Mined {stone_count} stone")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 2: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 3: Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 10)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 10, f"Failed to mine enough coal. Expected 10, but got {coal_count}"
    print(f"Mined {coal_count} coal")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 4: Place the stone furnace
    furnace_position = Position(x=coal_position.x + 2, y=coal_position.y)
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, position=furnace_position, direction=Direction.UP)
    print(f"Placed stone furnace at {furnace_position}")

    # Step 5: Smelt the stone into stone bricks
    # """[SYNTHESISED]
    # Name: smelt_stone_bricks
    # Objective: Smelt stone into stone bricks using a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt stone
    # Inventory: We have enough stone and coal in the inventory to smelt the stone bricks
    # :param input_coal: The number of coal to insert into the furnace
    # :param input_stone: The number of stone to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the stone bricks will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_stone_bricks(input_coal=10, input_stone=40, furnace=furnace)
    
    print("Smelted stone into stone bricks")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 6: Check if we have 20 stone bricks in the inventory
    stone_bricks_count = inspect_inventory()[Prototype.StoneBrick]
    assert stone_bricks_count >= 20, f"Failed to craft enough stone bricks. Expected 20, but got {stone_bricks_count}"
    
    print(f"Successfully crafted {stone_bricks_count} stone bricks!")
    print(f"Final inventory: {inspect_inventory()}")