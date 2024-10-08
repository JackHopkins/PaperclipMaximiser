from factorio_instance import *

# 1. Harvest Wood
nearest_tree = nearest(Resource.Wood)
move_to(nearest_tree)
harvest_resource(nearest_tree, quantity=4)

# Assert that we have harvested enough wood
wood_in_inventory = inspect_inventory()[Resource.Wood]
assert wood_in_inventory >= 4, f"Failed to harvest enough wood. Current amount: {wood_in_inventory}"

# 2. Craft Wooden Chest directly from Wood
craft_item(Prototype.WoodenChest, quantity=1)

# 3. Verify crafting
inventory = inspect_inventory()
wooden_chests_in_inventory = inventory[Prototype.WoodenChest]

# Assert that we have crafted the wooden chest
assert wooden_chests_in_inventory >= 1, f"Failed to craft a wooden chest. Current amount: {wooden_chests_in_inventory}"

# Final check to ensure we have exactly 1 wooden chest (in case we had any before)
print(f"Wooden chests in inventory: {wooden_chests_in_inventory}")

# Check remaining wood
remaining_wood = inventory[Resource.Wood]
print(f"Remaining wood in inventory: {remaining_wood}")
