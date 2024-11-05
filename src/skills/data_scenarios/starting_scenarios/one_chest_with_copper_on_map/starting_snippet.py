from factorio_instance import *

furnace_pos = Position(x = 8, y = 1)
move_to(furnace_pos)
stone_furnace = place_entity(Prototype.WoodenChest, Direction.UP, furnace_pos)
updated_chest = insert_item(Prototype.CopperPlate, stone_furnace, 20)