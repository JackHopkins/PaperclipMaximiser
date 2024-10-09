from factorio_instance import *

# 1. Mine stone
stone_position = nearest(Resource.Stone)
move_to(stone_position)
harvest_resource(stone_position, quantity=5)
# Assert that we have enough stone
stone_count = inspect_inventory()[Resource.Stone]
assert stone_count >= 5, f"Not enough stone mined. Expected at least 5, but got {stone_count}"

# 2. Craft stone furnace
craft_item(Prototype.StoneFurnace, quantity=1)
# Assert that we have crafted the stone furnace
furnace_count = inspect_inventory()[Prototype.StoneFurnace]
assert furnace_count >= 1, f"Failed to craft stone furnace. Expected at least 1, but got {furnace_count}"

# 3. Mine coal
coal_position = nearest(Resource.Coal)
move_to(coal_position)
harvest_resource(coal_position, quantity=1)
# Assert that we have enough coal
coal_count = inspect_inventory()[Resource.Coal]
assert coal_count >= 1, f"Not enough coal mined. Expected at least 1, but got {coal_count}"

# 4. Mine iron ore
iron_ore_position = nearest(Resource.IronOre)
move_to(iron_ore_position)
harvest_resource(iron_ore_position, quantity=1)
# Assert that we have enough iron ore
iron_ore_count = inspect_inventory()[Resource.IronOre]
assert iron_ore_count >= 1, f"Not enough iron ore mined. Expected at least 1, but got {iron_ore_count}"

# 5. Place and set up the stone furnace
furnace_position = Position(x=iron_ore_position.x, y=iron_ore_position.y - 1)  # Place furnace above iron ore
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
# Assert that the furnace was placed successfully
assert stone_furnace is not None, "Failed to place stone furnace"

# 6. Insert fuel and iron ore into the furnace
insert_item(Prototype.Coal, stone_furnace, quantity=1)
insert_item(Prototype.IronOre, stone_furnace, quantity=1)

# Wait for smelting to complete
sleep(10)
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, stone_furnace.position, 1)
    plates_extracted = inspect_inventory()[Prototype.IronPlate]
    if plates_extracted >= 1:
        break
    sleep(10)  # Wait a bit more if not all resources are ready

# Assert that we have crafted the iron plate
iron_plate_count = inspect_inventory()[Prototype.IronPlate]
assert iron_plate_count >= 1, f"Failed to craft iron plate. Expected at least 1, but got {iron_plate_count}"
print("Successfully crafted 1 iron plate from scratch!")
