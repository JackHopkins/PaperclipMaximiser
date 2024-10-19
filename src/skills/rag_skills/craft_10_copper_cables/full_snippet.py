from factorio_instance import *


def smelt_copper_ore(input_copper_ore: int) -> None:
    """
    Objective: Smelt copper ore into copper plates
    Mining setup: No existing furnace on the map
    Inventory: We have copper ore, enough stone for a furnace and coal in the inventory
    :param input_copper_ore (int): The number of copper ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore and coal in the inventory
    # 2. Craft and place a stone furnace
    # 3. Insert coal and copper ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract copper plates from the furnace
    # 6. Verify that we have the correct number of copper plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Check if we have enough copper ore and coal
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= input_copper_ore, f"Not enough copper ore. Required: {input_copper_ore}, Available: {inventory[Prototype.CopperOre]}"
    assert inventory[Prototype.Coal] >= 5, f"Not enough coal. Required: 5, Available: {inventory[Prototype.Coal]}"

    # Step 2: Craft and place a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    # place furnace near the copper ore
    furnace_position = nearest(Resource.CopperOre)
    # move to the furnace position
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 3: Insert coal and copper ore into the furnace
    insert_item(Prototype.Coal, furnace, 5)
    insert_item(Prototype.CopperOre, furnace, input_copper_ore)
    print(f"Inserted 5 coal and {input_copper_ore} copper ore into the furnace")

    # Step 4: Wait for smelting to complete (1 second per ore)
    sleep(input_copper_ore)

    # Step 5: Extract copper plates from the furnace
    initial_copper_plates = inventory[Prototype.CopperPlate]
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, input_copper_ore)
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_extracted = current_copper_plates - initial_copper_plates
        if copper_plates_extracted >= input_copper_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_extracted} copper plates from the furnace")

    # Step 6: Verify that we have the correct number of copper plates
    final_inventory = inspect_inventory()
    final_copper_plates = final_inventory[Prototype.CopperPlate]
    assert final_copper_plates >= initial_copper_plates + input_copper_ore, f"Failed to smelt enough copper plates. Expected at least {initial_copper_plates + input_copper_ore}, but got {final_copper_plates}"

    print(f"Final inventory: {final_inventory}")
    print(f"Successfully smelted {input_copper_ore} copper ore into copper plates!")


###FUNC SEP


def craft_10_copper_cables():
    """
    Objective: Craft 10 copper cables. The final success should be checked by looking if 10 copper cables are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for copper cables
    # 2. Get copper, coal and stone for smelting and crafting a furnace
    # We need to mine everything from scratch as we have no resources in the inventory
    # 3. Smelt copper ore into copper plates
    # 4. Craft copper cables
    # 5. Verify the final result
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Check the recipe for copper cables
    copper_cable_recipe = get_prototype_recipe(Prototype.CopperCable)
    print(f"Copper cable recipe: {copper_cable_recipe}")

    # Step 2: Mine copper ore
    # We need 5 copper plates to craft 10 copper cables, so we'll mine 6 copper ore to be safe
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    harvest_resource(copper_position, 6)
    copper_ore_count = inspect_inventory()[Resource.CopperOre]
    assert copper_ore_count >= 6, f"Failed to mine enough copper ore. Expected 6, but got {copper_ore_count}"
    print(f"Mined {copper_ore_count} copper ore")

    # We also need coal to smelt the copper ore
    # Having 5 coal should be enough
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 5)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Finally we need stone to craft a furnace
    # We need 5 stone to craft a furnace, so we'll mine 7 stone to be safe
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 7)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")
    

    # Step 3: Smelt copper ore into copper plates
    # """[SYNTHESISED]
    # Name: smelt_copper_ore
    # Objective: Smelt copper ore into copper plates
    # Mining setup: No existing furnace on the map
    # Inventory: We have copper ore, enough stone for a furnace and coal in the inventory
    # :param input_copper_ore (int): The number of copper ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_copper_ore(input_copper_ore=6)
    
    copper_plate_count = inspect_inventory()[Prototype.CopperPlate]
    assert copper_plate_count >= 5, f"Failed to smelt enough copper plates. Expected 5, but got {copper_plate_count}"
    print(f"Smelted {copper_plate_count} copper plates")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 10)  # Crafts 10 copper cables (1 plate per 2 cables)
    
    # Step 5: Verify the final result
    copper_cable_count = inspect_inventory()[Prototype.CopperCable]
    assert copper_cable_count >= 10, f"Failed to craft 10 copper cables. Current count: {copper_cable_count}"
    print(f"Successfully crafted {copper_cable_count} copper cables!")

    # Print final inventory
    print(f"Final inventory: {inspect_inventory()}")

    print("Successfully completed the objective: Crafted 10 copper cables!")


###FUNC SEP

craft_10_copper_cables()