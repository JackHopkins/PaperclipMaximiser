def craft_10_transport_belts():
    """
    Objective: Craft 10 transport belts. The final success should be checked by looking if 10 transport belts are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for transport belts
    # 2. Calculate the required resources (iron plates and iron gear wheels)
    # 3. Mine iron ore
    # 4. Craft iron plates
    # 5. Craft iron gear wheels
    # 6. Craft transport belts
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check the recipe for transport belts
    transport_belt_recipe = get_prototype_recipe(Prototype.TransportBelt)
    print(f"Transport belt recipe: {transport_belt_recipe}")

    # Calculate required resources
    iron_plates_needed = 10  # 1 per 2 transport belts, so 5 * 2 = 10
    iron_gear_wheels_needed = 5  # 1 per 2 transport belts

    # Mine iron ore
    iron_ore_needed = iron_plates_needed + (iron_gear_wheels_needed * 2)
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, iron_ore_needed + 5)  # Mine a bit extra
    print(f"Mined {iron_mined} iron ore")

    # """[SYNTHESISED]
    # Name: smelt_iron_plates
    # Objective: Smelt iron ore into iron plates
    # Mining setup: No existing setup
    # Inventory: We have iron ore in the inventory
    # :param iron_ore_count: The number of iron ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_iron_plates(iron_ore_count=iron_mined)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= iron_plates_needed, f"Not enough iron plates. Have {iron_plates}, need {iron_plates_needed}"
    print(f"Smelted {iron_plates} iron plates")

    # Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, iron_gear_wheels_needed)
    iron_gear_wheels = inspect_inventory()[Prototype.IronGearWheel]
    assert iron_gear_wheels >= iron_gear_wheels_needed, f"Not enough iron gear wheels. Have {iron_gear_wheels}, need {iron_gear_wheels_needed}"
    print(f"Crafted {iron_gear_wheels} iron gear wheels")

    # Craft transport belts
    craft_item(Prototype.TransportBelt, 5)  # Craft 5 times to get 10 transport belts
    
    # Verify crafting was successful
    transport_belts = inspect_inventory()[Prototype.TransportBelt]
    assert transport_belts >= 10, f"Failed to craft 10 transport belts. Current count: {transport_belts}"
    print(f"Successfully crafted {transport_belts} transport belts!")
    
    # Print final inventory
    print(f"Final inventory: {inspect_inventory()}")

    return True