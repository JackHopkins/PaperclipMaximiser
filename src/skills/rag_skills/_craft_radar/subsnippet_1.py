def craft_radar():
    """
    Objective: Craft one Radar. The final success should be checked by looking if a Radar is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft a Radar, we need:
    # - 5 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # - 5 iron gear wheels (each requiring 2 iron plates)
    # - 10 iron plates
    # 
    # Total raw materials needed:
    # - 30 iron plates (10 for radar + 10 for gear wheels + 5 for electronic circuits + 5 for copper cables)
    # - 15 copper plates (for electronic circuits)
    # 
    # Steps:
    # 1. Mine iron ore and copper ore
    # 2. Craft a stone furnace to smelt the ores
    # 3. Smelt iron plates and copper plates
    # 4. Craft copper cables
    # 5. Craft electronic circuits
    # 6. Craft iron gear wheels
    # 7. Finally, craft the radar
    # [END OF PLANNING]

    print("Starting to craft a Radar")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine resources
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 40)  # Mine extra to be safe
    
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    harvest_resource(copper_position, 20)  # Mine extra to be safe
    
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # For crafting furnaces

    print(f"Resources mined. Current inventory: {inspect_inventory()}")

    # Step 2: Craft stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    print(f"Stone furnaces crafted. Current inventory: {inspect_inventory()}")

    # Step 3: Smelt iron plates and copper plates
    """[SYNTHESISED]
    Name: smelt_plates
    Objective: Smelt the required number of iron and copper plates using two furnaces
    Mining setup: We have two stone furnaces placed on the map
    Inventory: We have iron ore, copper ore, and coal in the inventory
    :param iron_ore_count: The number of iron ore to smelt
    :param copper_ore_count: The number of copper ore to smelt
    :return: None
    [END OF SYNTHESISED]"""
    smelt_plates(iron_ore_count=30, copper_ore_count=15)

    print(f"Plates smelted. Current inventory: {inspect_inventory()}")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 15)
    print(f"Copper cables crafted. Current inventory: {inspect_inventory()}")

    # Step 5: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 5)
    print(f"Electronic circuits crafted. Current inventory: {inspect_inventory()}")

    # Step 6: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 5)
    print(f"Iron gear wheels crafted. Current inventory: {inspect_inventory()}")

    # Step 7: Craft the radar
    craft_item(Prototype.Radar, 1)
    print(f"Radar crafted. Final inventory: {inspect_inventory()}")

    # Check if we have successfully crafted a Radar
    radar_count = inspect_inventory().get(Prototype.Radar, 0)
    assert radar_count >= 1, f"Failed to craft Radar. Expected at least 1, but got {radar_count}"

    print("Successfully crafted one Radar!")