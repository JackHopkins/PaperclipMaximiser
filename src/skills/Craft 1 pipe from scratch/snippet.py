
from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)

# Assert that we have enough stone
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Not enough stone mined. Expected at least 5, but got {stone_count}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)

# Assert that we have crafted the stone furnace
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=5)

# Assert that we have enough coal
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 5, f"Not enough coal mined. Expected at least 5, but got {coal_count}"

# 4. Mine iron ore
iron_ore_position = nearest(Resource.IronOre)
move_to(iron_ore_position)
harvest_resource(iron_ore_position, quantity=1)

# Assert that we have enough iron ore
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 1, f"Not enough iron ore mined. Expected at least 1, but got {iron_ore_count}"

# 5. Place stone furnace
furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_ore_position)

# Assert that the furnace was placed successfully
assert furnace is not None, "Failed to place stone furnace"

# 6. Smelt iron ore into iron plate
insert_item(Prototype.Coal, furnace, quantity=1)
insert_item(Prototype.IronOre, furnace, quantity=1)

# Wait for smelting to complete
sleep(10)

# 7. Extract iron plate
extract_item(Prototype.IronPlate, furnace.position, quantity=1)

# Assert that we have the iron plate
iron_plate_count = inspect_inventory()[Prototype.IronPlate]
assert iron_plate_count >= 1, f"Failed to smelt iron plate. Expected 1, but got {iron_plate_count}"

# 8. Craft pipe
craft_item(Prototype.Pipe, quantity=1)

# Assert that we have crafted the pipe
pipe_count = inspect_inventory()[Prototype.Pipe]
assert pipe_count >= 1, f"Failed to craft pipe. Expected 1, but got {pipe_count}"

print("Successfully crafted 1 pipe from scratch!")
