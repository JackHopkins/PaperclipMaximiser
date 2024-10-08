
from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)

stone_in_inventory = inspect_inventory()[Resource.Stone]
assert stone_in_inventory >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_in_inventory}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)

furnace_in_inventory = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_in_inventory >= 1, f"Failed to craft stone furnace. Expected at least 1, but got {furnace_in_inventory}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=2)

coal_in_inventory = inspect_inventory()[Resource.Coal]
assert coal_in_inventory >= 2, f"Failed to mine enough coal. Expected at least 2, but got {coal_in_inventory}"

# 4. Find and mine copper ore
copper_position = nearest(Resource.CopperOre)
move_to(copper_position)
harvest_resource(copper_position, quantity=1)

copper_ore_in_inventory = inspect_inventory()[Resource.CopperOre]
assert copper_ore_in_inventory >= 1, f"Failed to mine enough copper ore. Expected at least 1, but got {copper_ore_in_inventory}"

# 5. Place and fuel the stone furnace
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=copper_position, direction=Direction.UP, spacing=1)
insert_item(Prototype.Coal, furnace, quantity=2)

# 6. Smelt copper ore into copper plate
insert_item(Prototype.CopperOre, furnace, quantity=1)

# Wait for smelting to complete
sleep(10)

extract_item(Prototype.CopperPlate, furnace.position, quantity=1)

copper_plate_in_inventory = inspect_inventory()[Prototype.CopperPlate]
assert copper_plate_in_inventory >= 1, f"Failed to smelt copper plate. Expected at least 1, but got {copper_plate_in_inventory}"

# 7. Craft copper cable
craft_item(Prototype.CopperCable, quantity=1)

# 8. Confirm crafting
copper_cable_in_inventory = inspect_inventory()[Prototype.CopperCable]
assert copper_cable_in_inventory >= 1, f"Failed to craft copper cable. Expected at least 1, but got {copper_cable_in_inventory}"

print("Successfully crafted 1 copper cable from scratch!")
