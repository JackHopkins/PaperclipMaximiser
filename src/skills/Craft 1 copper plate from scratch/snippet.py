
from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)

# Assert that we have enough stone
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)

# Assert that we have crafted the stone furnace
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=1)

# Assert that we have enough coal
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 1, f"Failed to mine enough coal. Expected 1, but got {coal_count}"

# 4. Mine copper ore
copper_position = nearest(Resource.CopperOre)
move_to(copper_position)
harvest_resource(copper_position, quantity=1)

# Assert that we have enough copper ore
copper_ore_count = inspect_inventory()[Resource.CopperOre]
assert copper_ore_count >= 1, f"Failed to mine enough copper ore. Expected 1, but got {copper_ore_count}"

# 5. Place stone furnace
furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=copper_position, direction=Direction.UP, spacing=1)

# Assert that the furnace was placed successfully
assert furnace is not None, "Failed to place stone furnace"

# 6. Insert fuel and copper ore into the furnace
insert_item(Prototype.Coal, furnace, quantity=1)
insert_item(Prototype.CopperOre, furnace, quantity=1)

# 7. Wait for smelting
sleep(10)  # Wait for 10 seconds to ensure smelting is complete

# 8. Extract copper plate
extract_item(Prototype.CopperPlate, furnace.position, quantity=1)

# Assert that we have crafted the copper plate
copper_plate_count = inspect_inventory()[Prototype.CopperPlate]
assert copper_plate_count >= 1, f"Failed to craft copper plate. Expected 1, but got {copper_plate_count}"

print("Successfully crafted 1 copper plate from scratch!")
