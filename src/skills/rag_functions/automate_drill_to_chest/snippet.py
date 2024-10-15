def connect_a_drills_output_to_a_existing_chest(chest, drill, direction):
    """
    Objective: We need to connect a drill to a chest with an burner inserter at the given direction
    Mining setup: We have a drill and a chest entity on the map
    Inventory: We have the burner inserter and transport belts in our inventory
    :param chest: The chest entity where the output of the drill needs to go
    :param drill: The drill entity that produces output for the chest
    :param direction: The direction where the burner inserter should be placed
    :return burner_inserter: The burner inserter entity that inserts items into the chest
    """

    # [PLANNING] 
    # To solve this objective, we first need to place down the burner inserter that puts items to the chest
    # We need to fuel and rotate the burner inserter to put items into the chest as by default it takes from the chest
    # finally we need to connect the burner inserter and the drill with transport belts
    # We already have an burner inserter and transport belts in our inventory so we don't need to craft them 
    # [END OF PLANNING]

    # First print our inventory for logging
    print(f"Inventory before placing burner inserter: {inspect_inventory()}")

    # We need to place an burner inserter on top of the chest
    burner_inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction = direction)
    assert burner_inserter, "Failed to place inserter"
    print(f"Placed burner inserter at {burner_inserter.position}")
    print(f"Inventory after placing burner inserter: {inspect_inventory()}")
    # We need to rotate the burner inserter as it currently is taking from the chest not putting into it
    # The direction is down as the burner inserter is above the chest
    burner_inserter = rotate_entity(burner_inserter, Direction.DOWN)
    print(f"Rotated burner inserter at {burner_inserter.position}")
    # We also need to fuel the burner inserter
    # first check if inventory has coal
    assert inventory.get(Prototype.Coal, 0) > 0, "No coal in inventory"
    inserter_with_coal = insert_item(Prototype.Coal, burner_inserter, quantity=min(5, inventory.get(Prototype.Coal)))
    print(inserter_with_coal.fuel_inventory)
    assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"
    print(f"Fuelled burner inserter with coal: {inserter_with_coal}")
    print(f"Inventory after fuelling: {inspect_inventory()}")


    # We then need to connect the mining drill to the chest inserter with a transport belt
    # We use the drop position of the drill as the start and the pickup position of the inserter as the end
    belts = connect_entities(drill.drop_position, burner_inserter.pickup_position, Prototype.TransportBelt)
    assert belts, "Failed to place transport belts"
    print(f"Connected the drill to the chest with transport belts")
    print(f"Inventory after connecting: {inspect_inventory()}")
    return burner_inserter