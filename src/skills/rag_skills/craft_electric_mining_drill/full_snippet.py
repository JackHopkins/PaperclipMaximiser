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

def craft_electric_mining_drill():
    """
    Objective: We need to craft one electric mining drill
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Gather raw resources: iron ore, copper ore, coal, and stone
    # We need to mine everything from scratch as we have no resources in the inventory
    # 2. Craft 2 stone furnaces, one for iron plates and one for copper plates
    # 3. Smelt iron plates
    # 4. Smelt copper plates
    # 5. Craft intermediate components: iron gear wheels, copper cables, and electronic circuits
    # 6. Craft the electric mining drill
    # 7. Verify the electric mining drill is in the inventory
    # [END OF PLANNING]

    print("Starting to craft an electric mining drill")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Gather raw resources
    resources_to_mine = [
        (Resource.IronOre, 25), # We need at least 25 iron ore for the plates
        (Resource.CopperOre, 10), # We need at least 10 copper ore for the plates
        (Resource.Coal, 15), # We need at least 15 coal for smelting
        (Resource.Stone, 10) # We need at least 10 stone for crafting the 2 furnaces
    ]

    for resource, amount in resources_to_mine:
        resource_position = nearest(resource)
        move_to(resource_position)
        harvest_resource(resource_position, amount)
        current_amount = inspect_inventory()[resource]
        assert current_amount >= amount, f"Failed to mine enough {resource}. Expected {amount}, but got {current_amount}"
        print(f"Mined {current_amount} {resource}")

    print(f"Current inventory after mining: {inspect_inventory()}")

    # Step 2: Craft 2 stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 2, f"Failed to craft 2 stone furnaces. Expected 2, but got {furnace_count}"
    print("Crafted 2 stone furnaces")

    # Step 3-4: Smelt the iron and copper plates
    # """[SYNTHESISED] 
    # Name: smelt_plates
    # Objective: Smelt the required number of iron and copper plates using two furnaces
    # Mining setup: There are no entities on the map
    # Inventory: We have iron ore, copper ore, and coal in the inventory. We also have 2 stone furnaces
    # :param iron_ore_count (int): The number of iron ore to smelt
    # :param copper_ore_count (int): The number of copper ore to smelt
    # :param total_coal (int): The total amount of coal to be used for smelting
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_plates(iron_ore_count=23, copper_ore_count=5, total_coal=15)

    print(f"Current inventory after smelting: {inspect_inventory()}")

    # Step 5: Craft intermediate components
    craft_item(Prototype.IronGearWheel, 5)
    craft_item(Prototype.CopperCable, 9)
    craft_item(Prototype.ElectronicCircuit, 3)

    print(f"Current inventory after crafting components: {inspect_inventory()}")

    # Step 6: Craft the electric mining drill
    craft_item(Prototype.ElectricMiningDrill, 1)

    # Step 7: Verify the electric mining drill is in the inventory
    drill_count = inspect_inventory()[Prototype.ElectricMiningDrill]
    assert drill_count == 1, f"Failed to craft electric mining drill. Expected 1, but got {drill_count}"
    print("Successfully crafted 1 electric mining drill!")
    print(f"Final inventory: {inspect_inventory()}")

    return True
###FUNC SEP

craft_electric_mining_drill()
