def craft_5_iron_gear_wheels():
    """
    Objective: Craft 5 iron gear wheels. The final success should be checked by looking if 5 gear wheels are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Mine iron ore (we need at least 10 iron ore to craft 5 iron gear wheels)
    # 2. Craft a stone furnace to smelt the iron ore
    # 3. Mine coal for the furnace
    # 4. Smelt the iron ore into iron plates
    # 5. Craft the iron gear wheels
    # 6. Verify that we have 5 iron gear wheels in the inventory
    # [END OF PLANNING]

    print("Starting to craft 5 iron gear wheels")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 15)  # Mine extra to account for any inefficiencies
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 10, f"Failed to mine enough iron ore. Expected at least 10, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Craft a stone furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 7)  # Mine extra to account for any inefficiencies
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 3: Mine coal for the furnace
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 7)  # Mine extra to account for any inefficiencies
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected at least 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 4: Smelt iron ore into iron plates
    move_to(iron_position)  # Move back to iron position to place the furnace
    furnace = place_entity(entity=Prototype.StoneFurnace, position=iron_position, direction=Direction.UP)
    
    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: Smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron ore and coal in the inventory to smelt the iron plates
    # :param input_coal: The number of coal to insert into the furnace
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_coal=5, input_iron_ore=10, furnace=furnace)

    iron_plate_count = inspect_inventory()[Prototype.IronPlate]
    assert iron_plate_count >= 10, f"Failed to smelt enough iron plates. Expected at least 10, but got {iron_plate_count}"
    print(f"Smelted {iron_plate_count} iron plates")

    # Step 5: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 5)

    # Step 6: Verify that we have 5 iron gear wheels in the inventory
    gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheel_count == 5, f"Failed to craft 5 iron gear wheels. Expected 5, but got {gear_wheel_count}"
    print(f"Successfully crafted {gear_wheel_count} iron gear wheels!")
    print(f"Final inventory: {inspect_inventory()}")