# inspect the inventory
boilers_in_inventory = inspect_inventory()[Prototype.Boiler]
steam_engines_in_inventory = inspect_inventory()[Prototype.SteamEngine]
pipes_in_inventory = inspect_inventory()[Prototype.Pipe]
# set the direction
DIR = Direction.UP
# move to the nearest water source
water_location = nearest(Resource.Water)
move_to(water_location)

# place an offshore pump at the water source
offshore_pump = place_entity(Prototype.OffshorePump,
                                  position=water_location,
                                  direction=DIR)
assert offshore_pump.direction.value == DIR.value

# Get offshore pump direction and connection point
direction = offshore_pump.direction
# pump connection point
pump_connection_point = offshore_pump.connection_points[0]

# place the boiler next to the offshore pump
boiler = place_entity_next_to(Prototype.Boiler,
                                   reference_position=offshore_pump.position,
                                   direction=direction,
                                   spacing=2)
assert boiler.direction.value == direction.value

# rotate the boiler to face the offshore pump
boiler = rotate_entity(boiler, Direction.next_clockwise(direction))

# insert coal into the boiler
insert_item(Prototype.Coal, boiler, quantity=5)

# connect the boiler and offshore pump with a pipe
offshore_pump_to_boiler_pipes = connect_entities(offshore_pump, boiler, connection_type=Prototype.Pipe)
assert offshore_pump_to_boiler_pipes, "Failed to connect the offshore pump and boiler with pipes"

# place the steam engine next to the boiler
move_to(Position(x=0, y=10))
steam_engine: Entity = place_entity_next_to(Prototype.SteamEngine,
                                                 reference_position=boiler.position,
                                                 direction=DIR,
                                                 spacing=2)

# connect the boiler and steam engine with a pipe
boiler_to_steam_engine_pipes = connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)
inspected_steam_engine = inspect_entities(position=steam_engine.position, radius=1).get_entity(Prototype.SteamEngine)
assert inspected_steam_engine.warning == 'not receiving electricity'
assert steam_engine.direction.value == DIR.value
print("Successfully placed a boiler and a steam engine next to each other in 3 cardinal directions.")