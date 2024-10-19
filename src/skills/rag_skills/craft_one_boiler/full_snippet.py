from factorio_instance import *

def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores. The furnace has been fueled with coal
    Inventory: We have enough iron ore in the inventory to smelt the iron plates
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore in the inventory
    # 2. Insert the iron ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the iron plates from the furnace
    # 5. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"

    # Insert the iron ore into the furnace
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_iron_ore} iron ore into the furnace")

    # Get the initial number of iron plates in the inventory
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]

    # Wait for smelting to complete (1 second per ore)
    smelting_time = input_iron_ore * 1  # 1 second per ore
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract the iron plates from the furnace
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        
        # Check how many plates we have in our inventory
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_smelted = current_iron_plates - initial_iron_plates
        
        if iron_plates_smelted >= input_iron_ore:
            print(f"Successfully extracted {iron_plates_smelted} iron plates")
            break
        
        if attempt < max_attempts - 1:
            print(f"Extraction incomplete. Waiting 5 seconds before next attempt.")
            sleep(5)
    
    # Verify that we have the correct number of iron plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    iron_plates_smelted = final_iron_plates - initial_iron_plates
    assert iron_plates_smelted >= input_iron_ore, f"Failed to smelt enough iron plates. Expected: {input_iron_ore}, Smelted: {iron_plates_smelted}"

    print(f"Final inventory: {inspect_inventory()}")
    print(f"Successfully smelted {iron_plates_smelted} iron plates")

###FUNC SEP

def craft_one_boiler():
    """
    Objective: We need to craft one boiler from scratch.
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for a boiler
    # 2. Mine the necessary resources (iron ore and stone) and coal for fuel
    # We need to mine everything from scratch as we have no resources in the inventory
    # 3. Craft a stone furnace to smelt iron plates
    # 4. Smelt iron ore into iron plates
    # 5. Craft the boiler
    # 6. Verify that we have a boiler in our inventory
    # [END OF PLANNING]

    # Step 1: Check the recipe for a boiler
    boiler_recipe = get_prototype_recipe(Prototype.Boiler)
    print(f"Boiler recipe: {boiler_recipe}")

    # Step 2: Mine necessary resources
    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 20)  # We need extra for the furnace
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 20, f"Failed to mine enough iron ore. Expected 20, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # We need 5 for the furnace and 5 for the boiler
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 10, f"Failed to mine enough stone. Expected 10, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # Mine coal for fuel
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 5)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    print(f"Current inventory: {inspect_inventory()}")

    # Step 3: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 4: Smelt iron ore into iron plates
    furnace_position = Position(x=0, y=0)
    move_to(furnace_position)  # Move to the position where we want to place the furnace
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"

    # add coal to the furnace
    # We need to add coal to the furnace to smelt the iron ore
    insert_item(Prototype.Coal, furnace, 5)
    print(f"Inserted 5 coal into the furnace")
    
    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. The furnace has been fueled with coal
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=20, furnace=furnace)

    iron_plate_count = inspect_inventory()[Prototype.IronPlate]
    assert iron_plate_count >= 20, f"Failed to smelt enough iron plates. Expected 20, but got {iron_plate_count}"
    print(f"Smelted {iron_plate_count} iron plates")

    print(f"Current inventory: {inspect_inventory()}")

    # Step 5: Craft the boiler
    craft_item(Prototype.Boiler, 1)

    # Step 6: Verify that we have a boiler in our inventory
    boiler_count = inspect_inventory()[Prototype.Boiler]
    assert boiler_count == 1, f"Failed to craft boiler. Expected 1, but got {boiler_count}"
    print("Successfully crafted 1 boiler!")
    print(f"Final inventory: {inspect_inventory()}")

    return True
###FUNC SEP
craft_one_boiler()
