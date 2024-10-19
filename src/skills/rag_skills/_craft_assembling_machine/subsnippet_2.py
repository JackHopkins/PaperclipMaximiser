def craft_assembling_machine():
    """
    Objective: Craft one AssemblingMachine. The final success should be checked by looking if a AssemblingMachine is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for AssemblingMachine
    # 2. Mine necessary resources: iron ore, copper ore, stone
    # 3. Craft stone furnaces for smelting
    # 4. Smelt iron plates and copper plates
    # 5. Craft intermediate products: iron gear wheels, electronic circuits
    # 6. Craft the AssemblingMachine
    # 7. Verify success by checking inventory
    # [END OF PLANNING]

    # Print initial information
    assembling_machine_recipe = get_prototype_recipe(Prototype.AssemblingMachine)
    print(f"AssemblingMachine recipe: {assembling_machine_recipe}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine necessary resources
    # We need more than required to account for inefficiencies
    """[SYNTHESISED]
    Name: mine_resources
    Objective: Mine iron ore, copper ore, and stone
    Mining setup: No entities on the map
    Inventory: Empty inventory
    :param iron_amount: Amount of iron ore to mine
    :param copper_amount: Amount of copper ore to mine
    :param stone_amount: Amount of stone to mine
    :return: None
    [END OF SYNTHESISED]"""
    mine_resources(iron_amount=35, copper_amount=10, stone_amount=10)

    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")

    # Step 3: Smelt iron plates and copper plates
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    furnace_iron = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    
    """[SYNTHESISED]
    Name: smelt_ore
    Objective: Smelt ore into plates using a furnace
    Mining setup: A furnace is placed on the map
    Inventory: We have ore and coal in the inventory
    :param furnace: The furnace entity to use for smelting
    :param ore_type: The type of ore to smelt (iron or copper)
    :param amount: The amount of ore to smelt
    :return: None
    [END OF SYNTHESISED]"""
    smelt_ore(furnace=furnace_iron, ore_type=Resource.IronOre, amount=30)

    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    furnace_copper = place_entity(Prototype.StoneFurnace, Direction.UP, copper_position)
    smelt_ore(furnace=furnace_copper, ore_type=Resource.CopperOre, amount=10)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft intermediate products
    craft_item(Prototype.IronGearWheel, 5)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count >= 5, f"Failed to craft iron gear wheels. Expected 5, but got {gear_count}"
    print(f"Crafted {gear_count} iron gear wheels")

    craft_item(Prototype.ElectronicCircuit, 3)
    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
    assert circuit_count >= 3, f"Failed to craft electronic circuits. Expected 3, but got {circuit_count}"
    print(f"Crafted {circuit_count} electronic circuits")

    # Step 5: Craft the AssemblingMachine
    craft_item(Prototype.AssemblingMachine, 1)
    
    # Verify success
    final_inventory = inspect_inventory()
    assembling_machine_count = final_inventory.get(Prototype.AssemblingMachine, 0)
    assert assembling_machine_count >= 1, f"Failed to craft AssemblingMachine. Expected 1, but got {assembling_machine_count}"
    
    print(f"Successfully crafted 1 AssemblingMachine!")
    print(f"Final inventory: {final_inventory}")