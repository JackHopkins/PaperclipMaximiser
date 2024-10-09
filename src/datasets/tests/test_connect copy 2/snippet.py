

# get the positions of furnace and coal
coal: Position = nearest(Resource.Coal)
furnace_position = Position(x=coal.x, y=coal.y - 10)

# place the furnace and inserter
move_to(furnace_position)
furnace = place_entity(Prototype.StoneFurnace, position=furnace_position)
inserter = place_entity_next_to(Prototype.BurnerInserter,
                                     reference_position=furnace.position,
                                     direction=RIGHT,
                                     spacing=0.5)
inserter = rotate_entity(inserter, Direction.LEFT)
assert furnace , f"Failed to place furnace at {furnace_position}"
assert inserter, f"Failed to place inserter at {inserter.position}"

# place the miner
move_to(coal)
miner = place_entity(Prototype.BurnerMiningDrill, position=coal)
assert miner, f"Failed to place miner at {coal}"

# connect the miner to the furnace
belts_in_inventory = inspect_inventory()[Prototype.TransportBelt]
connection = connect_entities(miner, inserter, connection_type=Prototype.TransportBelt)
assert connection

# make a final check
current_belts_in_inventory = inspect_inventory()[Prototype.TransportBelt]
spent_belts = (belts_in_inventory - current_belts_in_inventory)
assert spent_belts == len(connection)
print(f"Successfully connected miner to furnace using {spent_belts} transport belts")