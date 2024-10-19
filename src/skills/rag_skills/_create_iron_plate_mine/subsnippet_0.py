def connect_miner_to_chest(miner: BurnerMiningDrill, chest: Entity) -> None:
    """
    Connect the mining drill to the chest using transport belts and inserters
    :param miner: The burner mining drill entity
    :param chest: The iron chest entity
    :return: None
    """
    # [PLANNING]
    # 1. Place a burner inserter next to the miner
    # 2. Rotate the inserter to take from the miner
    # 3. Fuel the inserter
    # 4. Connect the inserter to the chest using transport belts
    # 5. Place another burner inserter next to the chest
    # 6. Rotate the chest inserter to put items into the chest
    # 7. Fuel the chest inserter
    # 8. Verify the connection
    # [END OF PLANNING]

    print(f"Starting to connect miner at {miner.position} to chest at {chest.position}")
    
    # Place burner inserter next to the miner
    miner_inserter = place_entity_next_to(Prototype.BurnerInserter, miner.position, direction=Direction.RIGHT)
    assert miner_inserter, "Failed to place inserter next to miner"
    print(f"Placed miner inserter at {miner_inserter.position}")

    # Rotate the miner inserter to take from the miner
    miner_inserter = rotate_entity(miner_inserter, Direction.LEFT)
    print(f"Rotated miner inserter to face the miner")

    # Fuel the miner inserter
    insert_item(Prototype.Coal, miner_inserter, quantity=5)
    print(f"Fueled miner inserter with coal")

    # Connect the miner inserter to the chest using transport belts
    belts = connect_entities(miner_inserter.drop_position, chest.position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts"
    print(f"Connected miner inserter to chest with transport belts")

    # Place burner inserter next to the chest
    chest_inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.LEFT)
    assert chest_inserter, "Failed to place inserter next to chest"
    print(f"Placed chest inserter at {chest_inserter.position}")

    # Rotate the chest inserter to put items into the chest
    chest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)
    print(f"Rotated chest inserter to face the chest")

    # Fuel the chest inserter
    insert_item(Prototype.Coal, chest_inserter, quantity=5)
    print(f"Fueled chest inserter with coal")

    # Verify the connection
    inspection = inspect_entities(miner.position, radius=20)
    assert any(entity.name == "transport-belt" for entity in inspection.entities), "Transport belts not found in the setup"
    assert any(entity.name == "burner-inserter" for entity in inspection.entities), "Burner inserters not found in the setup"
    
    print("Successfully connected miner to chest using transport belts and inserters")

    # Wait for a short time to allow items to move through the system
    sleep(10)

    # Check if items are in the chest
    chest_inventory = inspect_inventory(chest)
    assert chest_inventory.get(Prototype.IronOre, 0) > 0 or chest_inventory.get(Prototype.CopperOre, 0) > 0, "No ore found in the chest after waiting"
    
    print(f"Connection verified. Chest contains: {chest_inventory}")