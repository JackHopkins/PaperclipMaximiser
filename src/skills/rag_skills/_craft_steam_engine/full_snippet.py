from factorio_instance import *


def smelt_iron_with_furnace(input_coal: int, input_iron_ore: int, furnace: Entity) -> None:
    """
    Smelt iron ore into iron plates using a furnace
    Mining setup: One unfueled stone furnace placed near iron ore. We need to insert coal for fuel
    Inventory: Contains iron ore and coal
    :param input_coal (int): Amount of coal to insert into the furnace
    :param input_iron_ore (int): Amount of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough iron ore and coal in the inventory
    # 2. Insert coal and iron ore into the furnace
    # 3. Wait for smelting to complete
    # 4. Extract iron plates from the furnace
    # 5. Verify that we have the expected amount of iron plates
    # [END OF PLANNING]

    print(f"Starting iron smelting process. Initial inventory: {inspect_inventory()}")

    # Check if we have enough iron ore and coal in the inventory
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= input_iron_ore, f"Not enough iron ore. Required: {input_iron_ore}, Available: {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.Coal] >= input_coal, f"Not enough coal. Required: {input_coal}, Available: {inventory[Prototype.Coal]}"

    # Insert coal and iron ore into the furnace
    insert_item(Prototype.Coal, furnace, input_coal)
    insert_item(Prototype.IronOre, furnace, input_iron_ore)
    print(f"Inserted {input_coal} coal and {input_iron_ore} iron ore into the furnace")

    # Wait for smelting to complete (iron ore smelts at a rate of 1 ore per 1 seconds)
    smelting_time = input_iron_ore * 1
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)

    # Extract iron plates from the furnace
    initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
    max_attempts = 5
    for attempt in range(max_attempts):
        extract_item(Prototype.IronPlate, furnace.position, input_iron_ore)
        current_iron_plates = inspect_inventory()[Prototype.IronPlate]
        iron_plates_extracted = current_iron_plates - initial_iron_plates
        
        if iron_plates_extracted >= input_iron_ore:
            break
        
        if attempt < max_attempts - 1:
            print(f"Extracted {iron_plates_extracted} iron plates. Waiting for more...")
            sleep(5)
    
    print(f"Extracted {iron_plates_extracted} iron plates from the furnace")

    # Verify that we have the expected amount of iron plates
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.IronPlate] >= initial_iron_plates + input_iron_ore, f"Failed to smelt enough iron plates. Expected at least {initial_iron_plates + input_iron_ore}, but got {final_inventory[Prototype.IronPlate]}"

    print(f"Successfully smelted {input_iron_ore} iron ore into iron plates")
    print(f"Final inventory: {final_inventory}")
    print("Iron smelting process completed successfully")


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


def craft_steam_engine():
    """
    Objective: Craft one SteamEngine. The final success should be checked by looking if a SteamEngine is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for SteamEngine
    # 2. Mine necessary resources: iron ore and stone
    # 3. Craft stone furnaces for smelting
    # 4. Smelt iron plates
    # 5. Craft iron gear wheels
    # 6. Craft pipes
    # 7. Finally, craft the steam engine
    # 8. Verify that the steam engine is in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    steam_engine_recipe = get_prototype_recipe(Prototype.SteamEngine)
    print(f"Steam Engine recipe: {steam_engine_recipe}")

    # Step 1: Mine necessary resources
    # We need iron for plates, gear wheels, and pipes, stone for furnaces and coal for fuel
    # In total we need 31 iron plates (5 pipes, 8 gear wheels and 10 plates)
    # We'll mine extra to account for inefficiencies
    """[SYNTHESISED]
    Name: mine_resources
    Objective: Mine the specified amount of resources
    Mining setup: No existing mining setup
    Inventory: Empty
    :param resource (Resource): The resource to mine (e.g., Resource.IronOre)
    :param amount (int): The amount of resource to mine
    :return: None
    [END OF SYNTHESISED]"""
    mine_resources(Resource.Stone, amount=10)
    mine_resources(Resource.IronOre, amount=40)
    mine_resources(Resource.Coal, amount=10)

    print(f"After mining resources: {inspect_inventory()}")

    # Step 2: Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnaces. Expected 1, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")

    # Step 3: Smelt iron plates
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    
    """[SYNTHESISED]
    Name: smelt_iron_with_furnace
    Objective: Smelt iron ore into iron plates using a furnace
    Mining setup: One unfueled stone furnace placed near iron ore. We need to insert coal for fuel
    Inventory: Contains iron ore and coal
    :param input_coal (int): Amount of coal to insert into the furnace
    :param input_iron_ore (int): Amount of iron ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None
    [END OF SYNTHESISED]"""
    smelt_iron_with_furnace(input_coal=10, input_iron_ore=40, furnace=furnace)

    iron_plates = inspect_inventory()[Prototype.IronPlate]
    assert iron_plates >= 40, f"Failed to smelt enough iron plates. Expected at least 40, but got {iron_plates}"
    print(f"Smelted {iron_plates} iron plates")

    # Step 4: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 8)
    gear_wheels = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_wheels >= 8, f"Failed to craft enough iron gear wheels. Expected 8, but got {gear_wheels}"
    print(f"Crafted {gear_wheels} iron gear wheels")

    # Step 5: Craft pipes
    craft_item(Prototype.Pipe, 5)
    pipes = inspect_inventory()[Prototype.Pipe]
    assert pipes >= 5, f"Failed to craft enough pipes. Expected 5, but got {pipes}"
    print(f"Crafted {pipes} pipes")

    # Step 6: Craft the steam engine
    craft_item(Prototype.SteamEngine, 1)
    steam_engine_count = inspect_inventory()[Prototype.SteamEngine]
    assert steam_engine_count == 1, f"Failed to craft steam engine. Expected 1, but got {steam_engine_count}"
    print("Successfully crafted 1 Steam Engine!")

    # Final inventory check
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    assert Prototype.SteamEngine in final_inventory and final_inventory[Prototype.SteamEngine] == 1, "Steam Engine not found in inventory"
    print("Objective completed: Crafted one Steam Engine and verified it's in the inventory.")


###FUNC SEP

craft_steam_engine()