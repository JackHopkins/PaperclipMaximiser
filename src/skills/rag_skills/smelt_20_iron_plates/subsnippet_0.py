def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron ore in the inventory to smelt the iron plates
    :param input_iron_ore: The number of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore in the inventory
    # 2. Insert the iron ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the iron plates from the furnace
    # 5. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting to smelt {input_iron_ore} iron ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"

    # Insert the iron ore into the furnace
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_iron_ore} iron ore into the furnace")
    print(f"Inventory after insertion: {inspect_inventory()}")

    # Wait for the smelting process to complete
    # Smelting time is 3.5 seconds per iron plate
    smelting_time = input_iron_ore * 3.5
    print(f"Waiting for {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract the iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        if iron_plates_extracted >= input_iron_ore:
            break
        print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates. Waiting for more...")
        sleep(5)

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")
    print(f"Final inventory: {inspect_inventory()}")

    # Verify that we have the correct number of iron plates in our inventory
    assert iron_plates_extracted >= input_iron_ore, f"Failed to extract enough iron plates. Expected: {input_iron_ore}, Extracted: {iron_plates_extracted}"

    print(f"Successfully smelted {input_iron_ore} iron ore into {iron_plates_extracted} iron plates")