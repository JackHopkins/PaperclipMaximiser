def mine_and_smelt_resource(resource: Resource, quantity: int) -> None:
    """
    Mine a specific resource and smelt it into plates
    :param resource: The resource to mine (Resource.CopperOre or Resource.IronOre)
    :param quantity: The number of plates to produce
    :return: None
    """
    # [PLANNING]
    # 1. Determine the corresponding plate type and furnace recipe
    # 2. Find and move to the nearest resource patch
    # 3. Mine the required amount of ore (plus extra for inefficiencies)
    # 4. Find and move to the nearest coal patch
    # 5. Mine the required amount of coal for smelting
    # 6. Craft a stone furnace
    # 7. Place the stone furnace
    # 8. Smelt the ore into plates
    # 9. Verify the correct number of plates have been produced
    # [END OF PLANNING]

    # Step 1: Determine the corresponding plate type and furnace recipe
    if resource == Resource.CopperOre:
        plate_type = Prototype.CopperPlate
        ore_type = Prototype.CopperOre
    elif resource == Resource.IronOre:
        plate_type = Prototype.IronPlate
        ore_type = Prototype.IronOre
    else:
        raise ValueError("Invalid resource type. Must be CopperOre or IronOre.")

    print(f"Starting to mine and smelt {quantity} {plate_type.value[0]}s")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 2: Find and move to the nearest resource patch
    resource_position = nearest(resource)
    move_to(resource_position)
    print(f"Moved to {resource} patch at {resource_position}")

    # Step 3: Mine the required amount of ore (plus extra for inefficiencies)
    ore_to_mine = quantity + 5  # Add extra to account for inefficiencies
    harvest_resource(resource_position, ore_to_mine)
    ore_count = inspect_inventory()[ore_type]
    assert ore_count >= quantity, f"Failed to mine enough {resource}. Expected at least {quantity}, but got {ore_count}"
    print(f"Mined {ore_count} {resource}")

    # Step 4: Find and move to the nearest coal patch
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    print(f"Moved to coal patch at {coal_position}")

    # Step 5: Mine the required amount of coal for smelting
    coal_needed = quantity + 5  # Add extra to account for inefficiencies
    harvest_resource(coal_position, coal_needed)
    coal_count = inspect_inventory()[Prototype.Coal]
    assert coal_count >= quantity, f"Failed to mine enough coal. Expected at least {quantity}, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 6: Craft a stone furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 5)
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 7: Place the stone furnace
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 8: Smelt the ore into plates
    insert_item(Prototype.Coal, furnace, coal_needed)
    insert_item(ore_type, furnace, ore_to_mine)
    print(f"Inserted {coal_needed} coal and {ore_to_mine} {ore_type.value[0]} into the furnace")

    # Wait for smelting to complete
    sleep(quantity * 0.7)  # Assuming it takes about 0.7 seconds to smelt each ore

    # Step 9: Verify the correct number of plates have been produced
    max_attempts = 5
    plates_extracted = 0
    for _ in range(max_attempts):
        extract_item(plate_type, furnace.position, quantity - plates_extracted)
        plates_in_inventory = inspect_inventory()[plate_type]
        if plates_in_inventory >= quantity:
            plates_extracted = plates_in_inventory
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    assert plates_extracted >= quantity, f"Failed to smelt enough {plate_type.value[0]}s. Expected {quantity}, but got {plates_extracted}"
    print(f"Successfully mined and smelted {plates_extracted} {plate_type.value[0]}s")
    print(f"Final inventory: {inspect_inventory()}")