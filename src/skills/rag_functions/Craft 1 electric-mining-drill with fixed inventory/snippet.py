from factorio_instance import *
def craft_electric_mining_drill():
    """
    Objective: We need to craft one electric mining drill
    Mining setup: There are no entities on the map
    Inventory: We have no items in our inventory
    """
    # [PLANNING] 
    # We have got 20 iron plates, 20 copper plates, 20 coal and 2 stone furnaces in the inventory which we can use
    # We need to mine additional resources for the mining drill, specifically more iron ore for more iron plates
    # Then we need to craft the required iron gear wheels and electronic circuits for the drill 
    # [END OF PLANNING]

    # First we need to do initial prints for logging
    # first print out the recipe for the drill
    drill_recipe = get_recipe(Prototype.ElectricMiningDrill)
    print(f"Drill recipe: {drill_recipe}")

    # Step 1 - Mine 10 more iron ores to make sure we have enough iron for all required iron plates, circuits and gear wheels
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    harvest_resource(iron_position, 10)
    iron_count = inspect_inventory()[Resource.IronOre] 
    # Check if we have 10 iron ores
    assert iron_count >= 10, f"Failed to mine enough iron ores. Expected 10, but got {iron_count}"
    print(f"Mined {iron_count} iron ores")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 2: Smelt iron plates using furnace in the inventory
    # Place the stone furnacec close to your current location, i.e iron_position
    furnace = place_entity_next_to(Prototype.StoneFurnace, reference_position = iron_position, direction = Direction.UP, spacing = 1)
    # [SUBFUNCTION]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_coal: The number of coal to insert into the furnace
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :param output_iron_plate: The number of iron plates to extract from the furnace
    # :return: None as the iron plates will be in inventory
    # [END OF SUBFUNCTION]
    smelt_iron_with_a_furnace(input_coal=10, input_iron_ore=30, furnace=furnace, output_iron_plate=30)
    print("Smelted 30 iron plates!")
    print(f"Current inventory: {inspect_inventory()}")

    # Check if we have 30 iron plates
    iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
    assert iron_in_inventory >= 30, f"Failed to smelt enough iron plates. Expected 30, but got {iron_in_inventory}"

    # Step 3: Craft 3 iron gear wheels
    craft_item(Prototype.IronGearWheel, 3)  
    # Check if we have 3 iron gear wheels
    iron_gear_count = inspect_inventory()[Prototype.IronGearWheel]  
    assert iron_gear_count >= 3, f"Failed to craft 3 iron gears. Current count: {iron_gear_count}"
    print("Successfully crafted 3 iron gear wheels!")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 4: Craft 3 electronic circuits
    craft_item(Prototype.ElectronicCircuit, 3)
    # Check if we have 3 electronic circuits
    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
    assert circuit_count >= 3, f"Failed to craft 3 circuits. Current count: {circuit_count}"
    print("Successfully crafted 3 electronic circuits!")
    print(f"Current inventory: {inspect_inventory()}")

    # Step 5: Craft electric mining drill
    craft_item(Prototype.ElectricMiningDrill, 1)
    # Check if we have 1 electric mining drill
    drill_count = inspect_inventory()[Prototype.ElectricMiningDrill]
    assert drill_count >= 1, f"Failed to craft electric mining drill. Current count: {drill_count}"
    print("Successfully crafted 1 electric mining drill!")