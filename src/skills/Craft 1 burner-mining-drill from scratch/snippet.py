from factorio_instance import *

# Step 1: Mine raw resources
# Mine enough iron ore for the plates and gear wheels
iron_position = nearest(Resource.IronOre)
move_to(iron_position)
harvest_resource(iron_position, 20)
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 20, f"Failed to mine enough iron ore. Expected 20, but got {iron_ore_count}"

# Mine enough stone for 2 furnaces
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, 10)
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 10, f"Failed to mine enough stone. Expected 10, but got {stone_count}"

# Mine enough coal for the furnaces
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, 5)
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"

# Step 2: Craft first stone furnace
craft_item(Prototype.StoneFurnace, 1)
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# Step 3: Smelt iron plates
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = coal_position, direction = Direction.UP, spacing = 1)
insert_item(Prototype.Coal, furnace, 5)
insert_item(Prototype.IronOre, furnace, 20)

# Wait for smelting to complete
sleep(20)  # Increased sleep time
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

# Step 4: Craft iron gear wheels
craft_item(Prototype.IronGearWheel, 3)
gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
assert gear_wheel_count == 3, f"Failed to craft enough iron gear wheels. Expected 3, but got {gear_wheel_count}"

# Step 5: Craft burner-mining-drill
craft_item(Prototype.BurnerMiningDrill, 1)
drill_count = inspect_inventory()[Prototype.BurnerMiningDrill]
assert drill_count == 1, f"Failed to craft burner-mining-drill. Expected 1, but got {drill_count}"
print("Burner-mining-drill crafted successfully!")