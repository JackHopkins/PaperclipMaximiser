from factorio_instance import *
def craft_one_burner_mining_drill_from_scratch():
    """
    Objective: We need to craft one burner mining drill from scratch as we have no items in our inventory.
    Mining setup: Currently there are no entities on the map
    Inventory: We have no items in our inventory
    """
    # [PLANNING] 
    # We need to Mine raw resources and craft everything as we don't have any resources in the inventory
    # We need enough iron ore for the plates and gear wheels, stone for the furnaces, and coal for the furnaces
    # We will harvest more of everything to make sure we have enough, we will harvest 20 iron ore, 15 stone, and 10 coal 
    # We also need to smelt iron plates
    # we need 2 furnaces, 1 for smelting iron plates and one for crafting the burner-mining-drill 
    # [END OF PLANNING]

    # First we need to do initial prints for logging
    # first get the recipe for the burner mining drill
    drill_recipe = get_recipe(Prototype.BurnerMiningDrill)
    print(f"Drill recipe: {drill_recipe}")
    # print out initial inventory
    print(f"Inventory at starting: {inspect_inventory()}")

    # Mine enough iron ore for the plates and gear wheels
    # harvest more than needed to be sure
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    print(f"Moved to iron patch at {iron_position}")
    harvest_resource(iron_position, 20)
    # Check if we have enough iron ore
    iron_ore_count = inspect_inventory()[Resource.IronOre]
    assert iron_ore_count >= 20, f"Failed to mine enough iron ore. Expected 20, but got {iron_ore_count}"
    print(f"Mined {iron_ore_count} iron ore")
    print(f"Curent inventory: {inspect_inventory()}")

    # Mine enough stone for 2 furnaces
    # harvest more than needed to be sure
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    harvest_resource(stone_position, 15)
    # Check if we have enough stone
    stone_count = inspect_inventory()[Resource.Stone]
    assert stone_count >= 10, f"Failed to mine enough stone. Expected 10, but got {stone_count}"
    print(f"Mined {stone_count} stone")
    print(f"Curent inventory: {inspect_inventory()}")


    # Mine enough coal for the furnaces
    # harvest more than needed to be sure
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    harvest_resource(coal_position, 10)
    # Check if we have enough coal
    coal_count = inspect_inventory()[Resource.Coal]
    assert coal_count >= 5, f"Failed to mine enough coal. Expected 5, but got {coal_count}"
    print(f"Mined {coal_count} coal")
    print(f"Curent inventory: {inspect_inventory()}")


    # Step 2: Craft the stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 2, f"Failed to craft stone furnace. Expected 2, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")
    print(f"Curent inventory: {inspect_inventory()}")

    # Step 3: Smelt iron plates
    # Place the stone furnacec close to the coal position
    # VERY IMPORTANT: FIRST MOVE TO THE POSITION WE PLACE IT TO AS WE CAN'T PLACE IT FROM A FAR DISTANCE
    move_to(coal_position)
    # place the furnace
    furnace = place_entity(entity = Prototype.StoneFurnace, position =  coal_position, direction = Direction.UP)
    # [SUBFUNCTION]
    # Name: smelt_iron_with_a_furnace
    # Objective: We need to smelt iron ores into plates with a furnace. We need to use a input furnace variable
    # Mining setup: We have a furnace on the map that we can use to smelt iron ores
    # Inventory: We have enough iron and coal in the inventory to smelt the iron plates
    # :param input_coal: The number of coal to insert into the furnace
    # :param input_iron_ore: The number of iron ore to insert into the furnace
    # :param furnace: The furnace entity to use for smelting
    # :return: None as the iron plates will be in inventory
    # [END OF SUBFUNCTION]
    smelt_iron_with_a_furnace(input_coal=10, input_iron_ore=20, furnace=furnace)
    # Check if we have 10 iron plates
    iron_in_inventory = inspect_inventory()[Prototype.IronPlate]
    assert iron_in_inventory >= 10, f"Failed to smelt enough iron plates. Expected 10, but got {iron_in_inventory}"
    print(f"Smelted {iron_in_inventory} iron plates")
    print(f"Curent inventory: {inspect_inventory()}")

    # Step 4: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 3)
    # Check if we have enough iron gear wheels
    gear_wheel_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheel_count == 3, f"Failed to craft enough iron gear wheels. Expected 3, but got {gear_wheel_count}"
    print(f"Crafted {gear_wheel_count} iron gear wheels")
    print(f"Curent inventory: {inspect_inventory()}")

    # Step 5: Craft burner-mining-drill
    craft_item(Prototype.BurnerMiningDrill, 1)
    # Check if we have crafted the burner-mining-drill
    drill_count = inspect_inventory()[Prototype.BurnerMiningDrill]
    assert drill_count == 1, f"Failed to craft burner-mining-drill. Expected 1, but got {drill_count}"
    print("Burner-mining-drill crafted successfully!")
    print(f"Curent inventory: {inspect_inventory()}")
