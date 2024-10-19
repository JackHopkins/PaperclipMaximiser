from factorio_instance import *


def smelt_iron_with_furnace(input_coal: int, input_iron_ore: int, furnace: Entity, output_iron_plate: int) -> None:
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores. We need to fuel the furnace with coal
    Inventory: We have enough iron ore and coal in the inventory to smelt the iron plates
    :param input_coal (int): The number of coal to insert into the furnace
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :param output_iron_plate (int): The number of iron plates to extract from the furnace
    :return: None as the iron plates will be in inventory
    """
    
    # [PLANNING]
    # 1. Check inventory for required resources
    # 2. Move to the furnace
    # 3. Insert coal and iron ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract iron plates from the furnace
    # 6. Verify the result
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check inventory for required resources
    inventory = inspect_inventory()
    assert inventory[Prototype.Coal] >= input_coal, f"Not enough coal. Required: {input_coal}, Available: {inventory[Prototype.Coal]}"
    assert inventory[Prototype.IronOre] >= input_iron_ore, f"Not enough iron ore. Required: {input_iron_ore}, Available: {inventory[Prototype.IronOre]}"

    # Move to the furnace
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (assuming 3.5 seconds per iron plate)
    smelting_time = output_iron_plate * 3.5
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, output_iron_plate)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        
        if iron_plates_extracted >= output_iron_plate:
            print(f"Successfully extracted {iron_plates_extracted} iron plates")
            break
        elif attempt < max_attempts - 1:
            print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates. Waiting for more...")
            sleep(5)
    else:
        print(f"Warning: Could only extract {iron_plates_extracted} iron plates after {max_attempts} attempts")

    # Verify the result
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.IronPlate] >= initial_iron_plates + output_iron_plate, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + output_iron_plate}, but got {final_inventory[Prototype.IronPlate]}"

    print(f"Final inventory: {final_inventory}")
    print("Successfully completed iron smelting")


###FUNC SEP


def craft_one_steam_engine():
    """
    Objective: We need to craft one steam engine.
    Mining setup: There are no entities on the map
    Inventory: We start with an empty inventory
    """
    # [PLANNING]
    # 1. Mine raw resources: iron ore, stone, and coal
    # We need to mine everything from scratch as we have no resources in the inventory
    # 2. Craft a stone furnace
    # 3. Smelt iron plates
    # 4. Craft intermediate components: iron gear wheels and pipes
    # 5. Craft the steam engine
    # 6. Verify the result
    # [END OF PLANNING]

    print("Starting to craft one steam engine")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine raw resources
    resources_to_mine = [
        (Resource.IronOre, 31),
        (Resource.Stone, 10),
        (Resource.Coal, 20)
    ]

    for resource, amount in resources_to_mine:
        resource_position = nearest(resource)
        move_to(resource_position)
        harvest_resource(resource_position, amount)
        current_amount = inspect_inventory()[resource]
        assert current_amount >= amount, f"Failed to mine enough {resource}. Expected {amount}, but got {current_amount}"
        print(f"Mined {current_amount} {resource}")

    print(f"Current inventory after mining: {inspect_inventory()}")

    # Step 2: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 3: Smelt iron plates
    current_position = nearest(Resource.Coal)
    move_to(current_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, current_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # """[SYNTHESISED]
    # Name: smelt_iron_with_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. We need to fuel the furnace with coal
    # Inventory: We have enough iron ore and coal in the inventory to smelt the iron plates
    # :param input_coal (int): The number of coal to insert into the furnace
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :param output_iron_plate (int): The number of iron plates to extract from the furnace
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_furnace(input_coal=20, input_iron_ore=31, furnace=furnace, output_iron_plate=31)

    iron_plate_count = inspect_inventory()[Prototype.IronPlate]
    assert iron_plate_count >= 31, f"Failed to smelt enough iron plates. Expected 31, but got {iron_plate_count}"
    print(f"Smelted {iron_plate_count} iron plates")
    print(f"Current inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft intermediate components
    craft_item(Prototype.IronGearWheel, 8)
    gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheel_count == 8, f"Failed to craft enough iron gear wheels. Expected 8, but got {gear_wheel_count}"
    print(f"Crafted {gear_wheel_count} iron gear wheels")

    craft_item(Prototype.Pipe, 5)
    pipe_count = inspect_inventory()[Prototype.Pipe]
    assert pipe_count == 5, f"Failed to craft enough pipes. Expected 5, but got {pipe_count}"
    print(f"Crafted {pipe_count} pipes")

    print(f"Current inventory after crafting components: {inspect_inventory()}")

    # Step 5: Craft the steam engine
    craft_item(Prototype.SteamEngine, 1)

    # Step 6: Verify the result
    steam_engine_count = inspect_inventory()[Prototype.SteamEngine]
    assert steam_engine_count == 1, f"Failed to craft steam engine. Expected 1, but got {steam_engine_count}"
    print("Successfully crafted 1 steam engine!")
    print(f"Final inventory: {inspect_inventory()}")



###FUNC SEP

craft_one_steam_engine()