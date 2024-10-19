from factorio_instance import *


def smelt_plates(iron_ore_count: int, copper_ore_count: int, total_coal: int) -> None:
    """
    Objective: Smelt the required number of iron and copper plates using two furnaces
    Mining setup: There are no entities on the map
    Inventory: We have iron ore, copper ore, and coal in the inventory. We also have 2 stone furnaces
    :param iron_ore_count (int): The number of iron ore to smelt
    :param copper_ore_count (int): The number of copper ore to smelt
    :param total_coal (int): The total amount of coal to be used for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Place the 2 furnaces
    # 2. Insert coal into both furnaces
    # 3. Insert iron ore into one furnace and copper ore into the other
    # 4. Wait for smelting to complete
    # 5. Extract the iron and copper plates from the furnaces
    # 6. Verify that we have the correct number of plates in our inventory
    # [END OF PLANNING]

    print(f"Starting inventory: {inspect_inventory()}")

    # place down the 2 furnaces
    iron_furnace_position = Position(x=0, y=0)
    # move to the furnace position
    move_to(iron_furnace_position)
    iron_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_furnace_position)
    assert iron_furnace, "Failed to place iron furnace"
    print(f"Iron furnace placed at {iron_furnace_position}")

    copper_furnace_position = Position(x=0, y=1)
    copper_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, copper_furnace_position)
    assert copper_furnace, "Failed to place copper furnace"
    print(f"Copper furnace placed at {copper_furnace_position}")

    # put half the coal in each furnace
    coal_per_furnace = total_coal // 2
    insert_item(Prototype.Coal, iron_furnace, coal_per_furnace)
    insert_item(Prototype.Coal, copper_furnace, coal_per_furnace)
    print(f"Inserted {coal_per_furnace} coal into each furnace")

    # Insert iron ore and copper ore into respective furnaces
    insert_item(Prototype.IronOre, iron_furnace, iron_ore_count)
    insert_item(Prototype.CopperOre, copper_furnace, copper_ore_count)
    print(f"Inserted {iron_ore_count} iron ore and {copper_ore_count} copper ore into furnaces")

    # Wait for smelting to complete (1 second per ore)
    smelting_time = max(iron_ore_count, copper_ore_count)
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    initial_copper_plates = inspect_inventory()[Prototype.CopperPlate]
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]

    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.IronPlate, iron_furnace.position, iron_ore_count)
        extract_item(Prototype.CopperPlate, copper_furnace.position, copper_ore_count)
        
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        
        if current_iron_plates - initial_iron_plates >= iron_ore_count and current_copper_plates - initial_copper_plates >= copper_ore_count:
            break
        sleep(5)

    print(f"Extracted {current_iron_plates} iron plates and {current_copper_plates} copper plates")

    # Verify that we have the correct number of plates in our inventory
    final_iron_plates = inspect_inventory()[Prototype.IronPlate]
    final_copper_plates = inspect_inventory()[Prototype.CopperPlate]
    
    assert final_iron_plates >= initial_iron_plates + iron_ore_count, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + iron_ore_count}, but got {final_iron_plates}"
    assert final_copper_plates >= initial_copper_plates + copper_ore_count, f"Failed to smelt enough copper plates. Expected at least {initial_copper_plates + copper_ore_count}, but got {final_copper_plates}"

    print(f"Successfully smelted {iron_ore_count} iron plates and {copper_ore_count} copper plates")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP


def mine_resources(resource: Resource, amount: int) -> None:
    """
    Objective: Mine the specified amount of resources
    Mining setup: No existing mining setup
    Inventory: Empty
    :param resource (Resource): The resource to mine (e.g., Resource.IronOre)
    :param amount (int): The amount of resource to mine
    :return: None
    """
    # [PLANNING]
    # 1. Find the nearest resource patch
    # 2. Move to the resource patch
    # 3. Harvest the required amount of resource
    # 4. Verify that we have mined the correct amount
    # [END OF PLANNING]

    # Find the nearest resource patch
    resource_position = nearest(resource)
    assert resource_position, f"No {resource} found nearby"
    print(f"Found {resource} at {resource_position}")

    # Move to the resource patch
    move_to(resource_position)
    print(f"Moved to {resource} patch at {resource_position}")

    # Get the resource patch details
    resource_patch = get_resource_patch(resource, resource_position, radius=10)
    assert resource_patch, f"No {resource} patch found within radius"
    print(f"Resource patch details: {resource_patch}")

    # Harvest the required amount of resource
    harvested = harvest_resource(resource_position, amount)
    print(f"Harvested {harvested} {resource}")

    # Verify that we have mined the correct amount
    inventory = inspect_inventory()
    mined_amount = inventory.get(resource, 0)
    assert mined_amount >= amount, f"Failed to mine enough {resource}. Expected {amount}, but got {mined_amount}"

    print(f"Successfully mined {mined_amount} {resource}")
    print(f"Current inventory: {inventory}")


###FUNC SEP

def craft_radar():
    """
    Objective: Craft one Radar. The final success should be checked by looking if a Radar is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft a Radar, we need:
    # - 5 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # - 5 iron gear wheels (each requiring 2 iron plates)
    # - 10 iron plates
    # 
    # Total raw materials needed:
    # - 30 iron plates (10 for radar + 10 for gear wheels + 5 for electronic circuits + 5 for copper cables)
    # - 15 copper plates (for electronic circuits)
    # 
    # We also need 15 coal for fuel and 5 stone for the furnace
    # We will craft 2 stone furnaces, one for iron and another one for copper
    # We need to harvest everything as we don't have any resources in our inventory
    # Steps:
    # 1. Mine iron ore and copper ore, stone and coal
    # 2. Craft 2 stone furnaces to smelt the ores
    # 3. Smelt iron plates and copper plates
    # 4. Craft copper cables
    # 5. Craft electronic circuits
    # 6. Craft iron gear wheels
    # 7. Finally, craft the radar
    # [END OF PLANNING]

    print("Starting to craft a Radar")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine necessary resources
    # We need 30 iron plates and 15 copper plates
    # We also need 15 coal for fuel and 5 stone for the furnace
    # Let's mine a bit extra to account for inefficiencies
    """[SYNTHESISED]
    # Name: mine_resources
    # Objective: Mine the specified amount of resources
    # Mining setup: No existing mining setup
    # Inventory: Empty
    # :param resource (Resource): The resource to mine (e.g., Resource.IronOre)
    # :param amount (int): The amount of resource to mine
    # :return: None
    [END OF SYNTHESISED]"""
    mine_resources(resource=Resource.IronOre, amount=35)
    mine_resources(resource=Resource.CopperOre, amount=20)
    mine_resources(resource=Resource.Stone, amount=15)
    mine_resources(resource=Resource.Coal, amount=10)

    # Step 2: Craft 2 stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 2, f"Failed to craft 2 stone furnaces. Expected 2, but got {furnace_count}"

    # Step 3: Smelt iron plates and copper plates
    """[SYNTHESISED]
    Name: smelt_plates
    Objective: Smelt the required number of iron and copper plates using two furnaces
    Mining setup: There are no entities on the map
    Inventory: We have iron ore, copper ore, and coal in the inventory. We also have 2 stone furnaces
    :param iron_ore_count (int): The number of iron ore to smelt
    :param copper_ore_count (int): The number of copper ore to smelt
    :param total_coal (int): The total amount of coal to be used for smelting
    :return: None
    [END OF SYNTHESISED]"""
    smelt_plates(iron_ore_count=30, copper_ore_count=15, total_coal=15)

    print(f"Plates smelted. Current inventory: {inspect_inventory()}")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 15)
    print(f"Copper cables crafted. Current inventory: {inspect_inventory()}")

    # Step 5: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 5)
    print(f"Electronic circuits crafted. Current inventory: {inspect_inventory()}")

    # Step 6: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 5)
    print(f"Iron gear wheels crafted. Current inventory: {inspect_inventory()}")

    # Step 7: Craft the radar
    craft_item(Prototype.Radar, 1)
    print(f"Radar crafted. Final inventory: {inspect_inventory()}")

    # Check if we have successfully crafted a Radar
    radar_count = inspect_inventory().get(Prototype.Radar, 0)
    assert radar_count >= 1, f"Failed to craft Radar. Expected at least 1, but got {radar_count}"

    print("Successfully crafted one Radar!")


###FUNC SEP

craft_radar()