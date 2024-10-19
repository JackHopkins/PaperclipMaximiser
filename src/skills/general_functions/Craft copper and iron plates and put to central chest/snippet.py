# Place a drill to copper ore patch
copper_ore_patch = get_resource_patch(Resource.CopperOre, nearest(Resource.CopperOre))
assert copper_ore_patch, "No copper ore patch found"
print(f"copper ore patch found at {copper_ore_patch.bounding_box.center}")

# Place burner mining drill on copper ore patch
move_to(copper_ore_patch.bounding_box.center)
drill = place_entity(Prototype.BurnerMiningDrill, direction=Direction.RIGHT,
                         position=copper_ore_patch.bounding_box.center)
assert drill, "Failed to place burner mining drill"
print(f"Burner mining drill placed at {drill.position}")

# Fuel the burner mining drill
drill_with_coal = insert_item(Prototype.Coal, drill, quantity=5)
assert drill_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel burner mining drill"
print(f"Inserted {drill_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into burner mining drill")

# Place stone furnace next to drill
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=drill.position, direction=Direction.RIGHT)
assert furnace, "Failed to place stone furnace"
print(f"Stone furnace placed at {furnace.position}")

# Fuel the stone furnace
furnace_with_coal = insert_item(Prototype.Coal, furnace, quantity=5)
assert furnace_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel stone furnace"
print(f"Inserted {furnace_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into stone furnace")

# Place inserter next to furnace
furnace_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=furnace.position,
                                direction=Direction.RIGHT)
assert furnace_inserter, "Failed to place inserter"
print(f"Inserter placed at {furnace_inserter.position}")

# Fuel the inserter
inserter_with_coal = insert_item(Prototype.Coal, furnace_inserter, quantity=2)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"
print(f"Inserted {inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into inserter")

# Place a drill to iron ore patch
iron_ore_patch = get_resource_patch(Resource.IronOre, nearest(Resource.IronOre))
assert iron_ore_patch, "No iron ore patch found"
print(f"iron ore patch found at {iron_ore_patch.bounding_box.center}")

# Place burner mining drill on iron ore patch
move_to(iron_ore_patch.bounding_box.center)
iron_drill = place_entity(Prototype.BurnerMiningDrill, direction=Direction.RIGHT,
                         position=iron_ore_patch.bounding_box.center)
assert drill, "Failed to place burner mining drill"
print(f"Burner mining drill placed at {drill.position}")

# Fuel the burner mining drill
drill_with_coal = insert_item(Prototype.Coal, iron_drill, quantity=5)
assert drill_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel burner mining drill"
print(f"Inserted {drill_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into burner mining drill")

# Place stone furnace next to drill
iron_furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=iron_drill.position, direction=Direction.RIGHT)
assert furnace, "Failed to place stone furnace"
print(f"Stone furnace placed at {furnace.position}")

# Fuel the stone furnace
furnace_with_coal = insert_item(Prototype.Coal, iron_furnace, quantity=5)
assert furnace_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel stone furnace"
print(f"Inserted {furnace_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into stone furnace")

# Place inserter next to furnace
iron_furnace_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=iron_furnace.position,
                                direction=Direction.RIGHT)
assert iron_furnace_inserter, "Failed to place inserter"
print(f"Inserter placed at {iron_furnace_inserter.position}")

# Fuel the inserter
inserter_with_coal = insert_item(Prototype.Coal, iron_furnace_inserter, quantity=2)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"
print(f"Inserted {inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0)} coal into inserter")

# move to 0,0 and Place chest there
move_to(Position(x=0, y=0))
chest = place_entity(Prototype.WoodenChest, position=Position(x=0, y=0))
assert chest, "Failed to place chest"

# place a burner inserter next to the chest
chest_inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=chest.position, direction=Direction.LEFT)
assert chest_inserter, "Failed to place inserter"
print(f"Inserter placed at {chest_inserter.position}")

# rotate the inserter to face the chest
chest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)
assert chest_inserter.direction.value == Direction.RIGHT.value, "Failed to rotate inserter"

# add coal to the inserter
inserter_with_coal = insert_item(Prototype.Coal, chest_inserter, quantity=5)
assert inserter_with_coal.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"

# connect furnace_inserter to chest_inserter with transport belts
belts = connect_entities(furnace_inserter, chest_inserter, connection_type=Prototype.TransportBelt)
assert belts, "Failed to connect entities with transport belts"

# connect iron_furnace_inserter to chest_inserter with transport belts
belts = connect_entities(iron_furnace_inserter, chest_inserter, connection_type=Prototype.TransportBelt)
assert belts, "Failed to connect entities with transport belts"

# sleep for 15 seconds to wait for the plates to be produced
sleep(15)
# check if the chest has copper plates
chest_inventory = inspect_inventory(chest)
copper_plates = chest_inventory.get(Prototype.CopperPlate, 0)
assert copper_plates > 0, f"No copper plates produced after 30 seconds. Check fuel levels and connections."

# check if the chest has iron plates
iron_plates = chest_inventory.get(Prototype.IronPlate, 0)
assert iron_plates > 0, f"No iron plates produced after 15 seconds. Check fuel levels and connections."
print(f"Successfully created a factory for copper and iron plates")