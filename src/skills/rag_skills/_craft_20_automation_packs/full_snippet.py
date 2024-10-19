from factorio_instance import *


def smelt_ore(ore_type: Prototype, ore_count: int, furnace: Entity) -> None:
    """
    Objective: Smelt a specific type of ore into plates
    Mining setup: We have a fueled furnace. The furnace has already been fueled with coal
    Inventory: We have the required ore in the inventory
    :param ore_type (Prototype): The type of ore to smelt (Prototype.IronOre or Prototype.CopperOre)
    :param ore_count (int): The number of ores to smelt
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Verify we have enough ore in the inventory
    # 2. Determine the corresponding plate type for the given ore
    # 3. Insert the ore into the furnace
    # 4. Wait for smelting to complete
    # 5. Extract the plates from the furnace
    # 6. Verify we have the correct number of plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Verify we have enough ore in the inventory
    ore_in_inventory = inspect_inventory()[ore_type]
    assert ore_in_inventory >= ore_count, f"Not enough {ore_type} in inventory. Required: {ore_count}, Available: {ore_in_inventory}"

    # Determine the corresponding plate type
    if ore_type == Prototype.IronOre:
        plate_type = Prototype.IronPlate
    elif ore_type == Prototype.CopperOre:
        plate_type = Prototype.CopperPlate
    else:
        raise ValueError(f"Unsupported ore type: {ore_type}")

    # Insert the ore into the furnace
    insert_item(ore_type, furnace, ore_count)
    print(f"Inserted {ore_count} {ore_type} into the furnace")

    # Get the initial number of plates in the inventory
    initial_plates = inspect_inventory()[plate_type]

    # Wait for smelting to complete (1 second per ore)
    sleep(ore_count)

    # Extract the plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(plate_type, furnace.position, ore_count)
        current_plates = inspect_inventory()[plate_type]
        plates_produced = current_plates - initial_plates
        if plates_produced >= ore_count:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    print(f"Extracted {plates_produced} {plate_type} from the furnace")

    # Verify we have the correct number of plates in our inventory
    final_plates = inspect_inventory()[plate_type]
    plates_produced = final_plates - initial_plates
    assert plates_produced >= ore_count, f"Failed to smelt enough {plate_type}. Expected: {ore_count}, Produced: {plates_produced}"

    print(f"Successfully smelted {plates_produced} {plate_type}")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP


def smelt_ores(iron_ore_count: int, copper_ore_count: int) -> None:
    """
    Objective: Smelt iron and copper ores into plates.
    Need to also find or craft a furnace and fuel it with coal
    Mining setup: No existing setup
    Inventory: We have iron and copper ores in the inventory
    :param iron_ore_count (int): The number of iron ores to smelt
    :param copper_ore_count (int): The number of copper ores to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough ores in the inventory
    # 2. Find or create a stone furnace
    # 3. Fuel the furnace with coal
    # 4. Smelt iron ores
    # 5. Smelt copper ores
    # 6. Extract the smelted plates
    # 7. Verify the results
    # [END OF PLANNING]

    print(f"Starting to smelt {iron_ore_count} iron ores and {copper_ore_count} copper ores")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough ores in the inventory
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= iron_ore_count, f"Not enough iron ore. Required: {iron_ore_count}, Available: {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.CopperOre] >= copper_ore_count, f"Not enough copper ore. Required: {copper_ore_count}, Available: {inventory[Prototype.CopperOre]}"

    # Find or create a stone furnace
    furnaces = inspect_entities().get_entities(Prototype.StoneFurnace)
    furnace_position = Position(x=0, y=0)
    if not furnaces:
        print("No existing furnace found. Crafting a new one.")
        # check if we have a furnace in the inventory
        furnace_in_inventory = inventory.get(Prototype.StoneFurnace, 0)
        if furnace_in_inventory == 0:
            # check if we have the required resources to craft a furnace
            if inventory[Prototype.Stone] < 5:
                # mine stone if we don't have enough
                stone_position = nearest(Resource.Stone)
                move_to(stone_position)
                print(f"Moved to stone patch at {stone_position}")
                harvest_resource(stone_position, 5)
                print(f"Mined 5 stone")
                move_to(furnace_position)  # Move back to the starting position

            craft_item(Prototype.StoneFurnace, 1)
        furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    else:
        furnace = furnaces[0]
    
    print(f"Using furnace at position: {furnace.position}")
    move_to(furnace.position)

    # Fuel the furnace with coal
    coal_needed = (iron_ore_count + copper_ore_count) // 4 + 1  # Assuming 1 coal can smelt 4 ores
    if inventory[Prototype.Coal] < coal_needed:
        coal_to_mine = coal_needed - inventory[Prototype.Coal]
        coal_position = nearest(Resource.Coal)
        move_to(coal_position)
        harvest_resource(coal_position, coal_to_mine)
        move_to(furnace.position)
    
    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Inserted {coal_needed} coal into the furnace")

    # """[SYNTHESISED]
    # Name: smelt_ore
    # Objective: Smelt a specific type of ore into plates
    # Mining setup: We have a fueled furnace. The furnace has already been fueled with coal
    # Inventory: We have the required ore in the inventory
    # :param ore_type (Prototype): The type of ore to smelt (Prototype.IronOre or Prototype.CopperOre)
    # :param ore_count (int): The number of ores to smelt
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None
    # [END OF SYNTHESISED]"""

    # Smelt iron ores
    smelt_ore(ore_type=Prototype.IronOre, ore_count=iron_ore_count, furnace=furnace)

    # Smelt copper ores
    smelt_ore(ore_type=Prototype.CopperOre, ore_count=copper_ore_count, furnace=furnace)

    # Verify the results
    final_inventory = inspect_inventory()
    iron_plates_smelted = final_inventory[Prototype.IronPlate] - inventory[Prototype.IronPlate]
    copper_plates_smelted = final_inventory[Prototype.CopperPlate] - inventory[Prototype.CopperPlate]

    print(f"Iron plates smelted: {iron_plates_smelted}")
    print(f"Copper plates smelted: {copper_plates_smelted}")
    print(f"Final inventory: {final_inventory}")

    assert iron_plates_smelted >= iron_ore_count, f"Failed to smelt enough iron plates. Expected at least {iron_ore_count}, but got {iron_plates_smelted}"
    assert copper_plates_smelted >= copper_ore_count, f"Failed to smelt enough copper plates. Expected at least {copper_ore_count}, but got {copper_plates_smelted}"

    print("Successfully smelted all ores into plates!")



###FUNC SEP


def craft_20_automation_packs():
    """
    Objective: Craft 20 automation science packs. The final success should be checked by looking if 20 automation science packs are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for automation science packs
    # 2. Calculate the total resources needed
    # 3. Mine the necessary resources (iron ore and copper ore). We will need to mine all of the resources as we don't have any in our inventory
    # 4. Craft iron plates and copper plates
    # 5. Craft iron gear wheels
    # 6. Craft the automation science packs
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    automation_pack_recipe = get_prototype_recipe(Prototype.AutomationSciencePack)
    print(f"Automation Science Pack recipe: {automation_pack_recipe}")

    # Calculate total resources needed
    iron_plates_needed = 20 * 2  # 1 for the pack, 1 for the gear wheel
    copper_plates_needed = 20

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    iron_mined = harvest_resource(iron_position, iron_plates_needed + 5)  # Extra 5 for safety
    print(f"Mined {iron_mined} iron ore")

    # Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    copper_mined = harvest_resource(copper_position, copper_plates_needed + 5)  # Extra 5 for safety
    print(f"Mined {copper_mined} copper ore")

    # """[SYNTHESISED]
    # Name: smelt_ores
    # Objective: Smelt iron and copper ores into plates.
    # Need to also find or craft a furnace and fuel it with coal
    # Mining setup: No existing setup
    # Inventory: We have iron and copper ores in the inventory
    # :param iron_ore_count (int): The number of iron ores to smelt
    # :param copper_ore_count (int): The number of copper ores to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_ores(iron_ore_count=iron_plates_needed, copper_ore_count=copper_plates_needed)

    # Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 20)
    iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert iron_gear_count >= 20, f"Failed to craft enough iron gear wheels. Expected 20, got {iron_gear_count}"
    print(f"Crafted {iron_gear_count} iron gear wheels")

    # Craft automation science packs
    craft_item(Prototype.AutomationSciencePack, 20)
    
    # Verify crafting success
    final_inventory = inspect_inventory()
    automation_pack_count = final_inventory.get(Prototype.AutomationSciencePack, 0)
    assert automation_pack_count >= 20, f"Failed to craft 20 automation science packs. Crafted: {automation_pack_count}"
    
    print(f"Successfully crafted {automation_pack_count} automation science packs!")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP

craft_20_automation_packs()