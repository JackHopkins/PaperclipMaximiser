def smelt_10_copper_plates():
    """
    Objective: Smelt 10 copper plates. The final success should be checked by looking if the copper plates are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Print initial inventory
    # 2. Find and mine copper ore (we'll mine 15 to account for inefficiencies)
    # 3. Find and mine coal for fuel (we'll mine 10 to ensure we have enough)
    # 4. Craft a stone furnace
    # 5. Place the stone furnace
    # 6. Fuel the furnace with coal
    # 7. Smelt the copper ore into plates
    # 8. Check if we have 10 copper plates in the inventory
    # [END OF PLANNING]

    # Step 1: Print initial inventory
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Step 2: Find and mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    harvest_resource(copper_position, 15)
    copper_ore_count = inspect_inventory()[Resource.CopperOre]
    assert copper_ore_count >= 15, f"Failed to mine enough copper ore. Expected 15, but got {copper_ore_count}"
    print(f"Mined {copper_ore_count} copper ore")

    # Step 3: Find and mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 10)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 10, f"Failed to mine enough coal. Expected 10, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 4: Craft a stone furnace
    # """[SYNTHESISED]
    # Name: craft_stone_furnace
    # Objective: Craft a stone furnace
    # Mining setup: There are no entities on the map
    # Inventory: We should have enough stone to craft a furnace
    # :return: None
    # [END OF SYNTHESISED]"""
    craft_stone_furnace()
    
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print(f"Crafted 1 stone furnace")

    # Step 5: Place the stone furnace
    current_position = inspect_entities().player_position
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=current_position[0], y=current_position[1]))
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 6: Fuel the furnace with coal
    insert_item(Prototype.Coal, furnace, 5)
    print("Inserted 5 coal into the furnace")

    # Step 7: Smelt the copper ore into plates
    # """[SYNTHESISED]
    # Name: smelt_copper_with_furnace
    # Objective: Smelt copper ore into copper plates using a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt copper ore
    # Inventory: We have enough copper ore in the inventory to smelt the copper plates
    # :param input_copper_ore: The number of copper ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the copper plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_copper_with_furnace(input_copper_ore=15, furnace=furnace)
    
    # Step 8: Check if we have 10 copper plates in the inventory
    final_inventory = inspect_inventory()
    copper_plates = final_inventory[Prototype.CopperPlate]
    assert copper_plates >= 10, f"Failed to smelt enough copper plates. Expected at least 10, but got {copper_plates}"
    
    print(f"Successfully smelted {copper_plates} copper plates!")
    print(f"Final inventory: {final_inventory}")