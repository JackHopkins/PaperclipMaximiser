def place_and_power_electric_mining_drill_on_copper():
    """
    Objective: We need to place a electric mining drill on copper ore and create a steam energy setup to power it.
    Mining setup: There are no entities on the map
    Inventory: We have a boiler, electric mining drill, offshore pump, steam engine and power poles in our inventory
    """
    # [PLANNING] To create this we need to first place the offshore pump, boiler and steam engine
    # Then we need to put a electric mining drill on copper patch
    # Then we need to connect the offshore pump to the boiler with pipes
    # Then we need to power the boiler with coal and check the warning of engine to ensure it generates electricity using the boiler
    # Finally we need to connect the drill with engine with power poles and check the warning to ensure it is connected to the power network [END OF PLANNING]
    # We dont need to craft any resources for this task as all resources are present in inventory 
    
    # print out initial inventory
    initial_inventory = inspect_inventory()
    print(f"Inventory at starting: {initial_inventory}")
    
    # First we need to find the nearest copper patch
    # VERY IMPORTANT: FIRST MOVE TO THE POSITION WE PLACE THE DRILL AS WE CAN'T PLACE IT FROM A FAR DISTANCE
    copper_position = nearest(Resource.CopperOre)
    assert copper_position, "No copper found nearby"
    move_to(copper_position)
    print(f"Moved to copper patch at {copper_position}")

    # put down the electric mining drill
    electric_mining_drill = place_entity(Prototype.ElectricMiningDrill, Direction.DOWN, copper_position)
    assert electric_mining_drill, "Failed to place electric mining drill"
    print(f"Electric mining drill placed at {electric_mining_drill.position}")

    # Place offshore pump near water
    water_position = nearest(Resource.Water)
    assert water_position, "No water source found nearby"
    move_to(water_position)
    offshore_pump = place_entity(Prototype.OffshorePump, Direction.DOWN, water_position)
    assert offshore_pump, "Failed to place offshore pump"
    print(f"Offshore pump placed at {offshore_pump.position}")

    # Place boiler next to offshore pump
    boiler = place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.DOWN, spacing=2)
    assert boiler, "Failed to place boiler"
    print(f"Boiler placed at {boiler.position}")
    print(f"Current inventory: {inspect_inventory()}")

    # add coal to the boiler
    boiler_with_coal = insert_item(Prototype.Coal, boiler, quantity=5)
    print(f"Inventory after adding coal: {inspect_inventory()}")

    # Connect offshore pump to boiler with pipes
    pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)
    assert pipes, "Failed to connect offshore pump to boiler"
    print(f"Pipes placed between offshore pump and boiler")

    # Place steam engine next to boiler
    steam_engine = place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.LEFT, spacing=2)
    assert steam_engine, "Failed to place steam engine"
    print(f"Steam engine placed at {steam_engine.position}")

    # Connect boiler to steam engine with pipes
    pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)
    assert pipes, "Failed to connect boiler to steam engine"
    print(f"Pipes placed between boiler and steam engine")

    # check if the boiler is receiving electricity
    # if it says not connected to power network, then it is working
    # it just isn't connected to any power poles
    inspected_steam_engine = inspect_entities(position=steam_engine.position, radius=1).get_entity(Prototype.SteamEngine)
    assert inspected_steam_engine.warning == 'not connected to power network'
    print(f"Steam engine warning: {inspected_steam_engine.warning}")

    # Connect electric drill to steam engine with power poles
    poles = connect_entities(electric_mining_drill, steam_engine, Prototype.SmallElectricPole)
    assert poles, "Failed to connect drill to steam engine"
    print(f"Connected electric mining drill to steam engine with power poles")

    # verify that there is not warning for assmbling machine
    # if the warning is None, then it is connected to the power network
    inspected_drill = inspect_entities(position=electric_mining_drill.position, radius=1).get_entity(Prototype.ElectricMiningDrill)
    assert inspected_drill.warning is None, "Drill not connected to power network"
