

# Find the nearest iron ore patch
iron_ore_patch = get_resource_patch(Resource.IronOre, nearest(Resource.IronOre))

# Move to the center of the iron ore patch
move_to(iron_ore_patch.bounding_box.left_top)

# Place burner mining drill
miner = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, iron_ore_patch.bounding_box.left_top)
assert miner, f"Failed to place burner mining drill at {iron_ore_patch.bounding_box.left_top}"

# Place a transport belt from the miner's output
iron_belt_start = place_entity_next_to(Prototype.TransportBelt, miner.position, Direction.DOWN, spacing=0)
assert iron_belt_start.position.is_close(miner.drop_position, 1)
# Place 5 stone furnaces along the belt with burner inserters facing down from above
furnace_line_start = place_entity_next_to(Prototype.StoneFurnace, miner.drop_position, Direction.DOWN,
                                               spacing=2)
assert furnace_line_start.position.is_close(iron_belt_start.output_position, 1)
# Create a row of burner inserters to fuel the furnaces from the belt
inserter_line_start = place_entity_next_to(Prototype.BurnerInserter, furnace_line_start.position, Direction.UP,
                                                spacing=0)
assert inserter_line_start.position.is_close(furnace_line_start.position, 1)
inserter_line_start = rotate_entity(inserter_line_start, Direction.DOWN)


# create the row of furnaces
current_furnace = furnace_line_start
current_inserter = inserter_line_start
for _ in range(3):
    current_furnace = place_entity_next_to(Prototype.StoneFurnace, current_furnace.position, Direction.RIGHT,
                                                spacing=1)
    current_inserter = place_entity_next_to(Prototype.BurnerInserter, current_furnace.position,
                                                 Direction.UP, spacing=0)
    current_inserter = rotate_entity(current_inserter, Direction.DOWN)
    assert current_furnace, f"Failed to place stone furnace at {current_furnace.position}"
    assert current_inserter, f"Failed to place inserter at {current_inserter.position}"

# Connect furnaces with transport belt
above_current_furnace = Position(x=current_furnace.position.x, y=current_furnace.position.y - 2.5)
connect_entities(iron_belt_start.output_position, above_current_furnace, Prototype.TransportBelt)
print("Successfully built a row of 5 stone furnaces fueled by a burner mining drill")
