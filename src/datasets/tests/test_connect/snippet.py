# Find a water patch
water_patch = get_resource_patch(Resource.Water, nearest(Resource.Water))
move_to(water_patch.bounding_box.left_top)

# Place an offshore pump at the water patch    
offshore_pump = place_entity(Prototype.OffshorePump,
                                      position=nearest(Resource.Water))
assert offshore_pump, "Failed to place offshore pump"

# Place a boiler next to the offshore pump
boiler = place_entity_next_to(Prototype.Boiler,
                                       reference_position=offshore_pump.position,
                                       direction=offshore_pump.direction,
                                       spacing=5)
assert boiler, "Failed to place boiler"
assert boiler.direction.value == Direction.RIGHT.value

# Connect the boiler to the offshore pump with pipes
water_pipes = connect_entities(boiler, offshore_pump, connection_type=Prototype.Pipe)
assert len(water_pipes) == 5 + boiler.tile_dimensions.tile_width/2 + offshore_pump.tile_dimensions.tile_width/2 + 1