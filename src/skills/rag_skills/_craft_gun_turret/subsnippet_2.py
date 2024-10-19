def craft_gun_turret():
    """
    Objective: Craft one GunTurret. The final success should be checked by looking if a GunTurret is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for GunTurret
    # 2. Mine necessary resources: iron ore and copper ore
    # 3. Craft a stone furnace to smelt the ores
    # 4. Smelt iron plates and copper plates
    # 5. Craft iron gear wheels
    # 6. Craft the GunTurret
    # 7. Verify that the GunTurret is in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    gun_turret_recipe = get_prototype_recipe(Prototype.GunTurret)
    print(f"GunTurret recipe: {gun_turret_recipe}")

    # Step 1: Mine necessary resources
    # We need 40 iron plates (20 for plates, 20 for gear wheels) and 10 copper plates
    # Let's mine a bit extra to account for inefficiencies
    """[SYNTHESISED]
    # Name: mine_resources
    # Objective: Mine the specified amount of resources
    # Mining setup: No existing mining setup
    # Inventory: Empty
    # :param resource: The resource to mine (e.g., Resource.IronOre)
    # :param amount: The amount of resource to mine
    # :return: None
    [END OF SYNTHESISED]"""
    mine_resources(resource=Resource.IronOre, amount=50)
    mine_resources(resource=Resource.CopperOre, amount=15)
    mine_resources(resource=Resource.Stone, amount=10)

    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 3: Smelt iron plates and copper plates
    """[SYNTHESISED]
    # Name: smelt_plates
    # Objective: Smelt the specified amount of plates
    # Mining setup: One stone furnace available
    # Inventory: Contains iron ore, copper ore, and stone furnace
    # :param ore_type: The type of ore to smelt (e.g., Resource.IronOre)
    # :param amount: The amount of plates to smelt
    # :return: None
    [END OF SYNTHESISED]"""
    smelt_plates(ore_type=Resource.IronOre, amount=40)
    smelt_plates(ore_type=Resource.CopperOre, amount=10)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 10)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count == 10, f"Failed to craft iron gear wheels. Expected 10, but got {gear_count}"
    print("Crafted 10 iron gear wheels")

    # Step 5: Craft the GunTurret
    craft_item(Prototype.GunTurret, 1)

    # Step 6: Verify that the GunTurret is in the inventory
    gun_turret_count = inspect_inventory()[Prototype.GunTurret]
    assert gun_turret_count == 1, f"Failed to craft GunTurret. Expected 1, but got {gun_turret_count}"
    
    print("Successfully crafted 1 GunTurret!")
    print(f"Final inventory: {inspect_inventory()}")