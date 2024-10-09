# Find the nearest coal patch
coal_patch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
assert coal_patch is not None, "No coal patch found nearby"
assert coal_patch.size >= 25, f"Coal patch too small: {coal_patch.size} tiles (need at least 25)"

# Place 5 burner mining drills in a line
drills = []
inserters = []
move_to(coal_patch.bounding_box.center)
for i in range(5):
    drill_position = Position(x=coal_patch.bounding_box.left_top.x + i * 2, y=coal_patch.bounding_box.center.y)
    drill = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, drill_position)
    inserter = place_entity_next_to(Prototype.BurnerInserter, drill_position, direction=Direction.UP, spacing=0)
    inserter = rotate_entity(inserter, Direction.DOWN)
    assert drill is not None, f"Failed to place burner mining drill at {drill_position}"
    assert inserter is not None, f"Failed to place inserter at {drill_position}"
    drills.append(drill)
    inserters.append(inserter)

print(f"Placed {len(drills)} burner mining drills")

# Place transport belt parallel to the drills
belt_start = Position(x=drills[0].drop_position.x, y=drills[0].drop_position.y)
belt_end = Position(x=drills[-1].drop_position.x, y=drills[0].drop_position.y)
belt_entities = connect_entities(belt_start, belt_end, Prototype.TransportBelt)
assert len(belt_entities) > 0, "Failed to place transport belt"
belt_to_last_inserter = connect_entities(belt_end, inserters[-1].pickup_position, Prototype.TransportBelt)
assert len(belt_to_last_inserter) > 0, "Failed to connect belt to last inserter"
belt_to_first_inserter = connect_entities(inserters[-1].pickup_position, inserters[0].pickup_position, Prototype.TransportBelt)
assert len(belt_to_first_inserter) > 0, "Failed to connect belt to first inserter"
belt_to_close_loop = connect_entities(inserters[0].pickup_position, belt_start, Prototype.TransportBelt)
assert len(belt_to_close_loop) > 0, "Failed to connect belt to close the loop"
print(f"Placed {len(belt_entities)} transport belt segments")
print("Completed the belt loop")

# Verify the setup
inspection = inspect_entities(coal_patch.bounding_box.center, radius=15)
assert len([e for e in inspection.entities if
            e.name == Prototype.BurnerMiningDrill.value[0]]) == 5, "Not all burner mining drills were placed"
assert len([e for e in inspection.entities if
            e.name == Prototype.BurnerInserter.value[0]]) == 5, "Not all inserters were placed"
# sum all inspected entities with the name transport-belt
total_belts = sum([e.quantity if e.quantity else 1 for e in inspection.entities if e.name == Prototype.TransportBelt.value[0]])
assert total_belts >= 15, "Not enough transport belt segments were placed"
print("All components verified")

# Kickstart the system by placing coal on the belt
coal_placed = insert_item(Prototype.Coal, belt_entities[-1], quantity=10)
assert coal_placed is not None, "Failed to place coal on the belt"
print("System kickstarted with coal")
print("Self-fueling belt of 5 burner mining drills successfully set up")
