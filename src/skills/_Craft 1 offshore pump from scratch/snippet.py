from factorio_instance import *

# Step 1: Mine raw resources
# Mine enough iron ore for the plates, circuits, pipes and gear wheels
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 5)
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 5, f"Failed to mine enough iron ore. Expected 5, but got {iron_ore_count}"

# Mine enough stone for 1 furnace
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, 5)
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"

# Mine enough coal for the furnaces
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, 5)
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"

# Mine enough copper ore for the circuits
copper_position = nearest(Resource.CopperOre)
move_to(copper_position)
harvest_resource(copper_position, 5)
copper_count = inspect_inventory()[Resource.CopperOre]
assert copper_count >= 5, f"Failed to mine enough copper. Expected 5, but got {copper_count}"

# Step 2: Craft first stone furnace
craft_item(Prototype.StoneFurnace, 1)
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# Step 3: Smelt iron plates
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = copper_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 5)
insert_item(Prototype.IronOre, furnace, 5)

# Wait for smelting to complete
sleep(10)  # Increased sleep time

# Extract iron plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 5)
    iron_plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_extracted >= 5:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 5 iron plates
iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_in_inventory >= 5, f"Failed to smelt enough iron plates. Expected 5, but got {iron_in_inventory}"

# Step 4: Smelt copper plates
insert_item(Prototype.CopperOre, furnace, 5)

# Wait for smelting to complete
sleep(10)  # Increased sleep time

# Extract copper plates with a more robust approach
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.CopperPlate, furnace.position, 5)
    copper_plates_extracted = inspect_inventory()[Prototype.CopperPlate]
    if copper_plates_extracted >= 5:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# Check if we have 5 copper plates
copper_in_inventory = inspect_inventory()[Prototype.CopperPlate]
assert copper_in_inventory >= 5, f"Failed to smelt enough copper plates. Expected 5, but got {copper_in_inventory}"

# 5. Craft 1 iron gear wheels
craft_item(Prototype.IronGearWheel, 1)  
iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]  
assert iron_gear_count >= 1, f"Failed to craft 1 iron gears. Current count: {iron_gear_count}"

# 6. Craft 2 electronic circuits
craft_item(Prototype.ElectronicCircuit, 2)
circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
assert circuit_count >= 2, f"Failed to craft 2 circuits. Current count: {circuit_count}"

# 7. Craft Pipe
craft_item(Prototype.Pipe, 1)
pipe_in_inventory = inspect_inventory()[Prototype.Pipe]
assert pipe_in_inventory >= 1, f"Pipe not crafted. Expected 1, got {pipe_in_inventory}"

# 8. Craft Offshore Pump
craft_item(Prototype.OffshorePump, 1)
offshore_pump_in_inventory = inspect_inventory()[Prototype.OffshorePump]
assert offshore_pump_in_inventory >= 1, f"Offshore pump not crafted. Expected 1, got {offshore_pump_in_inventory}"

print("Successfully crafted 1 offshore pump from scratch!")
