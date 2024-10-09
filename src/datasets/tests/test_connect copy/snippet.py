# get the boilers, steam engines and pipes in inventory
boilers_in_inventory = inspect_inventory()[Prototype.Boiler]
steam_engines_in_inventory = inspect_inventory()[Prototype.SteamEngine]
pipes_in_inventory = inspect_inventory()[Prototype.Pipe]

# place a boiler
boiler = place_entity(Prototype.Boiler, position=Position(x=0, y=0), direction=Direction.UP)
assert boiler
assert boiler.direction.value == Direction.UP.value

# place a steam engine
move_to(Position(x=0, y=10))
steam_engine = place_entity(Prototype.SteamEngine, position=Position(x=0, y=10), direction=Direction.UP)
assert steam_engine.direction.value == Direction.UP.value
assert steam_engine

# connect the boiler to the steam engine using pipes
connection: List[Entity] = connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)
assert boilers_in_inventory - 1 == inspect_inventory()[Prototype.Boiler]
assert steam_engines_in_inventory - 1 == inspect_inventory()[Prototype.SteamEngine]
assert pipes_in_inventory - len(connection) == inspect_inventory()[Prototype.Pipe]
assert len(connection) >= 10
print("Successfully connected steam engine to boiler using pipes")