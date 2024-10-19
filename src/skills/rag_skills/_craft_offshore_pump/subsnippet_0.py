def smelt_ore_into_plates(ore_type: str, quantity: int) -> None:
    """
    Objective: Smelt iron ore into iron plates
    Mining setup: No existing setup
    Inventory: We have iron ore in our inventory
    :param ore_type: The type of ore to smelt (Iron or Copper)
    :param quantity: The number of plates to produce
    :return: None
    """
    # [PLANNING]
    # 1. Validate the ore type
    # 2. Check if we have enough ore in the inventory
    # 3. Place a stone furnace
    # 4. Fuel the furnace with coal
    # 5. Insert the ore into the furnace
    # 6. Wait for smelting to complete
    # 7. Extract the plates from the furnace
    # 8. Verify that we have the correct number of plates in our inventory
    # [END OF PLANNING]

    # Validate ore type and set up corresponding prototypes
    if ore_type.lower() == "iron":
        ore_prototype = Prototype.IronOre
        plate_prototype = Prototype.IronPlate
    elif ore_type.lower() == "copper":
        ore_prototype = Prototype.CopperOre
        plate_prototype = Prototype.CopperPlate
    else:
        raise ValueError(f"Invalid ore type: {ore_type}. Must be 'Iron' or 'Copper'.")

    # Check if we have enough ore in the inventory
    inventory = inspect_inventory()
    ore_count = inventory[ore_prototype]
    assert ore_count >= quantity, f"Not enough {ore_type} ore in inventory. Need {quantity}, but have {ore_count}."

    print(f"Starting inventory: {inventory}")

    # Place a stone furnace
    furnace_position = Position(x=0, y=0)  # Assuming we're at the origin
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Fuel the furnace with coal
    coal_needed = min(quantity, 5)  # Use up to 5 coal, or less if smelting fewer items
    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Fueled furnace with {coal_needed} coal")

    # Insert the ore into the furnace
    insert_item(ore_prototype, furnace, quantity)
    print(f"Inserted {quantity} {ore_type} ore into the furnace")

    # Wait for smelting to complete (1 second per ore)
    sleep(quantity)

    # Extract the plates from the furnace
    initial_plate_count = inventory[plate_prototype]
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(plate_prototype, furnace.position, quantity)
        current_plate_count = inspect_inventory()[plate_prototype]
        plates_produced = current_plate_count - initial_plate_count
        if plates_produced >= quantity:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    # Verify that we have the correct number of plates in our inventory
    final_inventory = inspect_inventory()
    final_plate_count = final_inventory[plate_prototype]
    plates_produced = final_plate_count - initial_plate_count
    assert plates_produced >= quantity, f"Failed to produce enough {ore_type} plates. Expected {quantity}, but produced {plates_produced}."

    print(f"Successfully produced {plates_produced} {ore_type} plates")
    print(f"Final inventory: {final_inventory}")

    # Clean up: remove the furnace (optional, depending on your needs)
    pickup_entity(Prototype.StoneFurnace, furnace.position)
    print("Removed the furnace")