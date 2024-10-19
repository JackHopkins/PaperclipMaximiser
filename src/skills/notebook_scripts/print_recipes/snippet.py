"""
[PLANNING]
We first need to print the recipes of the items we need to craft, i.e 
the burner mining drill, the burner inserter, the transport belt and the wooden chest
[PLANNING]
"""

# first get the recipe for the burner mining drill
drill_recipe = get_recipe(Prototype.BurnerMiningDrill)
print(f"Drill recipe: {drill_recipe}")

# get the recipe for the burner inserter
inserter_recipe = get_recipe(Prototype.BurnerInserter)
print(f"Inserter recipe: {inserter_recipe}")

# get the recipe for the transport belt
belt_recipe = get_recipe(Prototype.TransportBelt)
print(f"Belt recipe: {belt_recipe}")

# get the recipe for the wooden chest
chest_recipe = get_recipe(Prototype.WoodenChest)
print(f"Chest recipe: {chest_recipe}")
