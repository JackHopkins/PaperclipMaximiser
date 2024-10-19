from factorio_instance import *


def smelt_iron_with_a_furnace(input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace.
    We need to use an input furnace variable and put coal in it for fuel
    Mining setup: We have a unfueled furnace on the map that we can use to smelt iron ores. We need to put coal in it
    Inventory: We have enough iron ore in the inventory to smelt the iron plates
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore in the inventory
    # 2. Move to the furnace
    # 3. Insert coal into the furnace for fuel 
    # 4. Insert iron ore into the furnace
    # 5. Wait for smelting to complete
    # 6. Extract iron plates from the furnace
    # 7. Verify that we have the correct number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting iron smelting process. Input iron ore: {input_iron_ore}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore in the inventory
    iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
    assert iron_ore_in_inventory >= input_iron_ore, f"Not enough iron ore in inventory. Required: {input_iron_ore}, Available: {iron_ore_in_inventory}"

    # Move to the furnace
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Insert coal into the furnace for fuel (if needed)
    furnace_contents = inspect_inventory(furnace)
    coal_in_furnace = furnace_contents.get(Prototype.Coal, 0)
    if coal_in_furnace < 1:
        coal_to_insert = min(5, inspect_inventory()[Prototype.Coal])  # Insert up to 5 coal, or all we have if less
        insert_item(Prototype.Coal, furnace, coal_to_insert)
        print(f"Inserted {coal_to_insert} coal into the furnace")

    # Insert iron ore into the furnace
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (assuming 1 seconds per iron plate)
    smelting_time = input_iron_ore * 1
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)
    max_attempts = 5
    # get the initial number of irom plates in the inventory
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_produced = current_iron_plates - initial_iron_plates
        if iron_plates_produced >= input_iron_ore:
            break
        sleep(2)  # Wait a bit more if not all plates are ready
        
    # Verify that we have the correct number of iron plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    iron_plates_produced = final_iron_plates - initial_iron_plates
    assert iron_plates_produced == input_iron_ore, f"Expected to produce {input_iron_ore} iron plates, but produced {iron_plates_produced}"

    print(f"Successfully smelted {iron_plates_produced} iron plates")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP


def craft_20_firearm_magazines():
    """
    Objective: Craft 20 firearm magazines. The final success should be checked by looking if 20 firearm magazines are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for firearm magazines
    # 2. Calculate the total iron plates needed (4 * 20 = 80)
    # 3. Mine iron ore (we'll mine extra to account for inefficiencies)
    # 4. Mine stone for crafting a stone furnace and coal for fuel
    # 5. Craft a stone furnace to smelt iron plates
    # 6. Smelt iron plates
    # 7. Craft firearm magazines
    # 8. Verify the final count of firearm magazines in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    firearm_magazine_recipe = get_prototype_recipe(Prototype.FirearmMagazine)
    print(f"Firearm Magazine recipe: {firearm_magazine_recipe}")

    # Step 1: Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 100)  # Mining extra to account for inefficiencies
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 80, f"Failed to mine enough iron ore. Expected at least 80, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")

    # Step 2: Mine stone for furnace
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 10)  # Mining extra to account for inefficiencies
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 5, f"Failed to mine enough stone. Expected at least 5, but got {stone_count}"
    print(f"Mined {stone_count} stone")

    # Mine coal for the furnace
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 5)  # Mining extra to account for inefficiencies
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected at least 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")

    # Step 3: Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # Step 4: Place furnace and smelt iron plates
    # place the furnace to the iron position and move there
    move_to(iron_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # """[SYNTHESISED]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace.
    # We need to use an input furnace variable
    # Mining setup: We have a unfueled furnace on the map that we can use to smelt iron ores. We need to put coal in it
    # Inventory: We have enough iron ore in the inventory to smelt the iron plates
    # :param input_iron_ore (int): The number of iron ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_iron_with_a_furnace(input_iron_ore=80, furnace=furnace)

    # Check if we have enough iron plates
    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 80, f"Failed to smelt enough iron plates. Expected at least 80, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Step 5: Craft firearm magazines
    craft_item(Prototype.FirearmMagazine, 20)
    
    # Final check: Verify the count of firearm magazines in the inventory
    magazine_count = inspect_inventory()[Prototype.FirearmMagazine]
    assert magazine_count == 20, f"Failed to craft 20 firearm magazines. Current count: {magazine_count}"
    print(f"Successfully crafted {magazine_count} firearm magazines!")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP

craft_20_firearm_magazines()