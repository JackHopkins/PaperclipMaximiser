def smelt_copper_ore(input_copper_ore: int) -> None:
    """
    Objective: Smelt copper ore into copper plates
    Mining setup: No existing furnace on the map
    Inventory: We have copper ore and coal in the inventory
    :param input_copper_ore: The number of copper ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore and coal in the inventory
    # 2. Craft and place a stone furnace
    # 3. Insert coal and copper ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract copper plates from the furnace
    # 6. Verify that we have the correct number of copper plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Check if we have enough copper ore and coal
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= input_copper_ore, f"Not enough copper ore. Required: {input_copper_ore}, Available: {inventory[Prototype.CopperOre]}"
    assert inventory[Prototype.Coal] >= 5, f"Not enough coal. Required: 5, Available: {inventory[Prototype.Coal]}"

    # Step 2: Craft and place a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 3: Insert coal and copper ore into the furnace
    insert_item(Prototype.Coal, furnace, 5)
    insert_item(Prototype.CopperOre, furnace, input_copper_ore)
    print(f"Inserted 5 coal and {input_copper_ore} copper ore into the furnace")

    # Step 4: Wait for smelting to complete (1 second per ore)
    sleep(input_copper_ore)

    # Step 5: Extract copper plates from the furnace
    initial_copper_plates = inventory[Prototype.CopperPlate]
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, input_copper_ore)
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_extracted = current_copper_plates - initial_copper_plates
        if copper_plates_extracted >= input_copper_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_extracted} copper plates from the furnace")

    # Step 6: Verify that we have the correct number of copper plates
    final_inventory = inspect_inventory()
    final_copper_plates = final_inventory[Prototype.CopperPlate]
    assert final_copper_plates >= initial_copper_plates + input_copper_ore, f"Failed to smelt enough copper plates. Expected at least {initial_copper_plates + input_copper_ore}, but got {final_copper_plates}"

    print(f"Final inventory: {final_inventory}")
    print(f"Successfully smelted {input_copper_ore} copper ore into copper plates!")