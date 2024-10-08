from factorio_instance import *

from factorio_instance import *

# Step 1: Mine raw resources
# Mine enough iron ore for the plates, pipes and gear wheels
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 40)
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 40, f"Failed to mine enough iron ore. Expected 40, but got {iron_ore_count}"

# Mine enough stone for 1 furnace
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, 5)
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"

# Mine enough coal for the furnaces
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, 20)
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 20, f"Failed to mine enough coal. Expected 20, but got {coal_count}"


# Step 2: Craft first stone furnace
craft_item(Prototype.StoneFurnace, 1)
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# Step 3: Smelt iron plates
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = coal_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 20)
insert_item(Prototype.IronOre, furnace, 40)

# Wait for smelting to complete
sleep(30)  # Increased sleep time

# Extract iron plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 30)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 40:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 40 iron plates
iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_in_inventory >= 40, f"Failed to smelt enough iron plates. Expected 40, but got {iron_in_inventory}"

# 5. Craft 8 iron gear wheels
craft_item(Prototype.IronGearWheel, 8)  
iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]  
assert iron_gear_count >= 8, f"Failed to craft 8 iron gears. Current count: {iron_gear_count}"

# 6. Craft 5 pipes
craft_item(Prototype.Pipe, 5)
pipe_count = inspect_inventory()[Prototype.Pipe]
assert pipe_count >= 5, f"Failed to craft 5 pipes. Current count: {pipe_count}"

# 7 Craft steam engine and check if steam engine was crafted
craft_item(Prototype.SteamEngine, 1)
inventory = inspect_inventory()
assert inventory[Prototype.SteamEngine] >= 1, f"Failed to craft steam engine. Inventory: {inventory[Prototype.SteamEngine]}"

print("Successfully crafted 1 steam engine!")
