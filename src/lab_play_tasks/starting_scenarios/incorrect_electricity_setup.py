
# log your general idea what you will do next
print(f"I will create a power generation setup with a steam engine")

# get the water position
water_position = nearest(Resource.Water)
# moveto water positon
move_to(water_position)
# first place offshore pump on the water system
offshore_pump = place_entity(Prototype.OffshorePump, position=water_position)
print(f"Placed offshore pump to get water at {offshore_pump.position}")


# place the boiler next to offshore pump
boiler = place_entity_next_to(Prototype.Boiler, reference_position = offshore_pump.position, spacing = 1, direction = Direction.DOWN)
print(f"Placed boiler to generate steam at {boiler.position}. This will be connected to the offshore pump at {offshore_pump.position}")
# add coal to boiler to start the power generation
boiler = insert_item(Prototype.Coal, boiler, 10)


# place the steam engine next to boiler
steam_engine = place_entity_next_to(Prototype.SteamEngine, reference_position = boiler.position, spacing = 1, direction = Direction.DOWN)

print(f"Placed steam_engine to generate electricity at {steam_engine.position}. This will be connected to the boiler at {boiler.position} to generate electricity")

# Connect entities in order
water_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)
print(f"Connected offshore pump at {offshore_pump.position} to boiler at {boiler.position} with pipes {water_pipes}")
steam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)
print(f"Connected boiler at {boiler.position} to steam_engine at {steam_engine.position} with pipes {water_pipes}")

# check that it has power
# sleep for 5 seconds to ensure flow
sleep(5)
# update the entity
steam_engine = get_entity(Prototype.SteamEngine, position = steam_engine.position)
# check that the steam engine is generating power
assert steam_engine.energy > 0, f"Steam engine is not generating power"
print(f"Steam engine at {steam_engine.position} is generating power!")