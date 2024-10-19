def smelt_ore(ore_type: Prototype, ore_count: int, furnace: Entity) -> None:
    """
    Smelt a specific type of ore into plates
    :param ore_type: The type of ore to smelt (Prototype.IronOre or Prototype.CopperOre)
    :param ore_count: The number of ores to smelt
    :param furnace: The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Verify we have enough ore in the inventory
    # 2. Determine the corresponding plate type for the given ore
    # 3. Insert the ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract the plates from the furnace
    # 6. Verify we have the correct number of plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Verify we have enough ore in the inventory
    ore_in_inventory = inspect_inventory()[ore_type]
    assert ore_in_inventory >= ore_count, f"Not enough {ore_type} in inventory. Required: {ore_count}, Available: {ore_in_inventory}"

    # Determine the corresponding plate type
    if ore_type == Prototype.IronOre:
        plate_type = Prototype.IronPlate
    elif ore_type == Prototype.CopperOre:
        plate_type = Prototype.CopperPlate
    else:
        raise ValueError(f"Unsupported ore type: {ore_type}")

    # Insert the ore into the furnace
    insert_item(ore_type, furnace, ore_count)
    print(f"Inserted {ore_count} {ore_type} into the furnace")

    # Get the initial number of plates in the inventory
    initial_plates = inspect_inventory()[plate_type]

    # Wait for smelting to complete (1 second per ore)
    sleep(ore_count)

    # Extract the plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(plate_type, furnace.position, ore_count)
        current_plates = inspect_inventory()[plate_type]
        plates_produced = current_plates - initial_plates
        if plates_produced >= ore_count:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    print(f"Extracted {plates_produced} {plate_type} from the furnace")

    # Verify we have the correct number of plates in our inventory
    final_plates = inspect_inventory()[plate_type]
    plates_produced = final_plates - initial_plates
    assert plates_produced >= ore_count, f"Failed to smelt enough {plate_type}. Expected: {ore_count}, Produced: {plates_produced}"

    print(f"Successfully smelted {plates_produced} {plate_type}")
    print(f"Final inventory: {inspect_inventory()}")