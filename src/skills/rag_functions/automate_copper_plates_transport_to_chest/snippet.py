def create_an_automated_copper_plate_mine():
    """
    Objective: We need to create a mining setup that mines copper ore, smelts it to plates and puts it into a chest further away from the drill
    Mining setup: There are no entities on the map
    Inventory: We have all the required mining items in our inventory - more than one drill, more than one inserter, and enough transport belts, but we do not have a chest
    """
    # [PLANNING]
    # To solve this objective, we first need to place down the drill at a copper patch and fuel it
    # We then need to place the furnace with coal at the drop position of the drill. We also need to add a inserter that takes items from the furnace
    # Then we need to mine wood, craft the chest, place down a chest with an inserter that puts to the chest that is also fueled
    # We need to rotate the inserter to put items into the chest as by default it takes from the chest
    # finally we need to connect the chest inserter's pickup position and the furnace inserters drop position with transport belts
    # We need to only craft the chest
    # [END OF PLANNING]

    # First we need to do initial prints for logging
    # First print out the recipe for wooden chest
    chest_recipe = get_recipe(Prototype.WoodenChest)
    print(f"Chest recipe: {chest_recipe}")
    # also print out the starting inventory
    print(f"Inventory at starting: {inspect_inventory()}")

    # First we need to find the nearest copper patch
    copper_position = nearest(Resource.CopperOre)
    assert copper_position, "No copper found nearby"
    move_to(copper_position)
    print(f"Moving to copper patch at {copper_position}")

    # Get the copper patch details
    copper_patch = get_resource_patch(Resource.CopperOre, copper_position, radius=10)
    print(copper_patch)
    assert copper_patch, "No copper patch found within radius"

    # Place the mining drill to the copper patch. We need to place it in the center of the patch
    miner = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, copper_patch.bounding_box.center)
    assert miner, "Failed to place burner mining drill"
    print(f"Placed mining drill at {miner.position}")

    # We then need to fuel the mining drill with coal
    miner_with_coal = insert_item(Prototype.Coal, miner, quantity=5)
    print(f"Fuelled mining drill with coal: {miner_with_coal}")
    print(f"Inventory after fuelling: {inspect_inventory()}")

    # We then need to add a furnace at the drop position of the mining drill
    # We need to use place_entity as we need to place it at exactly the drop position of the drill
    # There should be no spacing
    furnace = place_entity(Prototype.StoneFurnace, Direction.DOWN, miner.drop_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # We then need to fuel the furnace with coal
    furnace_with_coal = insert_item(Prototype.Coal, furnace, quantity=5)
    print(f"Fuelled mining drill with coal: {furnace_with_coal}")
    print(f"Inventory after fuelling: {inspect_inventory()}")

    # We then need to mine wood to craft a chest
    wood_position = nearest(Resource.Wood)
    move_to(wood_position)
    print(f"Moving to wood patch at {wood_position}")

    # Get the wood patch details
    wood_patch = get_resource_patch(Resource.Wood, wood_position, radius=10)
    print(wood_patch)
    assert wood_patch, "No wood patch found within radius"

    # Mine wood to craft a chest
    harvest_resource(wood_position, 10)
    wood_count = inspect_inventory()[Resource.Wood]
    assert wood_count >= 10, f"Failed to mine enough wood. Expected 10, but got {wood_count}"
    print(f"Mined {wood_count} wood")
    print(f"Current inventory: {inspect_inventory()}")

    # Craft a chest
    craft_item(Prototype.WoodenChest, 1)
    chest_count = inspect_inventory()[Prototype.WoodenChest]
    assert chest_count >= 1, f"Failed to craft chest. Expected 1, but got {chest_count}"
    print(f"Crafted {chest_count} chest")

    # Place a chest a bit further away from the drill to ensure no collision
    # we place it down from the drill as the drill is facing down
    # VERY IMPORTANT: FIRST MOVE TO THE POSITION WE PLACE IT TO AS WE CAN'T PLACE IT FROM A FAR DISTANCE
    chest_pos = Position(x=miner.position.x, y=miner.position.y - 7)
    move_to(chest_pos)
    chest = place_entity(Prototype.WoodenChest, Direction.UP, chest_pos)
    assert chest, f"Failed to place chest at {chest}"
    print(f"Placed chest at {chest.position}")

    # [SUBFUNCTION]
    # Name: connect_a_drills_output_to_a_existing_chest
    # Objective: We need to connect a the furnace to a chest with inserters on both at the chest and furnace at the given direction. We have the inserter and transport belts in our inventory
    # Mining setup: We have a furnace and a chest entity on the map 
    # Inventory: We have the inserter and transport belts in our inventory
    # :param chest: The chest entity where the output of the furnace needs to go
    # :param furnace: The furnace entity that produces output for the chest
    # :param direction: The direction where the inserter should be placed
    # :return inserter: The inserter entity that inserts items into the chest
    # [END OF SUBFUNCTION]
    connect_a_furnace_to_a_existing_chest(chest = chest, furnace = furnace, direction = Direction.UP)
    print("Connected the drill to the chest")

    # We will then wait for 10 seconds to let the system produce some copper and put it to the chest
    sleep(10)
    # Check the chest to see if copper has been produced
    chest_inventory = inspect_inventory(chest)
    # get chests inventory
    copper_in_chest = chest_inventory.get(Prototype.CopperOre, 0)
    assert copper_in_chest > 0, "No copper was produced"
    print(f"Successfully produced {copper_in_chest} copper.")