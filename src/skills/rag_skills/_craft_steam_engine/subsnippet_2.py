def craft_steam_engine():
    """
    Objective: Craft one SteamEngine. The final success should be checked by looking if a SteamEngine is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for SteamEngine
    # 2. Mine necessary resources: iron ore and stone
    # 3. Craft stone furnaces for smelting
    # 4. Smelt iron plates
    # 5. Craft iron gear wheels
    # 6. Craft pipes
    # 7. Finally, craft the steam engine
    # 8. Verify that the steam engine is in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    steam_engine_recipe = get_prototype_recipe(Prototype.SteamEngine)
    print(f"Steam Engine recipe: {steam_engine_recipe}")

    # Step 1: Mine necessary resources
    # We need iron for plates, gear wheels, and pipes. We'll mine extra to be safe.
    """[SYNTHESISED]
    Name: mine_resources
    Objective: Mine iron ore and stone
    Mining setup: No entities on the map
    Inventory: Empty
    :param iron_amount: Amount of iron ore to mine
    :param stone_amount: Amount of stone to mine
    :return: None
    [END OF SYNTHESISED]"""
    mine_resources(iron_amount=70, stone_amount=15)

    print(f"After mining resources: {inspect_inventory()}")

    # Step 2: Craft stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")

    # Step 3: Smelt iron plates
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    
    """[SYNTHESISED]
    Name: smelt_iron_with_furnace
    Objective: Smelt iron ore into iron plates using a furnace
    Mining setup: One stone furnace placed near iron ore
    Inventory: Contains iron ore and coal
    :param input_coal: Amount of coal to insert into the furnace
    :param input_iron_ore: Amount of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None
    [END OF SYNTHESISED]"""
    smelt_iron_with_furnace(input_coal=20, input_iron_ore=60, furnace=furnace)

    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 50, f"Failed to smelt enough iron plates. Expected at least 50, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Step 4: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 8)
    gear_wheels = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheels >= 8, f"Failed to craft enough iron gear wheels. Expected 8, but got {gear_wheels}"
    print(f"Crafted {gear_wheels} iron gear wheels")

    # Step 5: Craft pipes
    craft_item(Prototype.Pipe, 5)
    pipes = inspect_inventory()[Prototype.Pipe]
    assert pipes >= 5, f"Failed to craft enough pipes. Expected 5, but got {pipes}"
    print(f"Crafted {pipes} pipes")

    # Step 6: Craft the steam engine
    craft_item(Prototype.SteamEngine, 1)
    steam_engine_count = inspect_inventory()[Prototype.SteamEngine]
    assert steam_engine_count == 1, f"Failed to craft steam engine. Expected 1, but got {steam_engine_count}"
    print("Successfully crafted 1 Steam Engine!")

    # Final inventory check
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    assert Prototype.SteamEngine in final_inventory and final_inventory[Prototype.SteamEngine] == 1, "Steam Engine not found in inventory"
    print("Objective completed: Crafted one Steam Engine and verified it's in the inventory.")