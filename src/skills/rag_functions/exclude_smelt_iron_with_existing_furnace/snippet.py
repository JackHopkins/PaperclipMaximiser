from factorio_instance import *
def smelt_iron_plates_with_furnace():
    """
    Objective: We need to smelt 10 iron ore into plates
    Mining setup: There are furnaces on the map
    Inventory: We have no items in our inventory
    """
    # [PLANNING] 
    # We first need to mine 10 iron ores to make sure we have enough iron
    # We then need to find a furnace that has enough coal in (5). If no furnace has enough coal, we need to mine coal
    # We will then need to smelt the iron ores into plates
    # Finally we will assert that we have enough iron plates
    # [END OF PLANNING]

    # First we need to do initial prints for logging
    # first print out the inventory
    initial_inv = inspect_inventory()
    print(f"Initial inventory: {initial_inv}")

    # Step 1 - Mine 10 more iron ores
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 10)
    iron_count = inspect_inventory()[Resource.IronOre] 
    # Check if we have 10 iron ores
    assert iron_count >= 10, f"Failed to mine enough iron ores. Expected 10, but got {iron_count}"
    print(f"Mined {iron_count} iron ores")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 2 - Inspect the map to find furnaces
    furnaces = inspect_entities().get_entities(Prototype.StoneFurnace)
    
    # get the furnace with most coal
    # We need atleast 5 coal so if we find a furnace with 5 coal, we can use it
    # Otherwise we have to mine coal
    furnaces_with_coal = [furnace for furnace in furnaces if furnace.contents.get(['coal'], 0) >= 5]
    

    if len(furnaces_with_coal) == 0:
        # Mine coal for the furnace
        coal_position = nearest(Resource.Coal)
        move_to(coal_position)
        harvest_resource(coal_position, 5)
        print(f"Mined 5 coal")
        print(f"Current inventory: {inspect_inventory()}")

        # choose the first furnace in the list
        furnace_with_coal = furnaces[0]
        # move to the furnace
        move_to(furnace_with_coal.position)
        print(f"Moving to furnace at {furnace_with_coal.position}")

        # add coal to the furnace
        insert_item(Prototype.Coal, furnace_with_coal, 5)
    
    else:
        furnace_with_coal = furnaces_with_coal[0]
        # move to the furnace
        move_to(furnace_with_coal.position)
        print(f"Moving to furnace at {furnace_with_coal.position}")

    # [SUBFUNCTION]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace. We need to use a input furnace variable
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SUBFUNCTION]
    smelt_iron_with_a_furnace(input_iron_ore=10, furnace=furnace_with_coal)
    print("Smelted 10 iron plates!")
    print(f"Current inventory: {inspect_inventory()}")

    # Check if we have 10 iron plates
    iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
    assert iron_in_inventory >= 10, f"Failed to smelt enough iron plates. Expected 10, but got {iron_in_inventory}"
    print("Successfully smelted 10 iron plates!")