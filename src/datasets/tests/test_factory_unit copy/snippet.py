
# move to nearest coal and place burner mining drill with a burner inserter
move_to(nearest(Resource.Coal))
burner_mining_drill = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.Coal))
burner_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                            reference_position=burner_mining_drill.position,
                                            direction_from=DOWN,
                                            spacing=1)
assert burner_inserter, "Failed to place burner inserter"
assert burner_mining_drill, "Failed to place burner mining drill"

# connect burner mining drill and inserter with transport belt
belts = connect_entities(burner_mining_drill, burner_inserter, connection_type=Prototype.TransportBelt)
assert belts

# insert coal into burner mining drill
burner_mining_drill: BurnerMiningDrill = insert_item(Prototype.Coal, burner_mining_drill, 5)
assert burner_mining_drill.remaining_fuel == 5

# move to nearest iron ore and place burner mining drill
nearest_iron_ore = nearest(Resource.IronOre)
move_to(nearest_iron_ore)
iron_mining_drill = place_entity(Prototype.BurnerMiningDrill, position=nearest_iron_ore)
assert iron_mining_drill, "Failed to place iron mining drill"

# add a stone furnace next to the iron mining drill
stone_furnace = place_entity(Prototype.StoneFurnace, position=iron_mining_drill.drop_position)
assert stone_furnace, "Failed to place stone furnace"
        
# add a burner inserter to move coal to the iron mining drill      
coal_to_iron_drill_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                                                reference_position=iron_mining_drill.position,
                                                                direction_from=DOWN,
                                                                spacing=1)
assert coal_to_iron_drill_inserter, "Failed to place coal to iron drill inserter"

# add a burner inserter to move coal to the stone furnace
coal_to_smelter_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                                             reference_position=stone_furnace.position,
                                                             direction_from=RIGHT,
                                                             spacing=1)

# connect the burner mining drill and inserter with a transport belt        
coal_to_drill_belt = connect_entities(belts[-1], coal_to_iron_drill_inserter.pickup_position,
                                                   connection_type=Prototype.TransportBelt)
assert coal_to_drill_belt, "Failed to connect coal to iron drill belt"

# connect the coal to the stone furnace with a transport belt
coal_to_smelter_belt = connect_entities(coal_to_drill_belt[-1], coal_to_smelter_inserter.pickup_position,
                                                     connection_type=Prototype.TransportBelt)
assert coal_to_smelter_belt, "Failed to connect coal to smelter belt"
