def smelt_20_iron_plates():
    """
    Objective: Smelt 20 iron plates. The final success should be checked by looking if the iron plates are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Mine iron ore (we'll mine 30 to account for inefficiencies)
    # 2. Mine coal for fuel (we'll mine 15 to ensure we have enough)
    # 3. Craft a stone furnace
    # 4. Place the stone furnace
    # 5. Fuel the furnace with coal
    # 6. Smelt the iron ore into iron plates
    # 7. Check if we have 20 iron plates in our inventory
    # [END OF PLANNING]

    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 30)
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 30, f"Failed to mine enough iron ore. Expected 30, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 15)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 15, f"Failed to mine enough coal. Expected 15, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 3: Mine stone and craft a stone furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 5)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 4: Place the stone furnace
    furnace_position = Position(x=iron_position.x, y=iron_position.y + 2)
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 5: Fuel the furnace with coal
    insert_item(Prototype.Coal, furnace, 15)
    print("Inserted 15 coal into the furnace")

    # Step 6: Smelt the iron ore into iron plates
    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=30, furnace=furnace)

    # Step 7: Check if we have 20 iron plates in our inventory
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 20, f"Failed to smelt 20 iron plates. Current count: {iron_plates}"
    
    print(f"Successfully smelted {iron_plates} iron plates!")
    print(f"Final inventory: {inspect_inventory()}")