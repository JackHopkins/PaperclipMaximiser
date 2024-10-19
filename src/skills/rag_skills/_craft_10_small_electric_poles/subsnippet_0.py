def smelt_copper_plates(copper_ore_amount: int) -> None:
    """
    Objective: Smelt copper ore into copper plates using a stone furnace
    Mining setup: No existing furnaces
    Inventory: Copper ore and some stone available
    :param copper_ore_amount: The amount of copper ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore and stone in the inventory
    # 2. Craft a stone furnace if we don't have one
    # 3. Place the stone furnace
    # 4. Insert coal into the furnace for fuel
    # 5. Insert copper ore into the furnace
    # 6. Wait for smelting to complete
    # 7. Extract copper plates from the furnace
    # 8. Verify that we have the correct amount of copper plates
    # [END OF PLANNING]

    print(f"Starting copper plate smelting process for {copper_ore_amount} copper ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough copper ore
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= copper_ore_amount, f"Not enough copper ore. Required: {copper_ore_amount}, Available: {inventory[Prototype.CopperOre]}"

    # Craft a stone furnace if we don't have one
    if inventory[Prototype.StoneFurnace] == 0:
        print("Crafting a stone furnace")
        assert inventory[Prototype.Stone] >= 5, f"Not enough stone to craft a furnace. Required: 5, Available: {inventory[Prototype.Stone]}"
        craft_item(Prototype.StoneFurnace, 1)
        print("Stone furnace crafted successfully")

    # Place the stone furnace
    furnace_position = Position(x=0, y=0)  # Assuming we're at the origin
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Stone furnace placed at {furnace.position}")

    # Insert coal into the furnace for fuel
    coal_needed = min(5, copper_ore_amount)  # Use 1 coal per 2 copper ore, minimum 5
    if inventory[Prototype.Coal] < coal_needed:
        coal_position = nearest(Resource.Coal)
        move_to(coal_position)
        harvest_resource(coal_position, coal_needed)
        print(f"Harvested {coal_needed} coal")

    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Inserted {coal_needed} coal into the furnace")

    # Insert copper ore into the furnace
    insert_item(Prototype.CopperOre, furnace, copper_ore_amount)
    print(f"Inserted {copper_ore_amount} copper ore into the furnace")

    # Wait for smelting to complete (1 second per ore)
    print(f"Waiting for smelting to complete...")
    sleep(copper_ore_amount)

    # Extract copper plates from the furnace
    initial_copper_plates = inventory[Prototype.CopperPlate]
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, copper_ore_amount)
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_produced = current_copper_plates - initial_copper_plates
        if copper_plates_produced >= copper_ore_amount:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_produced} copper plates from the furnace")

    # Verify that we have the correct amount of copper plates
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.CopperPlate] >= initial_copper_plates + copper_ore_amount, f"Failed to smelt enough copper plates. Expected at least {copper_ore_amount}, but got {copper_plates_produced}"

    print(f"Successfully smelted {copper_plates_produced} copper plates")
    print(f"Final inventory: {final_inventory}")