"""
[PLANNING]
We need to gather resources to craft the burner mining drill and the burner inserter
Burner mining drill requires 9 iron plates and one stone furnace in total
Burner inserter requires 3 iron plates in total
We also need to craft one additional stone furnace for smelting and coal for fuel
We will mine a bit more than needed to be sure we have enough
Therefore we need to mine atleast 15 iron ore, 10 stone and 5 coal
[PLANNING]
"""
# get the resources required
ore_required = [(Resource.IronOre, 15), (Resource.Stone, 10), (Resource.Coal, 5)]

# loop through the resources required
for resource, amount in ore_required:
    # get the nearest resource
    resource_position = nearest(resource)
    # move to the resource
    move_to(resource_position)
    # harvest the resource
    harvest_resource(resource_position, amount)
    # check if we have enough resources
    resource_count = inspect_inventory()[resource]
    assert resource_count >= amount, f"Failed to mine enough {resource}. Expected {amount}, but got {resource_count}"
    print(f"Mined {resource_count} {resource}")
    print(f"Current inventory: {inspect_inventory()}")

final_inventory = inspect_inventory()
print(f"Final inventory after harvesting: {final_inventory}")