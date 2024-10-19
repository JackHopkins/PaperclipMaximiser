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


def craft_burner_inserter():
    """
    Objective: Craft one BurnerInserter. The final success should be checked by looking if a BurnerInserter is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for BurnerInserter
    # 2. Mine necessary resources (iron ore and coal for fuel). We need to mine everything as we don't have any resources in the inventory
    # 3. Craft a stone furnace to smelt iron ore
    # 4. Smelt iron plates
    # 5. Craft iron gear wheel
    # 6. Craft burner inserter
    # 7. Verify success
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    burner_inserter_recipe = get_prototype_recipe(Prototype.BurnerInserter)
    print(f"Burner Inserter recipe: {burner_inserter_recipe}")

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 10)  # Mine extra to be safe
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 6, f"Failed to mine enough iron ore. Expected at least 6, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Mine stone for furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # Mine extra to be safe
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # mine coal for the furnace
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 5)  # Mine extra to be safe
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected at least 5, but got {coal_count}"

    # Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")
    
    # Place furnace and smelt iron plates
    # place at iron position
    # first move to iron position
    move_to(iron_position)
    furnace = place_entity(Prototype.StoneFurnace, position=iron_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # add coal to the furnace
    insert_item(Prototype.Coal, furnace, 5)
    print("Added 5 coal to the furnace")

    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace.
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. The furnace has been fueled with coal
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=6, furnace=furnace)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 3, f"Failed to smelt enough iron plates. Expected at least 3, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Craft iron gear wheel
    craft_item(Prototype.IronGearWheel, 1)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count == 1, f"Failed to craft iron gear wheel. Expected 1, but got {gear_count}"
    print("Crafted 1 iron gear wheel")

    # Craft burner inserter
    craft_item(Prototype.BurnerInserter, 1)
    inserter_count = inspect_inventory()[Prototype.BurnerInserter]
    assert inserter_count == 1, f"Failed to craft burner inserter. Expected 1, but got {inserter_count}"
    print("Successfully crafted 1 burner inserter!")

    # Final inventory check
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    assert final_inventory[Prototype.BurnerInserter] == 1, "Burner Inserter not found in final inventory"

    print("Objective completed: Crafted one BurnerInserter and verified it's in the inventory.")


###FUNC SEP

craft_burner_inserter()