def craft_lab():
    """
    Objective: Craft one Lab. The final success should be checked by looking if a Lab is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft a Lab, we need:
    # - 10 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # - 10 iron gear wheels (each requiring 2 iron plates)
    # - 4 transport belts (each requiring 1 iron gear wheel and 1 iron plate)
    # 
    # Total raw materials needed:
    # - 15 copper plates (for electronic circuits)
    # - 36 iron plates (for electronic circuits, iron gear wheels, and transport belts)
    # - 5 stone (for a stone furnace to smelt the plates)
    # 
    # Steps:
    # 1. Mine raw resources (copper ore, iron ore, stone, coal)
    # 2. Craft stone furnace
    # 3. Smelt copper and iron plates
    # 4. Craft copper cables
    # 5. Craft electronic circuits
    # 6. Craft iron gear wheels
    # 7. Craft transport belts
    # 8. Finally, craft the Lab
    # [END OF PLANNING]

    print("Starting to craft a Lab from scratch.")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine raw resources
    """[SYNTHESISED]
    Name: mine_raw_resources
    Objective: Mine the required raw resources for crafting a Lab
    Mining setup: No existing mining setup
    Inventory: Empty inventory
    :return: None (resources will be added to inventory)
    [END OF SYNTHESISED]"""
    mine_raw_resources()

    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    assert inspect_inventory()[Prototype.StoneFurnace] >= 1, "Failed to craft stone furnace"
    print("Crafted 1 stone furnace")

    # Step 3: Smelt copper and iron plates
    """[SYNTHESISED]
    Name: smelt_plates
    Objective: Smelt copper and iron plates using the stone furnace
    Mining setup: One stone furnace available
    Inventory: Raw ores and coal available
    :param copper_plates_needed: Number of copper plates to smelt
    :param iron_plates_needed: Number of iron plates to smelt
    :return: None (plates will be added to inventory)
    [END OF SYNTHESISED]"""
    smelt_plates(copper_plates_needed=15, iron_plates_needed=36)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 30)  # We need 30 copper cables for 10 electronic circuits
    assert inspect_inventory()[Prototype.CopperCable] >= 30, "Failed to craft enough copper cables"
    print("Crafted 30 copper cables")

    # Step 5: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 10)
    assert inspect_inventory()[Prototype.ElectronicCircuit] >= 10, "Failed to craft enough electronic circuits"
    print("Crafted 10 electronic circuits")

    # Step 6: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 14)  # 10 for the Lab, 4 for transport belts
    assert inspect_inventory()[Prototype.IronGearWheel] >= 14, "Failed to craft enough iron gear wheels"
    print("Crafted 14 iron gear wheels")

    # Step 7: Craft transport belts
    craft_item(Prototype.TransportBelt, 4)
    assert inspect_inventory()[Prototype.TransportBelt] >= 4, "Failed to craft enough transport belts"
    print("Crafted 4 transport belts")

    # Step 8: Craft the Lab
    craft_item(Prototype.Lab, 1)
    lab_count = inspect_inventory()[Prototype.Lab]
    assert lab_count >= 1, f"Failed to craft a Lab. Current count: {lab_count}"
    print("Successfully crafted 1 Lab!")

    print(f"Final inventory: {inspect_inventory()}")
    print("Lab crafting process completed successfully.")