
# Move to the nearest coal resource and place a burner mining drill
coal_position = nearest(Resource.Coal)
move_to(coal_position)
coal_drill = place_entity(Prototype.BurnerMiningDrill, position=coal_position, direction=Direction.DOWN)
assert coal_drill, "Failed to place coal drill"

# Find the nearest iron ore resource
iron_position = nearest(Resource.IronOre)
# Place the iron mining drill at iron_position, facing down
move_to_iron = move_to(iron_position)
iron_drill = place_entity(Prototype.BurnerMiningDrill, position=iron_position, direction=Direction.DOWN)
assert iron_drill, "Failed to place iron drill"

# Place an inserter to fuel the iron drill from the coal belt
inserter_position = Position(x=iron_drill.position.x + iron_drill.tile_dimensions.tile_width/2, y=iron_drill.position.y-1)
iron_drill_fuel_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                                       reference_position=iron_drill.position,
                                                       direction=Direction.RIGHT,
                                                       spacing=0)
assert iron_drill_fuel_inserter, "Failed to place inserter"
iron_drill_fuel_inserter = rotate_entity(iron_drill_fuel_inserter, Direction.LEFT)
coal_belt = connect_entities(source=coal_drill, target=iron_drill_fuel_inserter, connection_type=Prototype.TransportBelt)
assert coal_belt, "Failed to connect entities with transport belts"

# Extend coal belt to pass next to the furnace position
furnace_position = Position(x=iron_drill.drop_position.x, y=iron_drill.drop_position.y + 1)
assert furnace_position, "Failed to find furnace position"

# Place the furnace at the iron drill's drop position
iron_furnace = place_entity(Prototype.StoneFurnace, position=furnace_position)
assert iron_furnace, "Failed to place furnace"

# Place an inserter to fuel the furnace from the coal belt
furnace_fuel_inserter_position = Position(x=iron_furnace.position.x + 1, y=iron_furnace.position.y)
furnace_fuel_inserter = place_entity(Prototype.BurnerInserter, position=furnace_fuel_inserter_position, direction=Direction.LEFT)
assert furnace_fuel_inserter, "Failed to place inserter"

# Connect the iron drill fuel inserter to the furnace fuel inserter with transport belts
coal_belt_to_furnace = connect_entities(iron_drill_fuel_inserter.pickup_position, furnace_fuel_inserter.pickup_position, connection_type=Prototype.TransportBelt)
coal_belt.extend(coal_belt_to_furnace)
assert coal_belt_to_furnace, "Failed to connect entities with transport belts"

# Place an inserter to move iron plates from the furnace to the chest
furnace_to_chest_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                                      reference_position=iron_furnace.position,
                                                      direction=Direction.DOWN,
                                                      spacing=0)
# Place an iron chest to store iron plates
iron_chest = place_entity_next_to(Prototype.IronChest,
                                       reference_position=iron_furnace.position,
                                       direction=Direction.DOWN,
                                       spacing=1)
assert iron_chest, "Failed to place iron chest"

# Start the system by fueling the coal drill
move_to(coal_position)
insert_item(Prototype.Coal, coal_drill, quantity=10)
assert coal_drill.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel coal drill"

# Wait for some time to let the system produce iron plates
sleep(60)  # Wait for 60 seconds

# Check the iron chest to see if iron plates have been produced
chest_inventory = inspect_inventory(iron_chest)
iron_plates_in_chest = chest_inventory.get(Prototype.IronPlate, 0)
# Assert that some iron plates have been produced
assert iron_plates_in_chest > 0, "No iron plates were produced"
print(f"Successfully produced {iron_plates_in_chest} iron plates.")