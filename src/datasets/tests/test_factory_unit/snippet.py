# move to nearest water and place offshore pump and boiler
move_to(nearest(Resource.Water))
offshore_pump = place_entity(Prototype.OffshorePump,
                                  position=nearest(Resource.Water))
boiler = place_entity_next_to(Prototype.Boiler,
                                   reference_position=offshore_pump.position,
                                   direction=offshore_pump.direction,
                                   spacing=5)
assert offshore_pump, "Failed to place offshore pump"
assert boiler, "Failed to place boiler"

# connect the boiler and offshore pump with a pipe
water_pipes = connect_entities(boiler, offshore_pump, connection_type=Prototype.Pipe)
assert water_pipes, "Failed to connect boiler and offshore pump with pipes"

# place steam engine next to boiler and connect with pipe
steam_engine = place_entity_next_to(Prototype.SteamEngine,
                                         reference_position=boiler.position,
                                         direction=boiler.direction,
                                         spacing=5)
steam_pipes = connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)
assert steam_pipes, "Failed to connect boiler and steam engine with pipes"
assert steam_engine, "Failed to place steam engine"

# place a coal inserter
coal_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                          reference_position=boiler.position,
                                          direction=Direction.RIGHT,
                                          spacing=1)
coal_inserter = rotate_entity(coal_inserter, Direction.LEFT)
assert coal_inserter, "Failed to place coal inserter"

# move to nearest coal and place burner mining drill with a burner inserter
move_to(nearest(Resource.Coal))
burner_mining_drill = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.Coal))
burner_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                            reference_position=burner_mining_drill.position,
                                            direction=Direction.DOWN,
                                            spacing=0)
burner_inserter = rotate_entity(burner_inserter, Direction.UP)
assert burner_inserter

# connect burner mining drill and inserter with transport belt
belts = connect_entities(burner_mining_drill, burner_inserter, connection_type=Prototype.TransportBelt)
assert belts

# connect coal inserter and boiler with transport belt
coal_to_boiler_belts = connect_entities(belts[-1], coal_inserter, connection_type=Prototype.TransportBelt)
assert coal_to_boiler_belts

# place an assembler
assembler = place_entity_next_to(Prototype.AssemblingMachine1,
                                      reference_position=steam_engine.position,
                                      direction=Direction.LEFT,
                                      spacing=5)
assert assembler

# connect steam engine and assembler with poles
steam_engine_to_assembler_poles = connect_entities(assembler, steam_engine, connection_type=Prototype.SmallElectricPole)
assert steam_engine_to_assembler_poles
