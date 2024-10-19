def connect_miner_to_chest(miner: Entity, chest: Entity) -> None:
    """
    Connect a mining drill to a chest using transport belts and inserters.

    :param miner: The mining drill entity
    :param chest: The chest entity
    :return: None
    """
    # [PLANNING]
    # 1. Place an inserter next to the miner's output
    # 2. Rotate the inserter to take items from the miner
    # 3. Place transport belts from the inserter's output to near the chest
    # 4. Place another inserter next to the chest
    # 5. Rotate the chest inserter to put items into the chest
    # 6. Connect the transport belts to both inserters
    # [END OF PLANNING]

    print(f"Starting to connect miner at {miner.position} to chest at {chest.position}")

    # Place an inserter next to the miner's output
    miner_inserter = place_entity_next_to(Prototype.Inserter, miner.position, direction=Direction.DOWN, spacing=1)
    assert miner_inserter, "Failed to place inserter next to miner"
    print(f"Placed miner inserter at {miner_inserter.position}")

    # Rotate the miner inserter to take items from the miner
    miner_inserter = rotate_entity(miner_inserter, Direction.UP)
    print(f"Rotated miner inserter to face the miner")

    # Place an inserter next to the chest
    chest_inserter = place_entity_next_to(Prototype.Inserter, chest.position, direction=Direction.UP, spacing=1)
    assert chest_inserter, "Failed to place inserter next to chest"
    print(f"Placed chest inserter at {chest_inserter.position}")

    # Rotate the chest inserter to put items into the chest
    chest_inserter = rotate_entity(chest_inserter, Direction.DOWN)
    print(f"Rotated chest inserter to face the chest")

    # Connect the miner inserter to the chest inserter with transport belts
    belts = connect_entities(miner_inserter.drop_position, chest_inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts between inserters"
    print(f"Placed {len(belts)} transport belts to connect inserters")

    # Final checks
    inspection = inspect_entities(miner.position, radius=20)
    assert any(e.name == "inserter" for e in inspection.entities), "Miner inserter not found in inspection"
    assert any(e.name == "inserter" for e in inspection.entities), "Chest inserter not found in inspection"
    assert any(e.name == "transport-belt" for e in inspection.entities), "Transport belts not found in inspection"

    print("Successfully connected miner to chest using transport belts and inserters")