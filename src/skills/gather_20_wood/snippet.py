
# Find the nearest wood resource
wood_position = nearest(Resource.Wood)
print(f"Nearest wood position: {wood_position}")

# harvest 20 wood
harvested = harvest_resource(wood_position, quantity=20)
    
# Check inventory to confirm wood count
inventory = inspect_inventory()
actual_wood_count = inventory.get(Prototype.Wood, 0)
print(f"Wood in inventory: {actual_wood_count}")
# Assert that we have at least 20 wood
assert actual_wood_count >= 20, f"Failed to collect 20 wood. Only collected {actual_wood_count}"
print("Successfully collected at least 20 wood!")
