def create_iron_ore_mine():
    """
    Objective: Create an automated iron mine that mines iron ore to a chest further away and down from it.
    The final setup should be checked by looking if the chest has any iron ore in it.
    Mining setup: There are no entities on the map.
    Inventory: We have all the required items in our inventory.
    """
    # [PLANNING]
    # 1. Find the nearest iron ore patch
    # 2. Place a burner mining drill on the iron ore patch
    # 3. Fuel the mining drill with coal
    # 4. Place an iron chest further away and down from the drill
    # 5. Place a burner inserter between the drill and the chest
    # 6. Rotate the inserter to face the chest
    # 7. Fuel the inserter with coal
    # 8. Connect the drill to the inserter with a transport belt
    # 9. Wait for some time to allow the system to produce iron ore
    # 10. Check the chest for iron ore
    # [END OF PLANNING]

    print("Starting to create an automated iron ore mine")
    print(f"Initial inventory: {inspect_inventory()}")

    # Find the nearest iron ore patch
    iron_position = nearest(Resource.IronOre)
    assert iron_position, "No iron ore found nearby"
    move_to(iron_position)
    print(f"Moving to iron ore patch at {iron_position}")

    # Get the iron ore patch details
    iron_patch = get_resource_patch(Resource.IronOre, iron_position, radius=10)
    assert iron_patch, "No iron ore patch found within radius"
    print(f"Iron ore patch details: {iron_patch}")

    # Place the mining drill on the iron ore patch
    miner = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, iron_patch.bounding_box.center)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed mining drill at {miner.position}")

    # Fuel the mining drill with coal
    miner_with_coal = insert_item(Prototype.Coal, miner, quantity=5)
    print(f"Fuelled mining drill with coal: {miner_with_coal}")

    # Place an iron chest further away and down from the drill
    chest_pos = Position(x=miner.position.x, y=miner.position.y + 7)
    move_to(chest_pos)
    chest = place_entity(Prototype.IronChest, Direction.UP, chest_pos)
    assert chest, f"Failed to place iron chest at {chest_pos}"
    print(f"Placed iron chest at {chest.position}")

    # """[SYNTHESISED]
    # Name: connect_drill_to_chest_with_inserter
    # Objective: Connect a drill to a chest using a burner inserter and transport belt
    # Mining setup: We have a drill and a chest entity on the map
    # Inventory: We have burner inserters and transport belts in our inventory
    # :param chest: The chest entity where the output of the drill needs to go
    # :param drill: The drill entity that produces output for the chest
    # :return inserter: The inserter entity that inserts items into the chest
    # [END OF SYNTHESISED]"""
    inserter = connect_drill_to_chest_with_inserter(chest=chest, drill=miner)
    
    # Fuel the inserter with coal
    insert_item(Prototype.Coal, inserter, quantity=5)
    print("Fuelled inserter with coal")

    # Wait for the system to produce some iron ore
    print("Waiting for 15 seconds to allow the system to produce iron ore...")
    sleep(15)

    # Check the chest to see if iron ore has been produced
    chest_inventory = inspect_inventory(chest)
    iron_ore_in_chest = chest_inventory.get(Prototype.IronOre, 0)
    assert iron_ore_in_chest > 0, "No iron ore was produced"
    print(f"Successfully produced {iron_ore_in_chest} iron ore.")
    print("Automated iron ore mine created and functioning correctly!")