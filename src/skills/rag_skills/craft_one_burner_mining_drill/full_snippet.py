from factorio_instance import *


def smelt_iron_with_a_furnace(input_coal: int, input_iron_ore: int, furnace: Entity, output_iron_plate: int):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores. We need to fuel the furnace with coal
    Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    :param input_coal (int): The number of coal to insert into the furnace
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :param output_iron_plate (int): The number of iron plates to extract from the furnace
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Insert coal and iron ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the iron plates from the furnace
    # 5. Verify that we have the required number of iron plates in the inventory
    # [END OF PLANNING]

    # Log initial inventory state
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Check if we have enough iron ore and coal in the inventory
    iron_ore_in_inventory = initial_inventory.get(Prototype.IronOre, 0)
    coal_in_inventory = initial_inventory.get(Prototype.Coal, 0)
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"
    assert coal_in_inventory >= input_coal, f"Not enough coal in inventory. Required: {input_coal}, Available: {coal_in_inventory}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Log inventory after inserting items
    after_insert_inventory = inspect_inventory()
    print(f"Inventory after inserting items: {after_insert_inventory}")

    # Wait for the smelting process to complete
    print("Waiting for smelting process to complete...")
    sleep(20)  # Adjust this value based on the smelting time of your furnace

    # Extract iron plates from the furnace
    max_attempts = 5
    iron_plates_extracted = 0
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, output_iron_plate - iron_plates_extracted)
        current_inventory = inspect_inventory()
        iron_plates_extracted = current_inventory.get(Prototype.IronPlate, 0) - initial_inventory.get(Prototype.IronPlate, 0)
        print(f"Attempt {attempt + 1}: Extracted {iron_plates_extracted} iron plates")
        
        if iron_plates_extracted >= output_iron_plate:
            break
        
        if attempt < max_attempts - 1:
            print("Not all plates ready. Waiting a bit longer...")
            sleep(10)

    # Log final inventory state
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")

    # Verify that we have the required number of iron plates
    total_iron_plates = final_inventory.get(Prototype.IronPlate, 0)
    assert total_iron_plates >= output_iron_plate, f"Failed to smelt enough iron plates. Required: {output_iron_plate}, Produced: {total_iron_plates}"

    print(f"Successfully smelted {iron_plates_extracted} iron plates")


###FUNC SEP


def craft_one_burner_mining_drill():
    """
    Objective: We need to craft one burner mining drill from scratch.
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # We need to mine everything from scratch as we have no resources in the inventory
    # 1. Get the recipe for the burner mining drill
    # 2. Mine the necessary raw resources (iron ore, stone, coal)
    # 3. Craft stone furnaces
    # 4. Smelt iron plates
    # 5. Craft iron gear wheels
    # 6. Craft the burner mining drill
    # 7. Verify the final result
    # [END OF PLANNING]

    # Print initial information
    drill_recipe = get_prototype_recipe(Prototype.BurnerMiningDrill)
    print(f"Burner Mining Drill recipe: {drill_recipe}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 20)
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 20, f"Failed to mine enough iron ore. Expected 20, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 10, f"Failed to mine enough stone. Expected 10, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # Step 3: Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 5)
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    print(f"Current inventory after mining: {inspect_inventory()}")

    # Step 4: Craft stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")

    # Step 5: Smelt iron plates
    furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position=coal_position, direction=Direction.UP, spacing=1)
    
    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. We need to fuel the furnace with coal
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_coal (int): The number of coal to insert into the furnace
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :param output_iron_plate (int): The number of iron plates to extract from the furnace
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_coal=5, input_iron_ore=20, furnace=furnace, output_iron_plate=10)

    iron_plate_count = inspect_inventory()[Prototype.IronPlate]
    assert iron_plate_count >= 10, f"Failed to smelt enough iron plates. Expected 10, but got {iron_plate_count}"
    print(f"Smelted {iron_plate_count} iron plates")

    # Step 6: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 3)
    gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheel_count >= 3, f"Failed to craft enough iron gear wheels. Expected 3, but got {gear_wheel_count}"
    print(f"Crafted {gear_wheel_count} iron gear wheels")

    print(f"Current inventory before crafting burner mining drill: {inspect_inventory()}")

    # Step 7: Craft burner mining drill
    craft_item(Prototype.BurnerMiningDrill, 1)
    drill_count = inspect_inventory()[Prototype.BurnerMiningDrill]
    assert drill_count == 1, f"Failed to craft burner mining drill. Expected 1, but got {drill_count}"
    print("Burner mining drill crafted successfully!")

    # Final inventory check
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    assert final_inventory[Prototype.BurnerMiningDrill] == 1, "Burner mining drill not found in the final inventory"

    print("Objective completed: One burner mining drill has been crafted and is in the inventory.")


###FUNC SEP

craft_one_burner_mining_drill()