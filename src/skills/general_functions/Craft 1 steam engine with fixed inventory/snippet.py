from factorio_instance import *

# Initial inventory check
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 20, f"Not enough iron plates in inventory. Expected at least 20, but found {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.CopperPlate] >= 20, f"Not enough copper plates in inventory. Expected at least 20, but found {initial_inventory[Prototype.CopperPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, but found {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected at least 3, but found {initial_inventory[Prototype.StoneFurnace]}"

# Step 1 - Mine 20 iron ores to make sure we have enough iron for all required iron plates, circuits and gear wheels
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 20)
iron_count = inspect_inventory()[Resource.IronOre] 
# Check if we have 10 iron ores
assert iron_count >= 20, f"Failed to mine enough iron ores. Expected 20, but got {iron_count}"

# Step 2: Smelt iron plates using furnace in the inventory
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = iron_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 10)
insert_item(Prototype.IronOre, furnace, 20)

# Wait for smelting to complete
sleep(10)  # Increased sleep time
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 20)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 40:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 40 iron plates
iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_in_inventory >= 40, f"Failed to smelt enough iron plates. Expected 40, but got {iron_in_inventory}"

# Step 2 - Craft 8 iron gear wheels
craft_item(Prototype.IronGearWheel, 8)  
iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]  
assert iron_gear_count >= 8, f"Failed to craft 8 iron gears. Current count: {iron_gear_count}"

# Step 3 - Craft 5 pipes
craft_item(Prototype.Pipe, 5)
pipe_count = inspect_inventory()[Prototype.Pipe]
assert pipe_count >= 5, f"Failed to craft 5 pipes. Current count: {pipe_count}"

# Step 4 - Craft steam engine and check if steam engine was crafted
craft_item(Prototype.SteamEngine, 1)
inventory = inspect_inventory()
assert inventory[Prototype.SteamEngine] >= 1, f"Failed to craft steam engine. Inventory: {inventory[Prototype.SteamEngine]}"
print("Successfully crafted 1 steam engine!")
