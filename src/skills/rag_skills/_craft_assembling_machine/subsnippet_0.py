def smelt_ore(furnace: Entity, ore_type: str, amount: int) -> None:
    """
    Objective: Smelt ore into plates using a furnace
    Mining setup: A furnace is placed on the map
    Inventory: We have ore and coal in the inventory
    :param furnace: The furnace entity to use for smelting
    :param ore_type: The type of ore to smelt (iron or copper)
    :param amount: The amount of ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Validate input parameters
    # 2. Check inventory for required resources
    # 3. Insert coal into the furnace
    # 4. Insert ore into the furnace
    # 5. Wait for smelting to complete
    # 6. Extract plates from the furnace
    # 7. Verify the smelting process was successful
    # [END OF PLANNING]

    # Step 1: Validate input parameters
    assert ore_type in ['iron', 'copper'], f"Invalid ore type: {ore_type}. Must be 'iron' or 'copper'."
    assert amount > 0, f"Invalid amount: {amount}. Must be greater than 0."

    # Step 2: Check inventory for required resources
    inventory = inspect_inventory()
    ore_prototype = Prototype.IronOre if ore_type == 'iron' else Prototype.CopperOre
    plate_prototype = Prototype.IronPlate if ore_type == 'iron' else Prototype.CopperPlate
    
    print(f"Current inventory: {inventory}")
    assert inventory[ore_prototype] >= amount, f"Not enough {ore_type} ore in inventory. Required: {amount}, Available: {inventory[ore_prototype]}"
    assert inventory[Prototype.Coal] >= amount, f"Not enough coal in inventory. Required: {amount}, Available: {inventory[Prototype.Coal]}"

    # Step 3: Insert coal into the furnace
    insert_item(Prototype.Coal, furnace, amount)
    print(f"Inserted {amount} coal into the furnace")

    # Step 4: Insert ore into the furnace
    insert_item(ore_prototype, furnace, amount)
    print(f"Inserted {amount} {ore_type} ore into the furnace")

    # Step 5: Wait for smelting to complete
    # Smelting takes 3.2 seconds per item
    smelting_time = amount * 3.2
    print(f"Waiting for {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Step 6: Extract plates from the furnace
    initial_plates = inventory[plate_prototype]
    extract_item(plate_prototype, furnace.position, amount)
    print(f"Attempted to extract {amount} {ore_type} plates from the furnace")

    # Step 7: Verify the smelting process was successful
    final_inventory = inspect_inventory()
    plates_produced = final_inventory[plate_prototype] - initial_plates
    print(f"Plates produced: {plates_produced}")
    assert plates_produced == amount, f"Failed to produce the expected number of plates. Expected: {amount}, Produced: {plates_produced}"

    print(f"Successfully smelted {amount} {ore_type} ore into {plates_produced} {ore_type} plates")
    print(f"Final inventory: {final_inventory}")