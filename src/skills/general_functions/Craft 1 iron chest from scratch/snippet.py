from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)
stone_in_inventory = inspect_inventory()[Resource.Stone]
assert stone_in_inventory >= 5, f"Failed to mine enough stone. Current amount: {stone_in_inventory}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)
furnace_in_inventory = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_in_inventory >= 1, f"Failed to craft stone furnace. Current amount: {furnace_in_inventory}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=10)
coal_in_inventory = inspect_inventory()[Resource.Coal]
assert coal_in_inventory >= 10, f"Failed to mine enough coal. Current amount: {coal_in_inventory}"

# 4. Mine iron ore
iron_ore_position = nearest(Resource.IronOre)
move_to(iron_ore_position)
harvest_resource(iron_ore_position, quantity=8)
iron_ore_in_inventory = inspect_inventory()[Resource.IronOre]
assert iron_ore_in_inventory >= 8, f"Failed to mine enough iron ore. Current amount: {iron_ore_in_inventory}"

# 5. Place stone furnace
furnace_position = Position(x=iron_ore_position.x, y=iron_ore_position.y - 2)
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
assert stone_furnace is not None, "Failed to place stone furnace"

# 6. Smelt iron plates
insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.IronOre, stone_furnace, 8)

# Wait for smelting to complete
sleep(10)
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, stone_furnace.position, 8)
    plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if plates_extracted >= 8:
        break
    sleep(10)  # Wait a bit more if not all resources are ready

# Final check for iron plates
iron_plates_in_inventory = inspect_inventory()[Prototype.IronPlate]
assert iron_plates_in_inventory >= 8, f"Failed to smelt enough iron plates after {total_wait_time} seconds. Current amount: {iron_plates_in_inventory}"

# 8. Craft iron chest
craft_item(Prototype.IronChest, quantity=1)

# 9. Verify crafting
inventory = inspect_inventory()
iron_chests_in_inventory = inventory.get(Prototype.IronChest, 0)
assert iron_chests_in_inventory >= 1, f"Failed to craft iron chest. Current amount: {iron_chests_in_inventory}"
print("Successfully crafted 1 iron chest!")
