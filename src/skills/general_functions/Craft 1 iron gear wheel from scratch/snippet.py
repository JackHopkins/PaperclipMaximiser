from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)
# Assert that we have enough stone
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Not enough stone. Expected at least 5, but got {stone_count}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)
# Assert that we have crafted the stone furnace
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Failed to craft stone furnace. Expected at least 1, but got {furnace_count}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=10)
# Assert that we have enough coal
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 10, f"Not enough coal. Expected at least 10, but got {coal_count}"

# 4. Find and move to iron ore
iron_ore_position = nearest(Resource.IronOre)
move_to(iron_ore_position)

# 5. Place stone furnace next to iron ore
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=iron_ore_position, direction=Direction.UP, spacing=1)
# Assert that the furnace was placed successfully
assert furnace is not None, "Failed to place stone furnace"

# 6. Mine iron ore
harvest_resource(iron_ore_position, quantity=4)
# Assert that we have enough iron ore
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 4, f"Not enough iron ore. Expected at least 4, but got {iron_ore_count}"

# 7. Insert coal and iron into furnace
insert_item(Prototype.Coal, furnace, quantity=5)
insert_item(Prototype.IronOre, furnace, quantity=4)

# Wait for smelting to complete
sleep(10)
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, 2)
    plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if plates_extracted >= 2:
        break
    sleep(10)  # Wait a bit more if not all resources are ready

# Assert that we have enough iron plates
iron_plate_count = inspect_inventory()[Prototype.IronPlate]
assert iron_plate_count >= 2, f"Not enough iron plates. Expected at least 2, but got {iron_plate_count}"

# 11. Craft iron gear wheel
craft_item(Prototype.IronGearWheel, quantity=1)
#Verify the iron gear wheel is in the inventory
inventory = inspect_inventory()
iron_gear_wheel_count = inventory.get(Prototype.IronGearWheel, 0)
assert iron_gear_wheel_count >= 1, f"Failed to craft iron gear wheel. Expected at least 1, but got {iron_gear_wheel_count}"
print("Successfully crafted 1 iron gear wheel!")
