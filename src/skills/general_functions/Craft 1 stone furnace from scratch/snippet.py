
from factorio_instance import *

# 1. Locate the nearest stone resource
stone_position = nearest(Resource.Stone)
move_to(stone_position)

# 2. Harvest 5 stone
harvested = harvest_resource(stone_position, quantity=5)
# Verify that we have enough stone in our inventory
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Error: Not enough stone in inventory. Expected at least 5, but got {stone_count}."

# 3. Craft the stone furnace
crafted = craft_item(Prototype.StoneFurnace, quantity=1)
assert crafted == 1, f"Error: Failed to craft stone furnace. Expected to craft 1, but crafted {crafted}."

# 4. Verify that the stone furnace was crafted successfully
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Error: Stone furnace not found in inventory after crafting. Expected at least 1, but got {furnace_count}."
print("Successfully crafted 1 stone furnace!")
