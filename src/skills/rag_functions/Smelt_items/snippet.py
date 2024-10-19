from factorio_instance import *
def smelt_iron_with_a_furnace(input_coal: int, input_iron_ore: int, furnace: Entity):
    """
    Objective: We need to smelt iron ores into plates with a furnace
    Mining setup: We have a furnace on the map that we can use to smelt iron ores
    Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    :param input_coal (int): The number of coal to insert into the furnace
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Prototype.StoneFurnace): The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING] 
    # We first need to check if we have enough iron and coal in the inventory to smelt the iron plates
    # Then we will insert input coal and iron ore into the furnace from the inventory
    # We will then wait and extract the iron plates
    # Finally we will assert that we have enough iron plates 
    # [END OF PLANNING]

    # First we need to do initial prints for logging
    # print out the inventory
    print(f"Inventory before smelting: {inspect_inventory()}")

    # check if we have enough iron and coal in the inventory
    iron_in_inventory = inspect_inventory()[Prototype.IronOre]
    coal_in_inventory = inspect_inventory()[Prototype.Coal]
    assert iron_in_inventory >= input_iron_ore, f"Failed to find enough iron ore in inventory. Expected {input_iron_ore}, but got {iron_in_inventory}"
    assert coal_in_inventory >= input_coal, f"Failed to find enough coal in inventory. Expected {input_coal}, but got {coal_in_inventory}"
    # add coal and iron to the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")
    print(f"Inventory after inserting: {inspect_inventory}")

    # Get the initial number of iron plates in the inventory
    # This is used to check how many plates we have after smelting
    # This is important to know if we have smelted enough plates
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]

    # Wait for smelting to complete
    sleep(input_iron_ore * 0.7)
    max_attempts = 5
    for _ in range(max_attempts):
        # IMPORTANT: Always try to extract the exact number of items you need
        # It is OK to extract more than the furnace has
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        # IMPORTANT: To check the extraction, you need to check the amount of iron plates in the inventory
        # After every extraction, check how many plates you have in your inventory
        iron_plates_in_inventory = inspect_inventory()[Prototype.IronPlate]
        # take away the initial plates from the current plates to get the number of plates smelted
        iron_plates_extracted = iron_plates_in_inventory - initial_iron_plates
        # If you have enough plates, break out of the loop
        if iron_plates_extracted >= input_iron_ore:
            break
        sleep(10)  # Wait a bit more if not all plates are ready

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")
    print(f"Inventory after extracting: {inspect_inventory()}")
    # Check if we have more than input_iron_ore iron plates
    iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
    assert iron_in_inventory >= input_iron_ore, f"Failed to smelt enough iron plates. Expected {input_iron_ore}, but got {iron_in_inventory}"
