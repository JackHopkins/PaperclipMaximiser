from factorio_instance import *


def smelt_copper_with_furnace(input_copper_ore: int, furnace: Entity):
    """
    Objective: Smelt copper ore into copper plates using a furnace
    Mining setup: We have a furnace on the map that we can use to smelt copper ore
    We have fueled the furnace with coal
    Inventory: We have enough copper ore in the inventory to smelt the copper plates
    :param input_copper_ore (int): The number of copper ore to insert into the furnace
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None as the copper plates will be in inventory
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore in the inventory
    # 2. Insert the copper ore into the furnace
    # 3. Wait for the smelting process to complete
    # 4. Extract the copper plates from the furnace
    # 5. Verify that we have the expected number of copper plates in our inventory
    # [END OF PLANNING]

    # Print initial inventory for logging
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough copper ore in the inventory
    copper_ore_in_inventory = inspect_inventory()[Prototype.CopperOre]
    assert copper_ore_in_inventory >= input_copper_ore, f"Not enough copper ore in inventory. Expected {input_copper_ore}, but got {copper_ore_in_inventory}"

    # Insert copper ore into the furnace
    insert_item(Prototype.CopperOre, furnace, input_copper_ore)
    print(f"Inserted {input_copper_ore} copper ore into the furnace")

    # Get the initial number of copper plates in the inventory
    initial_copper_plates = inspect_inventory()[Prototype.CopperPlate]

    # Wait for smelting to complete (1 second per ore)
    sleep(input_copper_ore)

    # Extract copper plates from the furnace
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, input_copper_ore)
        copper_plates_in_inventory = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_smelted = copper_plates_in_inventory - initial_copper_plates
        if copper_plates_smelted >= input_copper_ore:
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_smelted} copper plates from the furnace")

    # Verify that we have the expected number of copper plates in our inventory
    final_copper_plates = inspect_inventory()[Prototype.CopperPlate]
    copper_plates_produced = final_copper_plates - initial_copper_plates
    assert copper_plates_produced >= input_copper_ore, f"Failed to smelt enough copper plates. Expected {input_copper_ore}, but got {copper_plates_produced}"

    print(f"Successfully smelted {copper_plates_produced} copper plates")
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

def smelt_10_copper_plates():
    """
    Objective: Smelt 10 copper plates. The final success should be checked by looking if the copper plates are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Print initial inventory
    # 2. Mine the necessary resources. We need to mine everything from scratch as we have no resources in the inventory
    # 3. Craft a stone furnace
    # 4. Place the stone furnace
    # 5. Fuel the furnace with coal
    # 6. Smelt the copper ore into plates
    # 7. Check if we have 10 copper plates in the inventory
    # [END OF PLANNING]

    # Step 1: Print initial inventory
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Step 2: Mine necessary resources
    # We need 10 copper plates
    # We also need 5 coal for fuel and 5 stone for the furnace
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
    mine_resources(resource=Resource.CopperOre, amount=15)
    mine_resources(resource=Resource.Stone, amount=10)
    mine_resources(resource=Resource.Coal, amount=10)

    # Step 3: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print(f"Crafted 1 stone furnace")

    # Step 4: Place the stone furnace next to copper
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, copper_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Placed stone furnace at {furnace.position}")

    # Step 5: Fuel the furnace with coal
    insert_item(Prototype.Coal, furnace, 5)
    print("Inserted 5 coal into the furnace")

    # Step 6: Smelt the copper ore into plates
    # """[SYNTHESISED]
    # Name: smelt_copper_with_furnace
    # Objective: Smelt copper ore into copper plates using a furnace
    # Mining setup: We have a furnace on the map that we can use to smelt copper ore
    # We have fueled the furnace with coal
    # Inventory: We have enough copper ore in the inventory to smelt the copper plates
    # :param input_copper_ore (int): The number of copper ore to insert into the furnace
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None as the copper plates will be in inventory
    # [END OF SYNTHESISED]"""
    smelt_copper_with_furnace(input_copper_ore=15, furnace=furnace)
    
    # Step 7: Check if we have 10 copper plates in the inventory
    final_inventory = inspect_inventory()
    copper_plates = final_inventory[Prototype.CopperPlate]
    assert copper_plates >= 10, f"Failed to smelt enough copper plates. Expected at least 10, but got {copper_plates}"
    
    print(f"Successfully smelted {copper_plates} copper plates!")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP

smelt_10_copper_plates()