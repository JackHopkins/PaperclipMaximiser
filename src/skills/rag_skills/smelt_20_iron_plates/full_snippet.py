from factorio_instance import *


def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores. The furnace has been fueled
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

    print(f"Starting to smelt {input_iron_ore} iron ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"

    # Insert the iron ore into the furnace
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_iron_ore} iron ore into the furnace")
    print(f"Inventory after insertion: {inspect_inventory()}")

    # Wait for the smelting process to complete
    # Smelting time is 3.5 seconds per iron plate
    smelting_time = input_iron_ore * 3.5
    print(f"Waiting for {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract the iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        if iron_plates_extracted >= input_iron_ore:
            break
        print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates. Waiting for more...")
        sleep(5)

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")
    print(f"Final inventory: {inspect_inventory()}")

    # Verify that we have the correct number of iron plates in our inventory
    assert iron_plates_extracted >= input_iron_ore, f"Failed to extract enough iron plates. Expected: {input_iron_ore}, Extracted: {iron_plates_extracted}"

    print(f"Successfully smelted {input_iron_ore} iron ore into {iron_plates_extracted} iron plates")


###FUNC SEP


def smelt_20_iron_plates():
    """
    Objective: Smelt 20 iron plates. The final success should be checked by looking if the iron plates are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # We need to mine everything from scratch as we don' have any resources
    # 1. Mine iron ore (we'll mine 30 to account for inefficiencies)
    # 2. Mine coal for fuel (we'll mine 15 to ensure we have enough)
    # 3. Craft a stone furnace
    # 4. Place the stone furnace
    # 5. Fuel the furnace with coal
    # 6. Smelt the iron ore into iron plates
    # 7. Check if we have 20 iron plates in our inventory
    # [END OF PLANNING]

    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 30)
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 30, f"Failed to mine enough iron ore. Expected 30, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 15)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 15, f"Failed to mine enough coal. Expected 15, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 3: Mine stone and craft a stone furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 5)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 4: Place the stone furnace
    furnace_position = Position(x=iron_position.x, y=iron_position.y + 2)
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 5: Fuel the furnace with coal
    insert_item(Prototype.Coal, furnace, 15)
    print("Inserted 15 coal into the furnace")

    # Step 6: Smelt the iron ore into iron plates
    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. The furnace has been fueled
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=30, furnace=furnace)

    # Step 7: Check if we have 20 iron plates in our inventory
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 20, f"Failed to smelt 20 iron plates. Current count: {iron_plates}"
    
    print(f"Successfully smelted {iron_plates} iron plates!")
    print(f"Final inventory: {inspect_inventory()}")



###FUNC SEP

smelt_20_iron_plates()