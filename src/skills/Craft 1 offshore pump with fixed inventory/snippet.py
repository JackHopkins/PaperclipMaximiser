from factorio_instance import *

# Initial inventory check
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 20, f"Not enough iron plates in inventory. Expected 20, got {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected 20, got {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.CopperPlate] >= 20, f"Not enough copper plates in inventory. Expected 20, got {initial_inventory[Prototype.CopperPlate]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected 3, got {initial_inventory[Prototype.StoneFurnace]}"

# 1. Craft iron gear wheels
craft_item(Prototype.IronGearWheel, 2)
inventory_after_gears = inspect_inventory()
assert inventory_after_gears[Prototype.IronGearWheel] >= 2, f"Failed to craft 2 iron gear wheels. Current inventory: {inventory_after_gears[Prototype.IronGearWheel]}"
assert inventory_after_gears[Prototype.IronPlate] >= 16, f"Unexpected iron plate count after crafting gears. Expected at least 16, got {inventory_after_gears[Prototype.IronPlate]}"

# 2. Craft pipe
craft_item(Prototype.Pipe, 1)
inventory_after_pipe = inspect_inventory()
assert inventory_after_pipe[Prototype.Pipe] >= 1, f"Failed to craft 1 pipe. Current inventory: {inventory_after_pipe[Prototype.Pipe]}"
assert inventory_after_pipe[Prototype.IronPlate] >= 15, f"Unexpected iron plate count after crafting pipe. Expected at least 15, got {inventory_after_pipe[Prototype.IronPlate]}"

# 3. Craft offshore pump
craft_item(Prototype.OffshorePump, 1)
final_inventory = inspect_inventory()
assert final_inventory[Prototype.OffshorePump] >= 1, f"Failed to craft 1 offshore pump. Current inventory: {final_inventory[Prototype.OffshorePump]}"
print("Successfully crafted 1 offshore pump!")
