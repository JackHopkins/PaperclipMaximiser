def craft_20_firearm_magazines():
    """
    Objective: Craft 20 firearm magazines. The final success should be checked by looking if 20 firearm magazines are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for firearm magazines
    # 2. Calculate the total iron plates needed (4 * 20 = 80)
    # 3. Mine iron ore (we'll mine extra to account for inefficiencies)
    # 4. Craft a stone furnace to smelt iron plates
    # 5. Smelt iron plates
    # 6. Craft firearm magazines
    # 7. Verify the final count of firearm magazines in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    firearm_magazine_recipe = get_prototype_recipe(Prototype.FirearmMagazine)
    print(f"Firearm Magazine recipe: {firearm_magazine_recipe}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 100)  # Mining extra to account for inefficiencies
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 80, f"Failed to mine enough iron ore. Expected at least 80, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Mine stone for furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # Mining extra to account for inefficiencies
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # Step 3: Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 4: Place furnace and smelt iron plates
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace. We need to use an input furnace variable
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=80, furnace=furnace)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 80, f"Failed to smelt enough iron plates. Expected at least 80, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Step 5: Craft firearm magazines
    craft_item(Prototype.FirearmMagazine, 20)
    
    # Final check: Verify the count of firearm magazines in the inventory
    magazine_count = inspect_inventory()[Prototype.FirearmMagazine]
    assert magazine_count == 20, f"Failed to craft 20 firearm magazines. Current count: {magazine_count}"
    print(f"Successfully crafted {magazine_count} firearm magazines!")
    print(f"Final inventory: {inspect_inventory()}")