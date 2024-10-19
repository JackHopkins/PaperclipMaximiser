def craft_offshore_pump():
    """
    Objective: Craft one OffshorePump. The final success should be checked by looking if a OffshorePump is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft an OffshorePump, we need:
    # 1. 2 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # 2. 1 iron gear wheel (requiring 2 iron plates)
    # 3. 1 pipe (requiring 1 iron plate)
    # In total, we need to mine and craft:
    # - 5 iron ore (for 5 iron plates)
    # - 3 copper ore (for 3 copper plates)
    # We'll mine a bit extra to account for any inefficiencies.
    # [END OF PLANNING]

    print("Starting to craft an OffshorePump")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, 7)
    print(f"Mined {iron_mined} iron ore")

    # Step 2: Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    copper_mined = harvest_resource(copper_position, 5)
    print(f"Mined {copper_mined} copper ore")

    # Step 3: Craft iron plates
    """[SYNTHESISED]
    Name: smelt_ore_into_plates
    Objective: Smelt iron ore into iron plates
    Mining setup: No existing setup
    Inventory: We have iron ore in our inventory
    :param ore_type: The type of ore to smelt (Iron or Copper)
    :param quantity: The number of plates to produce
    :return: None
    [END OF SYNTHESISED]"""
    smelt_ore_into_plates(ore_type=Resource.IronOre, quantity=5)
    
    # Step 4: Craft copper plates
    smelt_ore_into_plates(ore_type=Resource.CopperOre, quantity=3)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 5: Craft copper cables
    craft_item(Prototype.CopperCable, 6)
    copper_cable_count = inspect_inventory()[Prototype.CopperCable]
    assert copper_cable_count >= 6, f"Failed to craft enough copper cables. Expected 6, got {copper_cable_count}"
    print(f"Crafted {copper_cable_count} copper cables")

    # Step 6: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 2)
    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
    assert circuit_count >= 2, f"Failed to craft enough electronic circuits. Expected 2, got {circuit_count}"
    print(f"Crafted {circuit_count} electronic circuits")

    # Step 7: Craft iron gear wheel
    craft_item(Prototype.IronGearWheel, 1)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count >= 1, f"Failed to craft iron gear wheel. Expected 1, got {gear_count}"
    print(f"Crafted {gear_count} iron gear wheel")

    # Step 8: Craft pipe
    craft_item(Prototype.Pipe, 1)
    pipe_count = inspect_inventory()[Prototype.Pipe]
    assert pipe_count >= 1, f"Failed to craft pipe. Expected 1, got {pipe_count}"
    print(f"Crafted {pipe_count} pipe")

    # Step 9: Craft OffshorePump
    craft_item(Prototype.OffshorePump, 1)
    pump_count = inspect_inventory()[Prototype.OffshorePump]
    assert pump_count >= 1, f"Failed to craft OffshorePump. Expected 1, got {pump_count}"
    print(f"Successfully crafted {pump_count} OffshorePump")

    print(f"Final inventory: {inspect_inventory()}")
    print("Objective completed: Crafted one OffshorePump")