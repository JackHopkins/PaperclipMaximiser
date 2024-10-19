def smelt_iron_with_furnace(input_coal: int, input_iron_ore: int, furnace: Entity, output_iron_plate: int) -> None:
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron ore and coal in the inventory to smelt the iron plates
    :param input_coal: The number of coal to insert into the furnace
    :param input_iron_ore: The number of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :param output_iron_plate: The number of iron plates to extract from the furnace
    :return: None as the iron plates will be in inventory
    """
    
    # [PLANNING]
    # 1. Check inventory for required resources
    # 2. Move to the furnace
    # 3. Insert coal and iron ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract iron plates from the furnace
    # 6. Verify the result
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check inventory for required resources
    inventory = inspect_inventory()
    assert inventory[Prototype.Coal] >= input_coal, f"Not enough coal. Required: {input_coal}, Available: {inventory[Prototype.Coal]}"
    assert inventory[Prototype.IronOre] >= input_iron_ore, f"Not enough iron ore. Required: {input_iron_ore}, Available: {inventory[Prototype.IronOre]}"

    # Move to the furnace
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (assuming 3.5 seconds per iron plate)
    smelting_time = output_iron_plate * 3.5
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, output_iron_plate)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        
        if iron_plates_extracted >= output_iron_plate:
            print(f"Successfully extracted {iron_plates_extracted} iron plates")
            break
        elif attempt < max_attempts - 1:
            print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates. Waiting for more...")
            sleep(5)
    else:
        print(f"Warning: Could only extract {iron_plates_extracted} iron plates after {max_attempts} attempts")

    # Verify the result
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.IronPlate] >= initial_iron_plates + output_iron_plate, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + output_iron_plate}, but got {final_inventory[Prototype.IronPlate]}"

    print(f"Final inventory: {final_inventory}")
    print("Successfully completed iron smelting")