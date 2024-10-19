from factorio_instance import *


def craft_one_furnace():
    """
    Objective: We need to craft one stone furnace.
    Mining setup: There are no entities on the map
    Inventory: We start with an empty inventory
    """
    # [PLANNING]
    # To craft a stone furnace, we need:
    # 1. Mine 5 stone
    # 2. Craft the stone furnace
    # 3. Verify that we have a stone furnace in our inventory
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine stone
    stone_position = nearest(Resource.Stone)
    print(f"Moving to stone patch at {stone_position}")
    move_to(stone_position)
    
    harvest_resource(stone_position, 5)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 2: Craft the stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    
    # Step 3: Verify that we have a stone furnace in our inventory
    final_inventory = inspect_inventory()
    furnace_count = final_inventory.get(Prototype.StoneFurnace, 0)
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    
    print(f"Final inventory: {final_inventory}")
    print("Successfully crafted one stone furnace!")



###FUNC SEP

craft_one_furnace()