
from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Failed to mine enough stone. Current count: {stone_count}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Failed to craft stone furnace. Current count: {furnace_count}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=5)
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 5, f"Failed to mine enough coal. Current count: {coal_count}"

# 4. Mine iron ore
iron_ore_position = nearest(Resource.IronOre)
move_to(iron_ore_position)
harvest_resource(iron_ore_position, quantity=3)
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 3, f"Failed to mine enough iron ore. Current count: {iron_ore_count}"

# 5. Place stone furnace
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=iron_ore_position, direction=Direction.UP, spacing=1)
assert furnace, "Failed to place stone furnace"

# 6. Smelt iron plates
insert_item(Prototype.Coal, furnace, quantity=1)
insert_item(Prototype.IronOre, furnace, quantity=3)

# Wait for smelting to complete
sleep(10)

# 7. Collect iron plates
extract_item(Prototype.IronPlate, furnace.position, quantity=3)
iron_plate_count = inspect_inventory()[Prototype.IronPlate]
assert iron_plate_count >= 3, f"Failed to smelt enough iron plates. Current count: {iron_plate_count}"

# 8. Craft iron gear wheel
craft_item(Prototype.IronGearWheel, quantity=1)
gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
assert gear_wheel_count >= 1, f"Failed to craft iron gear wheel. Current count: {gear_wheel_count}"

# 9. Craft transport belt
craft_item(Prototype.TransportBelt, quantity=1)
transport_belt_count = inspect_inventory()[Prototype.TransportBelt]
assert transport_belt_count >= 1, f"Failed to craft transport belt. Current count: {transport_belt_count}"

print("Successfully crafted 1 transport belt from scratch!")
