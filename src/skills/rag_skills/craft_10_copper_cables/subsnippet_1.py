def craft_10_copper_cables():
    """
    Objective: Craft 10 copper cables. The final success should be checked by looking if 10 copper cables are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for copper cables
    # 2. Mine copper ore
    # 3. Smelt copper ore into copper plates
    # 4. Craft copper cables
    # 5. Verify the final result
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Check the recipe for copper cables
    copper_cable_recipe = get_prototype_recipe(Prototype.CopperCable)
    print(f"Copper cable recipe: {copper_cable_recipe}")

    # Step 2: Mine copper ore
    # We need 5 copper plates to craft 10 copper cables, so we'll mine 6 copper ore to be safe
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    harvest_resource(copper_position, 6)
    copper_ore_count = inspect_inventory()[Resource.CopperOre]
    assert copper_ore_count >= 6, f"Failed to mine enough copper ore. Expected 6, but got {copper_ore_count}"
    print(f"Mined {copper_ore_count} copper ore")

    # Step 3: Smelt copper ore into copper plates
    # """[SYNTHESISED]
    # Name: smelt_copper_ore
    # Objective: Smelt copper ore into copper plates
    # Mining setup: No existing furnace on the map
    # Inventory: We have copper ore and coal in the inventory
    # :param input_copper_ore: The number of copper ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_copper_ore(input_copper_ore=6)
    
    copper_plate_count = inspect_inventory()[Prototype.CopperPlate]
    assert copper_plate_count >= 5, f"Failed to smelt enough copper plates. Expected 5, but got {copper_plate_count}"
    print(f"Smelted {copper_plate_count} copper plates")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 5)  # Crafts 10 copper cables (2 per craft)
    
    # Step 5: Verify the final result
    copper_cable_count = inspect_inventory()[Prototype.CopperCable]
    assert copper_cable_count >= 10, f"Failed to craft 10 copper cables. Current count: {copper_cable_count}"
    print(f"Successfully crafted {copper_cable_count} copper cables!")

    # Print final inventory
    print(f"Final inventory: {inspect_inventory()}")

    print("Successfully completed the objective: Crafted 10 copper cables!")