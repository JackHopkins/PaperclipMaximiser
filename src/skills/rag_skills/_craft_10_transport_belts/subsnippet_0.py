def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    :param input_iron_ore: The number of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Calculate the amount of coal needed (1 coal per 4 iron ore)
    # 3. Insert coal and iron ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract iron plates from the furnace
    # 6. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting to smelt {input_iron_ore} iron ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Need {input_iron_ore}, have {iron_ore_in_inventory}"

    # Calculate and check if we have enough coal
    coal_needed = (input_iron_ore + 3) // 4  # Round up division
    coal_in_inventory = inspect_inventory()[Prototype.Coal]
    assert coal_in_inventory >= coal_needed, f"Not enough coal in inventory. Need {coal_needed}, have {coal_in_inventory}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, coal_needed)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {coal_needed} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (smelting takes 3.2 seconds per iron plate)
    smelting_time = input_iron_ore * 3.2
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Get the initial number of iron plates in the inventory
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]

    # Extract iron plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        if iron_plates_extracted >= input_iron_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")

    # Verify that we have the correct number of iron plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert final_iron_plates >= initial_iron_plates + input_iron_ore, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + input_iron_ore}, but got {final_iron_plates}"

    print(f"Successfully smelted {input_iron_ore} iron ore into iron plates")
    print(f"Final inventory: {inspect_inventory()}")