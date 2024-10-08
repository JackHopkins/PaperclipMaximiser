from factorio_instance import *

from factorio_instance import *

# Step 1: Mine raw resources
# Mine enough iron ore for the plates
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 10)
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 10, f"Failed to mine enough iron ore. Expected 10, but got {iron_ore_count}"

# Mine enough stone for 1 furnace
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, 5)
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"

# Mine enough coal for the furnaces
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, 10)
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 10, f"Failed to mine enough coal. Expected 10, but got {coal_count}"


# Step 2: Craft stone furnace
craft_item(Prototype.StoneFurnace, 1)
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# Step 3: Smelt iron plates
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = coal_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 10)
insert_item(Prototype.IronOre, furnace, 10)

# Wait for smelting to complete
sleep(10)  # Increased sleep time

# Extract iron plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 10)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 10:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 10 iron plates
iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_in_inventory >= 10, f"Failed to smelt enough iron plates. Expected 10, but got {iron_in_inventory}"

# Step 4: Insert steel plates into the furnace
insert_item(Prototype.IronPlate, furnace, 10)

# Wait for smelting to complete
sleep(10)

# Extract steel plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.SteelPlate, furnace.position, 2)
    iron_plates_extracted = inspect_inventory()[Prototype.SteelPlate]
    if iron_plates_extracted >= 2:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Final check
final_steel_count = inspect_inventory()[Prototype.SteelPlate]
assert final_steel_count >= 2, f"Failed to craft 2 steel plates. Current amount: {final_steel_count}"

print(f"Successfully crafted {final_steel_count} steel plates!")
