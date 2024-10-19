def smelt_iron_with_a_furnace(input_coal: int, input_iron_ore: int, furnace: Entity, output_iron_plate: int):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    :param input_coal: The number of coal to insert into the furnace
    :param input_iron_ore: The number of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :param output_iron_plate: The number of iron plates to extract from the furnace
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Insert coal and iron ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the iron plates from the furnace
    # 5. Verify that we have the required number of iron plates in the inventory
    # [END OF PLANNING]

    # Log initial inventory state
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Check if we have enough iron ore and coal in the inventory
    iron_ore_in_inventory = initial_inventory.get(Prototype.IronOre, 0)
    coal_in_inventory = initial_inventory.get(Prototype.Coal, 0)
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"
    assert coal_in_inventory >= input_coal, f"Not enough coal in inventory. Required: {input_coal}, Available: {coal_in_inventory}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Log inventory after inserting items
    after_insert_inventory = inspect_inventory()
    print(f"Inventory after inserting items: {after_insert_inventory}")

    # Wait for the smelting process to complete
    print("Waiting for smelting process to complete...")
    sleep(20)  # Adjust this value based on the smelting time of your furnace

    # Extract iron plates from the furnace
    max_attempts = 5
    iron_plates_extracted = 0
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, output_iron_plate - iron_plates_extracted)
        current_inventory = inspect_inventory()
        iron_plates_extracted = current_inventory.get(Prototype.IronPlate, 0) - initial_inventory.get(Prototype.IronPlate, 0)
        print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates")
        
        if iron_plates_extracted >= output_iron_plate:
            break
        
        if attempt < max_attempts - 1:
            print("Not all plates ready. Waiting a bit longer...")
            sleep(10)

    # Log final inventory state
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")

    # Verify that we have the required number of iron plates
    total_iron_plates = final_inventory.get(Prototype.IronPlate, 0)
    assert total_iron_plates >= output_iron_plate, f"Failed to smelt enough iron plates. Required: {output_iron_plate}, Produced: {total_iron_plates}"

    print(f"Successfully smelted {iron_plates_extracted} iron plates")