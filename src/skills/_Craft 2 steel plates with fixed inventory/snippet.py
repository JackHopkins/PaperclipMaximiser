from factorio_instance import *

# Check initial inventory
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 10, f"Not enough iron plates in inventory. Expected at least 10, but found {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, but found {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected at least 3, but found {initial_inventory[Prototype.StoneFurnace]}"

# 1. Place a stone furnace
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))
assert stone_furnace is not None, "Failed to place stone furnace"

# 2. Smelt steel plates using resources from inventory
insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.IronPlate, stone_furnace, 10)

# 3. Wait for the smelting process
sleep(10)
# Extract steel plates
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.SteelPlate, stone_furnace.position, 10)
    steel_plates_extracted = inspect_inventory()[Prototype.SteelPlate]
    if steel_plates_extracted >= 2:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# 4. Confirm the steel plates in inventory
steel_plates = inspect_inventory()[Prototype.SteelPlate]
assert steel_plates >= 2, f"Failed to craft 2 steel plates. Only found {steel_plates} in inventory"

print(f"Successfully crafted {steel_plates} steel plates")
