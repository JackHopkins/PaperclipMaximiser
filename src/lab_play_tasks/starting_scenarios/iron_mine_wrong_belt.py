iron_ore_loc = nearest(Resource.IronOre)
print(f"found iron ore at {iron_ore_loc}")
move_to(iron_ore_loc)
print(f"Moved to iron ore location")
drill = place_entity(Prototype.BurnerMiningDrill, position = iron_ore_loc)
drill = insert_item(Prototype.Coal, drill, 30)
print(f"Placed drill at iron ore location ({drill.position}) and inserted coal")

furnace_pos = Position(x = drill.position.x - 9, y =  drill.position.y)
move_to(furnace_pos)
furnace = place_entity(Prototype.StoneFurnace, position = furnace_pos)
furnace = insert_item(Prototype.Coal, furnace, 30)
print(f"Placed furnace to smelt iron ore into plates ({furnace.position}) and inserted coal")


belts = connect_entities(drill.drop_position, furnace.position, Prototype.TransportBelt)
print(f"Connected drill at {drill.position} to furnace at {furnace.position} with belts {belts}")

# wait for 30 seconds and check if furnace is smelting plates
sleep(30)

# get the updated furnace entity
furnace = get_entity(Prototype.StoneFurnace, position = furnace.position)
# get the inventory
furnace_inventory = inspect_inventory(furnace)
# get the iron plate in furnace inventory
iron_plates_in_chest = furnace_inventory[Prototype.IronPlate]
# check for iron plates
assert iron_plates_in_chest > 0, "No plates in furnace"