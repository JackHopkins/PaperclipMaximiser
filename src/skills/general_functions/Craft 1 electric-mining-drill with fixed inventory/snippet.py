from factorio_instance import *

# Check initial inventory
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 20, f"Not enough iron plates in inventory. Expected 20, got {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.CopperPlate] >= 20, f"Not enough copper plates in inventory. Expected 20, got {initial_inventory[Prototype.CopperPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected 20, got {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected 3, got {initial_inventory[Prototype.StoneFurnace]}"

# Step 1 - Mine 10 iron ores to make sure we have enough iron for all required iron plates, circuits and gear wheels
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 10)
iron_count = inspect_inventory()[Resource.IronOre] 
# Check if we have 10 iron ores
assert iron_count >= 10, f"Failed to mine enough iron ores. Expected 10, but got {iron_count}"

# Step 2: Smelt iron plates using furnace in the inventory
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = iron_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 10)
insert_item(Prototype.IronOre, furnace, 10)

# Wait for smelting to complete
sleep(10)  # Increased sleep time
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 10)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 30:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 30 iron plates
iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_in_inventory >= 30, f"Failed to smelt enough iron plates. Expected 30, but got {iron_in_inventory}"

# Step 3: Craft 3 iron gear wheels
craft_item(Prototype.IronGearWheel, 3)  
iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]  
assert iron_gear_count >= 3, f"Failed to craft 3 iron gears. Current count: {iron_gear_count}"

# Step 4: Craft 3 electronic circuits
craft_item(Prototype.ElectronicCircuit, 3)
circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
assert circuit_count >= 3, f"Failed to craft 3 circuits. Current count: {circuit_count}"

# Step 5: Craft electric mining drill
craft_item(Prototype.ElectricMiningDrill, 1)
drill_count = inspect_inventory()[Prototype.ElectricMiningDrill]
assert drill_count >= 1, f"Failed to craft electric mining drill. Current count: {drill_count}"
print("Successfully crafted 1 electric mining drill!")