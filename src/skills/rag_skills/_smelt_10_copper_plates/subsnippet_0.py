def smelt_copper_with_furnace(input_copper_ore: int, furnace: Entity):
    """
    Objective: Smelt copper ore into copper plates using a furnace
    Mining setup: We have a furnace on the map that we can use to smelt copper ore
    Inventory: We have enough copper ore in the inventory to smelt the copper plates
    :param input_copper_ore: The number of copper ore to insert into the furnace
    :param furnace: The furnace entity to use for smelting
    :return: None as the copper plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore in the inventory
    # 2. Insert the copper ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the copper plates from the furnace
    # 5. Verify that we have the expected number of copper plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough copper ore in the inventory
    copper_ore_in_inventory = inspect_inventory()[Prototype.CopperOre]
    assert copper_ore_in_inventory >= input_copper_ore, f"Not enough copper ore in inventory. Expected {input_copper_ore}, but got {copper_ore_in_inventory}"

    # Insert copper ore into the furnace
    insert_item(Prototype.CopperOre, furnace, input_copper_ore)
    print(f"Inserted {input_copper_ore} copper ore into the furnace")

    # Get the initial number of copper plates in the inventory
    initial_copper_plates = inspect_inventory()[Prototype.CopperPlate]

    # Wait for smelting to complete (1 second per ore)
    sleep(input_copper_ore)

    # Extract copper plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, input_copper_ore)
        copper_plates_in_inventory = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_smelted = copper_plates_in_inventory - initial_copper_plates
        if copper_plates_smelted >= input_copper_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_smelted} copper plates from the furnace")

    # Verify that we have the expected number of copper plates in our inventory
    final_copper_plates = inspect_inventory()[Prototype.CopperPlate]
    copper_plates_produced = final_copper_plates - initial_copper_plates
    assert copper_plates_produced >= input_copper_ore, f"Failed to smelt enough copper plates. Expected {input_copper_ore}, but got {copper_plates_produced}"

    print(f"Successfully smelted {copper_plates_produced} copper plates")
    print(f"Final inventory: {inspect_inventory()}")