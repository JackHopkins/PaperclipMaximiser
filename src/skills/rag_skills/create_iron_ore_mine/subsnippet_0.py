def connect_drill_to_chest_with_inserter(chest: Entity, drill: Entity) -> Entity:
    """
    Connect a drill to a chest using a burner inserter and transport belt
    :param chest: The chest entity where the output of the drill needs to go
    :param drill: The drill entity that produces output for the chest
    :return inserter: The inserter entity that inserts items into the chest
    """
    # [PLANNING]
    # 1. Place a burner inserter next to the chest
    # 2. Rotate the inserter to face the chest
    # 3. Fuel the inserter with coal
    # 4. Connect the drill to the inserter using transport belts
    # 5. Verify the connection
    # [END OF PLANNING]

    print(f"Starting to connect drill at {drill.position} to chest at {chest.position}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Place burner inserter next to the chest
    inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.UP, spacing=0)
    assert inserter, "Failed to place burner inserter"
    print(f"Placed burner inserter at {inserter.position}")

    # Rotate the inserter to face the chest (insert items into the chest)
    inserter = rotate_entity(inserter, Direction.DOWN)
    print(f"Rotated burner inserter to face the chest")

    # Fuel the inserter with coal
    coal_in_inventory = inspect_inventory().get(Prototype.Coal, 0)
    assert coal_in_inventory > 0, "No coal in inventory to fuel the inserter"
    coal_to_insert = min(5, coal_in_inventory)
    inserter_with_coal = insert_item(Prototype.Coal, inserter, quantity=coal_to_insert)
    assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"
    print(f"Fueled burner inserter with {coal_to_insert} coal")

    # Connect the drill to the inserter using transport belts
    belts = connect_entities(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts between drill and inserter"
    print(f"Connected drill to inserter with transport belts")

    # Verify the connection
    inspection = inspect_entities(drill.position, radius=20)
    assert any(e.name == "burner-inserter" for e in inspection.entities), "Burner inserter not found in the setup"
    assert any(e.name == "transport-belt" for e in inspection.entities), "Transport belt not found in the setup"
    
    print("Successfully connected drill to chest with inserter and transport belt")
    print(f"Final inventory: {inspect_inventory()}")

    return inserter