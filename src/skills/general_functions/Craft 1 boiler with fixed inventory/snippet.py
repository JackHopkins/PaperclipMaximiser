from factorio_instance import *

# Check initial inventory to ensure we have enough resources
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 20, f"Not enough iron plates in inventory. Expected at least 20, got {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, got {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.CopperPlate] >= 20, f"Not enough copper plates in inventory. Expected at least 20, got {initial_inventory[Prototype.CopperPlate]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected at least 3, got {initial_inventory[Prototype.StoneFurnace]}"

# Craft the boiler
craft_item(Prototype.Boiler, 1)
# Verify the boiler crafting
final_inventory = inspect_inventory()
assert final_inventory[Prototype.Boiler] >= 1, f"Failed to craft boiler. Expected at least 1, got {final_inventory[Prototype.Boiler]}"
print("Successfully crafted 1 boiler!")
