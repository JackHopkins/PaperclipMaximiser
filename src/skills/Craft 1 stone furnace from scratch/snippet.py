
from factorio_instance import *

# 1. Locate the nearest stone resource
stone_position = nearest(Resource.Stone)

# 2. Move to the stone resource
move_to(stone_position)

# 3. Harvest 5 stone
harvested = harvest_resource(stone_position, quantity=5)
if harvested < 5:
    print("Not enough stone harvested. Trying to harvest more.")
    while harvested < 5:
        harvested += harvest_resource(stone_position, quantity=5-harvested)

# 4. Verify that we have enough stone in our inventory
inventory = inspect_inventory()
stone_count = inventory.get(Resource.Stone, 0)
assert stone_count >= 5, f"Error: Not enough stone in inventory. Expected at least 5, but got {stone_count}."

# 5. Craft the stone furnace
crafted = craft_item(Prototype.StoneFurnace, quantity=1)
assert crafted == 1, f"Error: Failed to craft stone furnace. Expected to craft 1, but crafted {crafted}."

# 6. Verify that the stone furnace was crafted successfully
inventory = inspect_inventory()
furnace_count = inventory.get(Prototype.StoneFurnace, 0)
assert furnace_count >= 1, f"Error: Stone furnace not found in inventory after crafting. Expected at least 1, but got {furnace_count}."

print("Successfully crafted 1 stone furnace!")
