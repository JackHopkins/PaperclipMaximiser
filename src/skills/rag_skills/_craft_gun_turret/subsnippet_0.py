def smelt_plates(ore_type: Resource, amount: int) -> None:
    """
    Smelt the specified amount of plates using a stone furnace.
    
    :param ore_type: The type of ore to smelt (e.g., Resource.IronOre)
    :param amount: The amount of plates to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Determine the corresponding plate type based on the ore type
    # 2. Check if we have enough ore in the inventory
    # 3. Place the stone furnace if not already placed
    # 4. Insert coal into the furnace for fuel
    # 5. Insert ore into the furnace
    # 6. Wait for smelting to complete
    # 7. Extract the plates from the furnace
    # 8. Verify that we have the correct amount of plates in the inventory
    # [END OF PLANNING]

    # Determine the corresponding plate type
    if ore_type == Resource.IronOre:
        plate_type = Prototype.IronPlate
    elif ore_type == Resource.CopperOre:
        plate_type = Prototype.CopperPlate
    else:
        raise ValueError(f"Unsupported ore type: {ore_type}")

    print(f"Starting to smelt {amount} {plate_type} from {ore_type}")
    
    # Check if we have enough ore in the inventory
    initial_ore_count = inspect_inventory()[ore_type]
    assert initial_ore_count >= amount, f"Not enough {ore_type} in inventory. Need {amount}, have {initial_ore_count}"
    
    # Place the stone furnace if not already placed
    furnace = get_entity(Prototype.StoneFurnace, nearest(Prototype.StoneFurnace))
    if not furnace:
        furnace_position = Position(x=0, y=0)  # Assuming we're at the origin
        furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
        assert furnace, "Failed to place stone furnace"
    print(f"Stone furnace placed/found at {furnace.position}")

    # Insert coal into the furnace for fuel
    insert_item(Prototype.Coal, furnace, 5)
    print("Inserted 5 coal into the furnace")

    # Insert ore into the furnace
    insert_item(ore_type, furnace, amount)
    print(f"Inserted {amount} {ore_type} into the furnace")

    # Wait for smelting to complete (1 second per ore)
    sleep(amount)
    print(f"Waiting {amount} seconds for smelting to complete")

    # Extract the plates from the furnace
    initial_plate_count = inspect_inventory()[plate_type]
    extract_item(plate_type, furnace.position, amount)
    
    # Verify that we have the correct amount of plates in the inventory
    final_plate_count = inspect_inventory()[plate_type]
    plates_smelted = final_plate_count - initial_plate_count
    assert plates_smelted >= amount, f"Failed to smelt enough plates. Expected {amount}, but got {plates_smelted}"
    
    print(f"Successfully smelted {plates_smelted} {plate_type}")
    print(f"Current inventory: {inspect_inventory()}")