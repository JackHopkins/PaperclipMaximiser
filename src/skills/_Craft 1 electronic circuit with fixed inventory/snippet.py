from factorio_instance import *

# Initial inventory check
inventory = inspect_inventory()
assert inventory[Prototype.IronPlate] >= 20, f"Not enough iron plates in inventory. Required: 20, Available: {inventory[Prototype.IronPlate]}"
assert inventory[Prototype.CopperPlate] >= 20, f"Not enough copper plates in inventory. Required: 20, Available: {inventory[Prototype.CopperPlate]}"
assert inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Required: 20, Available: {inventory[Prototype.Coal]}"
assert inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Required: 3, Available: {inventory[Prototype.StoneFurnace]}"

# Step 1 - Craft 1 electronic circuits
craft_item(Prototype.ElectronicCircuit, 1)
circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
assert circuit_count >= 1, f"Failed to craft 1 circuit. Current count: {circuit_count}"


print("Successfully crafted 1 electronic circuit from scratch!")
