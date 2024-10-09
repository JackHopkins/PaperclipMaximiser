
# Find the nearest coal patch and move to it
coal_patch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
# Move to the center of the coal patch
move_to(coal_patch.bounding_box.left_top)

# Place the first drill
drill = place_entity(Prototype.BurnerMiningDrill, Direction.UP, coal_patch.bounding_box.left_top)
assert drill, "Failed to place the first drill"

# Place a chest next to the first drill to collect coal
chest = place_entity(Prototype.IronChest, Direction.RIGHT, drill.drop_position)
assert chest, "Failed to place the chest"
    
# Connect the first drill to the chest with an inserter
inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.UP, spacing=0)
first_inserter = inserter
assert inserter, "Failed to place the inserter"

# Place an inserter south of the drill to insert coal into the drill
drill_bottom_y = drill.position.y + drill.dimensions.height
drill_inserter = place_entity(Prototype.BurnerInserter, Direction.UP, Position(x=drill.position.x, y=drill_bottom_y))
drill_inserter = rotate_entity(drill_inserter, Direction.UP)
first_drill_inserter = drill_inserter
assert drill_inserter, "Failed to place the drill inserter"

# Start the transport belt from the chest
move_to(inserter.drop_position)

# Place additional drills and connect them to the belt in a loop
drills = []
for i in range(1, 3):
    # Place the next drill
    next_drill = place_entity_next_to(Prototype.BurnerMiningDrill, drill.position, Direction.RIGHT, spacing=2)
    next_drill = rotate_entity(next_drill, Direction.UP)
    drills.append(next_drill)
    # Place a chest next to the next drill to collect coal
    chest = place_entity(Prototype.IronChest, Direction.RIGHT, next_drill.drop_position)
    assert chest, "Failed to place the chest"
    # Place an inserter to connect the chest to the transport belt
    next_inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.UP, spacing=0)
    assert next_inserter, "Failed to place the inserter"
    # Place an insert underneath the drill to insert coal into the drill
    drill_bottom_y = next_drill.position.y + next_drill.dimensions.height
    drill_inserter = place_entity(Prototype.BurnerInserter, Direction.UP, Position(x=next_drill.position.x, y=drill_bottom_y))
    drill_inserter = rotate_entity(drill_inserter, Direction.UP)
    assert drill_inserter, "Failed to place the drill inserter"
    # Extend the transport belt to the next drill
    connect_entities(inserter.drop_position, next_inserter.drop_position, Prototype.TransportBelt)
    # Update the drill reference for the next iteration
    drill = next_drill
    inserter = next_inserter
    next_drill_inserter = drill_inserter

# Connect the drop position of the final drill block to the inserter that is loading it with coal
connect_entities(next_inserter.drop_position, next_drill_inserter.pickup_position, Prototype.TransportBelt)

# Connect that inserter to the inserter that is loading the first drill with coal
connect_entities(next_drill_inserter.pickup_position, first_drill_inserter.pickup_position, Prototype.TransportBelt)

# Connect the first drill inserter to the drop point of the first inserter
connect_entities(first_drill_inserter.pickup_position, first_inserter.drop_position, Prototype.TransportBelt)

# Initialize the system by adding some coal to each drill and inserter
for drill in drills:
    insert_item(Prototype.Coal, drill, 5)
    assert drill.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel the drill"
print(f"Auto-refilling coal mining system with {num_drills} drills has been built!")