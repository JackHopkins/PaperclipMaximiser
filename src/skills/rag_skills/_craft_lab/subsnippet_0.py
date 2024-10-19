def smelt_plates(copper_plates_needed: int, iron_plates_needed: int):
    """
    Objective: Smelt copper and iron plates using the stone furnace
    Mining setup: One stone furnace available
    Inventory: Raw ores and coal available
    :param copper_plates_needed: Number of copper plates to smelt
    :param iron_plates_needed: Number of iron plates to smelt
    :return: None (plates will be added to inventory)
    """
    # [PLANNING]
    # 1. Find the stone furnace
    # 2. Calculate the amount of ore and coal needed
    # 3. Smelt copper plates
    # 4. Smelt iron plates
    # 5. Verify the smelted plates are in the inventory
    # [END OF PLANNING]

    # Find the stone furnace
    furnace_position = nearest(Prototype.StoneFurnace)
    assert furnace_position, "No stone furnace found nearby"
    furnace = get_entity(Prototype.StoneFurnace, furnace_position)
    print(f"Found stone furnace at {furnace_position}")

    # Calculate the amount of ore and coal needed (1 ore = 1 plate, add 20% extra for inefficiencies)
    copper_ore_needed = int(copper_plates_needed * 1.2)
    iron_ore_needed = int(iron_plates_needed * 1.2)
    total_ore = copper_ore_needed + iron_ore_needed
    coal_needed = int(total_ore * 0.5)  # Assuming 1 coal per 2 plates

    print(f"Resources needed: {copper_ore_needed} copper ore, {iron_ore_needed} iron ore, {coal_needed} coal")

    # Check if we have enough resources
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= copper_ore_needed, f"Not enough copper ore. Need {copper_ore_needed}, have {inventory[Prototype.CopperOre]}"
    assert inventory[Prototype.IronOre] >= iron_ore_needed, f"Not enough iron ore. Need {iron_ore_needed}, have {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.Coal] >= coal_needed, f"Not enough coal. Need {coal_needed}, have {inventory[Prototype.Coal]}"

    # Smelt copper plates
    if copper_plates_needed > 0:
        print(f"Smelting {copper_plates_needed} copper plates")
        insert_item(Prototype.Coal, furnace, coal_needed // 2)
        insert_item(Prototype.CopperOre, furnace, copper_ore_needed)
        sleep(copper_ore_needed)  # Wait for smelting (1 second per ore)
        extract_item(Prototype.CopperPlate, furnace.position, copper_plates_needed)

    # Smelt iron plates
    if iron_plates_needed > 0:
        print(f"Smelting {iron_plates_needed} iron plates")
        insert_item(Prototype.Coal, furnace, coal_needed - (coal_needed // 2))
        insert_item(Prototype.IronOre, furnace, iron_ore_needed)
        sleep(iron_ore_needed)  # Wait for smelting (1 second per ore)
        extract_item(Prototype.IronPlate, furnace.position, iron_plates_needed)

    # Verify the smelted plates are in the inventory
    final_inventory = inspect_inventory()
    copper_plates_smelted = final_inventory[Prototype.CopperPlate] - inventory[Prototype.CopperPlate]
    iron_plates_smelted = final_inventory[Prototype.IronPlate] - inventory[Prototype.IronPlate]

    print(f"Smelted {copper_plates_smelted} copper plates and {iron_plates_smelted} iron plates")
    assert copper_plates_smelted >= copper_plates_needed, f"Failed to smelt enough copper plates. Needed {copper_plates_needed}, smelted {copper_plates_smelted}"
    assert iron_plates_smelted >= iron_plates_needed, f"Failed to smelt enough iron plates. Needed {iron_plates_needed}, smelted {iron_plates_smelted}"

    print("Successfully smelted all required plates!")
    print(f"Final inventory: {final_inventory}")