# Place a drill to coal ore patch
coal_ore_patch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
assert coal_ore_patch, "No coal ore patch found"
print(f"coal ore patch found at {coal_ore_patch.bounding_box.center}")

# Place burner mining drill on copper ore patch
move_to(coal_ore_patch.bounding_box.center)
drill = place_entity(Prototype.BurnerMiningDrill, direction=Direction.RIGHT,
                         position=coal_ore_patch.bounding_box.center)
assert drill, "Failed to place burner mining drill"
print(f"Burner mining drill placed at {drill.position}")

# Fuel the burner mining drill
drill_with_coal = insert_item(Prototype.Coal, drill, quantity=50)
assert drill_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel burner mining drill"
print(f"Inserted {drill_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into burner mining drill")

# Place inserter next to the drill
drill_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=drill.position,
                                direction=Direction.RIGHT)
assert drill_inserter, "Failed to place inserter"
print(f"Inserter placed at {drill_inserter.position}")

# Fuel the inserter
inserter_with_coal = insert_item(Prototype.Coal, drill_inserter, quantity=2)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"
print(f"Inserted {inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into inserter")

# move to 0,0 and Place chest there
move_to(Position(x=0, y=0))
chest = place_entity(Prototype.WoodenChest, position=Position(x=0, y=0))
assert chest, "Failed to place chest"

# place a burner inserter next to the chest
chest_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=chest.position, direction=Direction.RIGHT)
assert chest_inserter, "Failed to place inserter"
print(f"Inserter placed at {chest_inserter.position}")

# rotate the inserter to face the chest
chest_inserter = rotate_entity(chest_inserter, Direction.LEFT)
assert chest_inserter.direction.value == Direction.LEFT.value, "Failed to rotate inserter"

# add coal to the inserter
inserter_with_coal = insert_item(Prototype.Coal, chest_inserter, quantity=5)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"

# connect drill_inserter to chest_inserter with transport belts
belts = connect_entities(drill_inserter, chest_inserter, connection_type=Prototype.TransportBelt)
assert belts, "Failed to connect entities with transport belts"

# sleep for 30 seconds
sleep(15)

# check if the chest has coal
chest_inventory = inspect_inventory(chest)
coal = chest_inventory.get(Prototype.Coal, 0)
assert coal > 0, f"No coal produced after 30 seconds. Check fuel levels and connections."

# place another inserter next to the chest
chest_inserter2 = place_entity_next_to(Prototype.BurnerInserter, reference_position=chest.position, direction=Direction.LEFT)
assert chest_inserter2, "Failed to place inserter"
print(f"Second Inserter placed at {chest_inserter2.position}")

# add coal to the inserter
inserter_with_coal = insert_item(Prototype.Coal, chest_inserter2, quantity=5)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"

# Place a drill to copper ore patch
copper_ore_patch = get_resource_patch(Resource.CopperOre, nearest(Resource.CopperOre))
assert copper_ore_patch, "No copper ore patch found"
print(f"copper ore patch found at {copper_ore_patch.bounding_box.center}")

# Place burner mining drill on copper ore patch
move_to(copper_ore_patch.bounding_box.center)
copper_drill = place_entity(Prototype.BurnerMiningDrill, direction=Direction.RIGHT,
                         position=copper_ore_patch.bounding_box.center)
assert copper_drill, "Failed to place burner mining drill"
print(f"Burner mining drill placed at {copper_drill.position}")

# place a burner inserter next to the copper drill
copper_drill_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=copper_drill.position, direction=Direction.LEFT)
assert copper_drill_inserter, "Failed to place inserter"
print(f"Inserter placed at {copper_drill_inserter.position}")

# rotate the inserter to face the drill
copper_drill_inserter = rotate_entity(copper_drill_inserter, Direction.RIGHT)
assert copper_drill_inserter.direction.value == Direction.RIGHT.value, "Failed to rotate inserter"

# add coal to the inserter
inserter_with_coal = insert_item(Prototype.Coal, copper_drill_inserter, quantity=5)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"

# connect drill_inserter to chest_inserter with transport belts
belts = connect_entities(chest_inserter2, copper_drill_inserter, connection_type=Prototype.TransportBelt)
assert belts, "Failed to connect entities with transport belts"
print(f"Successfully created an factory that gets coal from a chest and mines copper ore")