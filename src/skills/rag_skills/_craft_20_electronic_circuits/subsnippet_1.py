def craft_20_electronic_circuits():
    """
    Objective: Craft 20 electronic circuits. The final success should be checked by looking if 10 electronic circuits are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for electronic circuits
    # 2. Calculate the required resources (copper plates and iron plates)
    # 3. Mine the necessary copper ore and iron ore
    # 4. Craft a stone furnace to smelt the ores
    # 5. Smelt copper plates and iron plates
    # 6. Craft copper cables
    # 7. Craft the electronic circuits
    # 8. Verify the success of the operation
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check the recipe for electronic circuits
    circuit_recipe = get_prototype_recipe(Prototype.ElectronicCircuit)
    print(f"Electronic circuit recipe: {circuit_recipe}")

    # Calculate required resources
    copper_plates_needed = 20 * 2  # 2 copper plates per circuit (3 cables = 1.5 plates, rounded up to 2)
    iron_plates_needed = 20 * 1   # 1 iron plate per circuit

    # """[SYNTHESISED]
    # Name: mine_and_smelt_resource
    # Objective: Mine a specific resource and smelt it into plates
    # Mining setup: No existing setup
    # Inventory: Empty
    # :param resource: The resource to mine (Resource.CopperOre or Resource.IronOre)
    # :param quantity: The number of plates to produce
    # :return: None
    # [END OF SYNTHESISED]"""
    mine_and_smelt_resource(resource=Resource.CopperOre, quantity=copper_plates_needed)
    mine_and_smelt_resource(resource=Resource.IronOre, quantity=iron_plates_needed)

    print(f"Inventory after mining and smelting: {inspect_inventory()}")

    # Craft copper cables
    copper_cables_needed = 20 * 3  # 3 copper cables per circuit
    craft_item(Prototype.CopperCable, copper_cables_needed // 2)  # Crafting produces 2 cables at a time
    
    print(f"Inventory after crafting copper cables: {inspect_inventory()}")

    # Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 20)

    # Verify the success of the operation
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    
    circuits_crafted = final_inventory.get(Prototype.ElectronicCircuit, 0)
    assert circuits_crafted >= 20, f"Failed to craft 20 electronic circuits. Only crafted {circuits_crafted}"
    
    print("Successfully crafted 20 electronic circuits!")