def smelt_plates(iron_ore_count: int, copper_ore_count: int):
    """
    Objective: Smelt the required number of iron and copper plates using two furnaces
    Mining setup: We have two stone furnaces placed on the map
    Inventory: We have iron ore, copper ore, and coal in the inventory
    :param iron_ore_count: The number of iron ore to smelt
    :param copper_ore_count: The number of copper ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Find and move to the two stone furnaces
    # 2. Insert coal into both furnaces
    # 3. Insert iron ore into one furnace and copper ore into the other
    # 4. Wait for smelting to complete
    # 5. Extract the iron and copper plates from the furnaces
    # 6. Verify that we have the correct number of plates in our inventory
    # [END OF PLANNING]

    print(f"Starting inventory: {inspect_inventory()}")

    # Find the two stone furnaces
    furnaces = inspect_entities(radius=100).get_entities(Prototype.StoneFurnace)
    assert len(furnaces) == 2, f"Expected 2 stone furnaces, but found {len(furnaces)}"
    iron_furnace, copper_furnace = furnaces[0], furnaces[1]

    # Move to the first furnace
    move_to(iron_furnace.position)

    # Insert coal into both furnaces
    coal_per_furnace = max(iron_ore_count, copper_ore_count) // 2 + 5  # Add extra coal to ensure we don't run out
    insert_item(Prototype.Coal, iron_furnace, coal_per_furnace)
    insert_item(Prototype.Coal, copper_furnace, coal_per_furnace)
    print(f"Inserted {coal_per_furnace} coal into each furnace")

    # Insert iron ore and copper ore into respective furnaces
    insert_item(Prototype.IronOre, iron_furnace, iron_ore_count)
    insert_item(Prototype.CopperOre, copper_furnace, copper_ore_count)
    print(f"Inserted {iron_ore_count} iron ore and {copper_ore_count} copper ore into furnaces")

    # Wait for smelting to complete (1 second per ore)
    smelting_time = max(iron_ore_count, copper_ore_count)
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract the iron and copper plates from the furnaces
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    initial_copper_plates = inspect_inventory()[Prototype.CopperPlate]

    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, iron_furnace.position, iron_ore_count)
        extract_item(Prototype.CopperPlate, copper_furnace.position, copper_ore_count)
        
        current_iron_plates = inspect_inventory()[Prototype.IronPlate] - initial_iron_plates
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate] - initial_copper_plates
        
        if current_iron_plates >= iron_ore_count and current_copper_plates >= copper_ore_count:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {current_iron_plates} iron plates and {current_copper_plates} copper plates")

    # Verify that we have the correct number of plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    final_copper_plates = inspect_inventory()[Prototype.CopperPlate]
    
    assert final_iron_plates >= initial_iron_plates + iron_ore_count, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + iron_ore_count}, but got {final_iron_plates}"
    assert final_copper_plates >= initial_copper_plates + copper_ore_count, f"Failed to smelt enough copper plates. Expected at least {initial_copper_plates + copper_ore_count}, but got {final_copper_plates}"

    print(f"Successfully smelted {iron_ore_count} iron plates and {copper_ore_count} copper plates")
    print(f"Final inventory: {inspect_inventory()}")