def craft_burner_inserter():
    """
    Objective: Craft one BurnerInserter. The final success should be checked by looking if a BurnerInserter is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for BurnerInserter
    # 2. Mine necessary resources (iron ore)
    # 3. Craft a stone furnace to smelt iron ore
    # 4. Smelt iron plates
    # 5. Craft iron gear wheel
    # 6. Craft burner inserter
    # 7. Verify success
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    burner_inserter_recipe = get_prototype_recipe(Prototype.BurnerInserter)
    print(f"Burner Inserter recipe: {burner_inserter_recipe}")

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 10)  # Mine extra to be safe
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 6, f"Failed to mine enough iron ore. Expected at least 6, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Mine stone for furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # Mine extra to be safe
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Place furnace and smelt iron plates
    furnace = place_entity(Prototype.StoneFurnace, position=iron_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=6, furnace=furnace)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 3, f"Failed to smelt enough iron plates. Expected at least 3, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Craft iron gear wheel
    craft_item(Prototype.IronGearWheel, 1)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count == 1, f"Failed to craft iron gear wheel. Expected 1, but got {gear_count}"
    print("Crafted 1 iron gear wheel")

    # Craft burner inserter
    craft_item(Prototype.BurnerInserter, 1)
    inserter_count = inspect_inventory()[Prototype.BurnerInserter]
    assert inserter_count == 1, f"Failed to craft burner inserter. Expected 1, but got {inserter_count}"
    print("Successfully crafted 1 burner inserter!")

    # Final inventory check
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    assert final_inventory[Prototype.BurnerInserter] == 1, "Burner Inserter not found in final inventory"

    print("Objective completed: Crafted one BurnerInserter and verified it's in the inventory.")