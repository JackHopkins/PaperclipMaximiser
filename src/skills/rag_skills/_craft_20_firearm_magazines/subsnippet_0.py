def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace. We need to use an input furnace variable
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron ore in the inventory to smelt the iron plates
    :param input_iron_ore: The number of iron ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore in the inventory
    # 2. Move to the furnace
    # 3. Insert coal into the furnace for fuel (if needed)
    # 4. Insert iron ore into the furnace
    # 5. Wait for smelting to complete
    # 6. Extract iron plates from the furnace
    # 7. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting iron smelting process. Input iron ore: {input_iron_ore}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"

    # Move to the furnace
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Insert coal into the furnace for fuel (if needed)
    furnace_contents = inspect_inventory(furnace)
    coal_in_furnace = furnace_contents.get(Prototype.Coal, 0)
    if coal_in_furnace < 1:
        coal_to_insert = min(5, inspect_inventory()[Prototype.Coal])  # Insert up to 5 coal, or all we have if less
        insert_item(Prototype.Coal, furnace, coal_to_insert)
        print(f"Inserted {coal_to_insert} coal into the furnace")

    # Insert iron ore into the furnace
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (assuming 3.2 seconds per iron plate)
    smelting_time = input_iron_ore * 3.2
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
    
    # Verify that we have the correct number of iron plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    iron_plates_produced = final_iron_plates - initial_iron_plates
    assert iron_plates_produced == input_iron_ore, f"Expected to produce {input_iron_ore} iron plates, but produced {iron_plates_produced}"

    print(f"Successfully smelted {iron_plates_produced} iron plates")
    print(f"Final inventory: {inspect_inventory()}")