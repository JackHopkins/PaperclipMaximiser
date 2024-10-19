"""
[PLANNING]
We have harvested resources and smelt the iron ore into iron plates
We also have the stone in inventory for the stone furnace
Now we need to craft the burner mining drill and burner inserter
[PLANNING]
"""

# first craft a the burner mining drill
craft_item(Prototype.BurnerMiningDrill, 1)
# check the inventory after crafting the drill
drill_count = inspect_inventory()[Prototype.BurnerMiningDrill]
assert drill_count >= 1, f"Failed to craft burner mining drill. Expected 1, but got {drill_count}"
print("Crafted a burner mining drill")

# craft the burner inserter
craft_item(Prototype.BurnerInserter, 1)
# check the inventory after crafting the inserter
inserter_count = inspect_inventory()[Prototype.BurnerInserter]
assert inserter_count >= 1, f"Failed to craft burner inserter. Expected 1, but got {inserter_count}"
print("Crafted a burner inserter")