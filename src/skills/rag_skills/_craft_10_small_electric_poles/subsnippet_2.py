def craft_10_small_electric_poles():
    """
    Objective: Craft 10 small electric poles. The final success should be checked by looking if 10 small electric poles are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for small electric poles
    # 2. Calculate the required resources (copper plates and wood)
    # 3. Mine copper ore and harvest wood
    # 4. Smelt copper ore into copper plates
    # 5. Craft copper cables
    # 6. Craft small electric poles
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Step 1: Check the recipe for small electric poles
    pole_recipe = get_prototype_recipe(Prototype.SmallElectricPole)
    print(f"Small Electric Pole recipe: {pole_recipe}")

    # Step 2: Calculate required resources
    # We need to craft 10 poles, each requiring 1 copper plate and 1 wood
    required_copper_plates = 5  # (10 poles * 1 copper plate per 2 poles)
    required_wood = 10

    # Step 3: Mine copper ore and harvest wood
    # """[SYNTHESISED]
    # Name: harvest_resources
    # Objective: Harvest the specified amount of a given resource
    # Mining setup: No existing mining setup
    # Inventory: Empty
    # :param resource: The resource to harvest (Resource enum)
    # :param amount: The amount of resource to harvest
    # :return: None
    # [END OF SYNTHESISED]"""
    harvest_resources(Resource.CopperOre, required_copper_plates)
    harvest_resources(Resource.Wood, required_wood)

    print(f"Current inventory after harvesting: {inspect_inventory()}")

    # Step 4: Smelt copper ore into copper plates
    # """[SYNTHESISED]
    # Name: smelt_copper_plates
    # Objective: Smelt copper ore into copper plates using a stone furnace
    # Mining setup: No existing furnaces
    # Inventory: Copper ore and some stone available
    # :param copper_ore_amount: The amount of copper ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_copper_plates(required_copper_plates)

    print(f"Current inventory after smelting: {inspect_inventory()}")

    # Step 5: Craft copper cables
    copper_cable_amount = required_copper_plates * 2  # Each copper plate produces 2 copper cables
    craft_item(Prototype.CopperCable, copper_cable_amount)

    print(f"Current inventory after crafting copper cables: {inspect_inventory()}")

    # Step 6: Craft small electric poles
    craft_item(Prototype.SmallElectricPole, 10)

    # Step 7: Verify the crafting was successful
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")

    crafted_poles = final_inventory.get(Prototype.SmallElectricPole, 0)
    assert crafted_poles >= 10, f"Failed to craft 10 small electric poles. Crafted: {crafted_poles}"

    print("Successfully crafted 10 small electric poles!")