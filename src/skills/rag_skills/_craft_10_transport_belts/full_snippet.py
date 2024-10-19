from factorio_instance import *


def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity, coal_needed: int) -> None:
    """
    Objective: We need to smelt iron ores into plates with a furnace.
    Mining setup: We have a furnace on the map that we can use to smelt iron ores. Mining setup: We have a furnace on the map that we can use to smelt iron ores. We also need to put coal into the furnace for fuel
    Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :param coal_needed (int): The number of coal needed for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Calculate the amount of coal needed (1 coal per 4 iron ore)
    # 3. Insert coal and iron ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract iron plates from the furnace
    # 6. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting to smelt {input_iron_ore} iron ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Need {input_iron_ore}, have {iron_ore_in_inventory}"

    # check if we have enough coal
    coal_in_inventory = inspect_inventory()[Prototype.Coal]
    assert coal_in_inventory >= coal_needed, f"Not enough coal in inventory. Need {coal_needed}, have {coal_in_inventory}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, coal_needed)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {coal_needed} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (smelting takes 1 seconds per iron plate)
    smelting_time = input_iron_ore *1
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Get the initial number of iron plates in the inventory
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]

    # Extract iron plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        if iron_plates_extracted >= input_iron_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")

    # Verify that we have the correct number of iron plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert final_iron_plates >= initial_iron_plates + input_iron_ore, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + input_iron_ore}, but got {final_iron_plates}"

    print(f"Successfully smelted {input_iron_ore} iron ore into iron plates")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP


def smelt_iron_plates(iron_ore_count: int, coal_needed: int) -> None:
    """
    Objective: Smelt iron ore into iron plates
    Mining setup: No existing setup
    Inventory: We have iron ore and coal in the inventory
    :param iron_ore_count (int): The number of iron ore to smelt
    :param coal_needed (int): The number of coal needed for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore in the inventory
    # 2. Find or create a stone furnace
    # 3. Ensure we have coal for the furnace
    # 4. Smelt the iron ore into iron plates
    # 5. Extract the iron plates from the furnace
    # 6. Verify that we have the correct number of iron plates
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= iron_ore_count, f"Not enough iron ore. Required: {iron_ore_count}, Available: {inventory[Prototype.IronOre]}"

    # Find or create a stone furnace
    furnaces = inspect_entities().get_entities(Prototype.StoneFurnace)
    furnace_pos = Position(x=0, y=0)
    if not furnaces:
        # Create a stone furnace if none exists
        stone_count = inventory[Prototype.Stone]
        if stone_count < 5:
            # Mine stone if we don't have enough
            stone_position = nearest(Resource.Stone)
            move_to(stone_position)
            harvest_resource(stone_position, 5 - stone_count)
        
        # Craft and place the stone furnace
        craft_item(Prototype.StoneFurnace, 1)
        # move to the furnace position
        move_to(furnace_pos)
        furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_pos)
    else:
        furnace = furnaces[0]

    # Move to the furnace
    move_to(furnace.position)

    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. We also need to put coal into the furnace for fuel
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=iron_ore_count,
                               furnace=furnace,
                               coal_needed=coal_needed)

    # Verify that we have the correct number of iron plates
    final_inventory = inspect_inventory()
    iron_plates = final_inventory[Prototype.IronPlate]
    assert iron_plates >= iron_ore_count, f"Failed to smelt enough iron plates. Expected at least {iron_ore_count}, but got {iron_plates}"

    print(f"Successfully smelted {iron_ore_count} iron ore into iron plates!")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP


def craft_10_transport_belts():
    """
    Objective: Craft 10 transport belts. The final success should be checked by looking if 10 transport belts are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for transport belts
    # 2. Calculate the required resources (iron plates and iron gear wheels). We do not have any resources in the inventory so we need to mine all of them
    # 3. Mine iron ore and coal required for smelting
    # 4. Craft iron plates
    # 5. Craft iron gear wheels
    # 6. Craft transport belts
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check the recipe for transport belts
    transport_belt_recipe = get_prototype_recipe(Prototype.TransportBelt)
    print(f"Transport belt recipe: {transport_belt_recipe}")

    # Calculate required resources
    iron_plates_needed = 10  # 1 per 2 transport belts, so 5 * 2 = 10
    iron_gear_wheels_needed = 5  # 1 per 2 transport belts

    # Mine iron ore
    iron_ore_needed = iron_plates_needed + (iron_gear_wheels_needed * 2)
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, iron_ore_needed + 5)  # Mine a bit extra
    print(f"Mined {iron_mined} iron ore")

    # Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    coal_mined = harvest_resource(coal_position, 7) # Mine 5 coal enough for smelting
    print(f"Mined {coal_mined} coal")
    print(f"Current inventory: {inspect_inventory()}")
    

    # """[SYNTHESISED]
    # Name: smelt_iron_plates
    # Objective: Smelt iron ore into iron plates
    # Mining setup: No existing setup
    # Inventory: We have iron ore and coal in the inventory
    # :param iron_ore_count (int): The number of iron ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_iron_plates(iron_ore_count=iron_mined, coal_needed=7)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= iron_plates_needed, f"Not enough iron plates. Have {iron_plates}, need {iron_plates_needed}"
    print(f"Smelted {iron_plates} iron plates")

    # Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, iron_gear_wheels_needed)
    iron_gear_wheels = inspect_inventory()[Prototype.IronGearWheel]
    assert iron_gear_wheels >= iron_gear_wheels_needed, f"Not enough iron gear wheels. Have {iron_gear_wheels}, need {iron_gear_wheels_needed}"
    print(f"Crafted {iron_gear_wheels} iron gear wheels")

    # Craft transport belts
    craft_item(Prototype.TransportBelt, 10)  # Craft 10 transport belts
    
    # Verify crafting was successful
    transport_belts = inspect_inventory()[Prototype.TransportBelt]
    assert transport_belts >= 10, f"Failed to craft 10 transport belts. Current count: {transport_belts}"
    print(f"Successfully crafted {transport_belts} transport belts!")
    
    # Print final inventory
    print(f"Final inventory: {inspect_inventory()}")

    return True


###FUNC SEP

craft_10_transport_belts()