from factorio_instance import *

def smelt_iron_with_a_furnace(input_coal: int, input_iron_ore: int, furnace: Entity):
    """
    Objective: Smelt iron ores into plates with a furnace. The furnace needs to be fueled
    Mining setup: We have a furnace on the map that we can use to smelt iron ores.  We need to put coal in it
    Inventory: We have enough iron ore and coal in the inventory to smelt the iron plates
    :param input_coal (int): The number of coal to insert into the furnace
    :param input_iron_ore (int): The number of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None as the iron plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Insert coal and iron ore into the furnace
    # 3. Wait for smelting to complete
    # 4. Extract iron plates from the furnace
    # 5. Verify that we have the expected number of iron plates in our inventory
    # [END OF PLANNING]

    print(f"Starting smelting process. Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore and coal in the inventory
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= input_iron_ore, f"Not enough iron ore. Required: {input_iron_ore}, Available: {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.Coal] >= input_coal, f"Not enough coal. Required: {input_coal}, Available: {inventory[Prototype.Coal]}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Get the initial number of iron plates in the inventory
    initial_iron_plates = inventory[Prototype.IronPlate]

    # Wait for smelting to complete (assuming 3.2 seconds per iron plate)
    smelting_time = input_iron_ore * 3.2
    print(f"Waiting for {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    max_attempts = 5
    iron_plates_extracted = 0
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        if iron_plates_extracted >= input_iron_ore:
            break
        print(f"Extracted {iron_plates_extracted} iron plates. Waiting for more...")
        sleep(5)

    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")

    # Verify that we have the expected number of iron plates in our inventory
    final_inventory = inspect_inventory()
    final_iron_plates = final_inventory[Prototype.IronPlate]
    assert final_iron_plates >= initial_iron_plates + input_iron_ore, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + input_iron_ore}, but got {final_iron_plates}"

    print(f"Smelting complete. Final inventory: {final_inventory}")
    print(f"Successfully smelted {iron_plates_extracted} iron plates!")


###FUNC SEP


def craft_electric_mining_drill():
    """
    Objective: We need to craft one electric mining drill
    Mining setup: There are no entities on the map
    Inventory: {
            "iron-plate": 20,
            "coal": 20,
            "copper-plate": 20,
            "stone-furnace": 3
          }
    """
    # [PLANNING] 
    # We have got 20 iron plates, 20 copper plates, 20 coal and 3 stone furnaces in the inventory which we can use
    # We need to mine additional resources for the mining drill, specifically more iron ore for more iron plates
    # We will harvest more iron than needed to make sure we have enough, we will harvest 10 iron ore to be exact 
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
    # Place the stone furnace close to your current location, i.e iron_position
    # VERY IMPORTANT: FIRST MOVE TO THE POSITION WE PLACE IT TO AS WE CAN'T PLACE IT FROM A FAR DISTANCE
    move_to(iron_position)
    furnace = place_entity(entity = Prototype.StoneFurnace, position =  iron_position, direction = Direction.UP)
    
    # [SUBFUNCTION]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace. We need to use a input furnace variable
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores. We need to put coal in it
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_coal: The number of coal to insert into the furnace
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SUBFUNCTION]
    smelt_iron_with_a_furnace(input_coal=10, input_iron_ore=30, furnace=furnace)
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

###FUNC SEP
craft_electric_mining_drill()