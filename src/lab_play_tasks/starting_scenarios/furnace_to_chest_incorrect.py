iron_ore_loc = nearest(Resource.IronOre)
print(f"found iron ore at {iron_ore_loc}")
move_to(iron_ore_loc)
print(f"Moved to iron ore location")
furnace = place_entity(Prototype.StoneFurnace, position = iron_ore_loc)
furnace = insert_item(Prototype.Coal, furnace, 30)
print(f"Placed a drill at location ({furnace.position}) and inserted coal")

# insert iron ore into furnace
furnace = insert_item(Prototype.IronOre, furnace, 30)
print(f"Inserted iron ore into furnace at {furnace.position}")

# put a inserter next to the furnace
furnace_output_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position = furnace.position, spacing = 0)
# no need to rotate as inserter takes from furnace
furnace_output_inserter = insert_item(Prototype.Coal, furnace_output_inserter, 30)
print(f"Placed inserter at {furnace_output_inserter.position} and inserted coal")

chest_pos = Position(x = furnace.position.x - 9, y =  furnace.position.y)
move_to(chest_pos)
chest = place_entity(Prototype.WoodenChest, position = chest_pos)
print(f"Placed chest to pickup plates at ({chest.position})")


belts = connect_entities(furnace_output_inserter.drop_position, chest.position, Prototype.TransportBelt)
print(f"Connected furnace_output_inserter at {furnace_output_inserter.position} to chest at {chest.position} with belts {belts}")

# wait for 10 seconds and check if chest has plates
sleep(10)

# get the updated furnace entity
chest = get_entity(Prototype.WoodenChest, position = chest.position)
# get the inventory
chest_inventory = inspect_inventory(chest)
# get the iron plate in furnace inventory
iron_plates_in_chest = chest_inventory[Prototype.IronPlate]
# check for iron plates
assert iron_plates_in_chest > 0, "No plates in chest"