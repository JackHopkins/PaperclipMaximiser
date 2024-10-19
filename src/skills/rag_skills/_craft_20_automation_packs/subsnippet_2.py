def craft_20_automation_packs():
    """
    Objective: Craft 20 automation science packs. The final success should be checked by looking if 20 automation science packs are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for automation science packs
    # 2. Calculate the total resources needed
    # 3. Mine the necessary resources (iron ore and copper ore)
    # 4. Craft iron plates and copper plates
    # 5. Craft iron gear wheels
    # 6. Craft the automation science packs
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    automation_pack_recipe = get_prototype_recipe(Prototype.AutomationSciencePack)
    print(f"Automation Science Pack recipe: {automation_pack_recipe}")

    # Calculate total resources needed
    iron_plates_needed = 20 * 2  # 1 for the pack, 1 for the gear wheel
    copper_plates_needed = 20

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, iron_plates_needed + 5)  # Extra 5 for safety
    print(f"Mined {iron_mined} iron ore")

    # Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    copper_mined = harvest_resource(copper_position, copper_plates_needed + 5)  # Extra 5 for safety
    print(f"Mined {copper_mined} copper ore")

    # """[SYNTHESISED]
    # Name: smelt_ores
    # Objective: Smelt iron and copper ores into plates
    # Mining setup: No existing setup
    # Inventory: We have iron and copper ores in the inventory
    # :param iron_ore_count: The number of iron ores to smelt
    # :param copper_ore_count: The number of copper ores to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_ores(iron_ore_count=iron_plates_needed, copper_ore_count=copper_plates_needed)

    # Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 20)
    iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert iron_gear_count >= 20, f"Failed to craft enough iron gear wheels. Expected 20, got {iron_gear_count}"
    print(f"Crafted {iron_gear_count} iron gear wheels")

    # Craft automation science packs
    craft_item(Prototype.AutomationSciencePack, 20)
    
    # Verify crafting success
    final_inventory = inspect_inventory()
    automation_pack_count = final_inventory.get(Prototype.AutomationSciencePack, 0)
    assert automation_pack_count >= 20, f"Failed to craft 20 automation science packs. Crafted: {automation_pack_count}"
    
    print(f"Successfully crafted {automation_pack_count} automation science packs!")
    print(f"Final inventory: {final_inventory}")