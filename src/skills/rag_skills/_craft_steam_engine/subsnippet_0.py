def smelt_iron_with_furnace(input_coal: int, input_iron_ore: int, furnace: Entity) -> None:
    """
    Smelt iron ore into iron plates using a furnace
    :param input_coal: Amount of coal to insert into the furnace
    :param input_iron_ore: Amount of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Insert coal and iron ore into the furnace
    # 3. Wait for smelting to complete
    # 4. Extract iron plates from the furnace
    # 5. Verify that we have the expected amount of iron plates
    # [END OF PLANNING]

    print(f"Starting iron smelting process. Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore and coal in the inventory
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= input_iron_ore, f"Not enough iron ore. Required: {input_iron_ore}, Available: {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.Coal] >= input_coal, f"Not enough coal. Required: {input_coal}, Available: {inventory[Prototype.Coal]}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (iron ore smelts at a rate of 1 ore per 3.2 seconds)
    smelting_time = input_iron_ore * 3.2
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        
        if iron_plates_extracted >= input_iron_ore:
            break
        
        if attempt < max_attempts - 1:
            print(f"Extracted {iron_plates_extracted} iron plates. Waiting for more...")
            sleep(5)
    
    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")

    # Verify that we have the expected amount of iron plates
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.IronPlate] >= initial_iron_plates + input_iron_ore, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + input_iron_ore}, but got {final_inventory[Prototype.IronPlate]}"

    print(f"Successfully smelted {input_iron_ore} iron ore into iron plates")
    print(f"Final inventory: {final_inventory}")
    print("Iron smelting process completed successfully")