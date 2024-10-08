from factorio_instance import *

# 1. Gather raw materials
# Mine enough stone for 2 furnaces
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, 10)

# Check if we have enough stone
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 10, f"Not enough stone. Expected 10, but got {stone_count}"

# Mine enough iron ore for the plates and pipes
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 10)

# Check if we have enough iron ore
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 10, f"Not enough iron ore. Expected 10, but got {iron_ore_count}"

# Mine enough coal for the furnaces
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, 10)

# Check if we have enough coal
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 10, f"Not enough coal. Expected 10, but got {coal_count}"

# 2. Craft the stone furnaces
craft_item(Prototype.StoneFurnace, 2)

# Check if we have crafted 2 stone furnaces
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 2, f"Not enough stone furnaces. Expected 2, but got {furnace_count}"

# Place one stone furnace for smelting near the coal
player_position = inspect_entities().player_position
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=coal_position, direction=Direction.UP, spacing=1)
assert furnace is not None, "Failed to place stone furnace"

# 4. Smelt iron plates
insert_item(Prototype.Coal, furnace, 5)
insert_item(Prototype.IronOre, furnace, 10)

# Wait for smelting to complete
sleep(20)  # Increased sleep time

# Extract iron plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 10)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 10:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 10 iron plates
iron_plate_count = inspect_inventory()[Prototype.IronPlate]
assert iron_plate_count >= 10, f"Not enough iron plates. Expected 10, but got {iron_plate_count}"

# 5. Craft pipes
craft_item(Prototype.Pipe, 10)

# Check if we have crafted 10 pipes
pipe_count = inspect_inventory()[Prototype.Pipe]
assert pipe_count >= 10, f"Not enough pipes. Expected 10, but got {pipe_count}"

# 6. Craft boiler
craft_item(Prototype.Boiler, 1)

# Final check: Do we have 1 boiler?
boiler_count = inspect_inventory()[Prototype.Boiler]
assert boiler_count >= 1, f"Failed to craft boiler. Expected 1, but got {boiler_count}"

print("Successfully crafted 1 boiler from scratch!")