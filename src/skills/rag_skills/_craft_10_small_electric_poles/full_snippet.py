from factorio_instance import *


def smelt_copper_plates(copper_ore_amount: int) -> None:
    """
    Objective: Smelt copper ore into copper plates using a stone furnace
    We also need to craft a stone furnace and put coal into the furnace for fuel
    Mining setup: No existing furnaces
    Inventory: Copper ore and some stone available
    :param copper_ore_amount (int): The amount of copper ore to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough copper ore and stone in the inventory
    # 2. Craft a stone furnace if we don't have one
    # 3. Place the stone furnace
    # 4. We need to mine coal as we don't have any in our inventory. Then insert coal into the furnace for fuel
    # 5. Insert copper ore into the furnace
    # 6. Wait for smelting to complete
    # 7. Extract copper plates from the furnace
    # 8. Verify that we have the correct amount of copper plates
    # [END OF PLANNING]

    print(f"Starting copper plate smelting process for {copper_ore_amount} copper ore")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough copper ore
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= copper_ore_amount, f"Not enough copper ore. Required: {copper_ore_amount}, Available: {inventory[Prototype.CopperOre]}"

    # Craft a stone furnace if we don't have one
    if inventory[Prototype.StoneFurnace] == 0:
        print("Crafting a stone furnace")
        assert inventory[Prototype.Stone] >= 5, f"Not enough stone to craft a furnace. Required: 5, Available: {inventory[Prototype.Stone]}"
        craft_item(Prototype.StoneFurnace, 1)
        print("Stone furnace crafted successfully")

    # Place the stone furnace
    furnace_position = Position(x=0, y=0)
    # Important: move to the furnace position
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"
    print(f"Stone furnace placed at {furnace.position}")

    # Insert coal into the furnace for fuel
    coal_needed = min(5, copper_ore_amount)  # Use 1 coal per 2 copper ore, minimum 5
    if inventory[Prototype.Coal] < coal_needed:
        coal_position = nearest(Resource.Coal)
        move_to(coal_position)
        harvest_resource(coal_position, coal_needed)
        print(f"Harvested {coal_needed} coal")

    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Inserted {coal_needed} coal into the furnace")

    # Insert copper ore into the furnace
    insert_item(Prototype.CopperOre, furnace, copper_ore_amount)
    print(f"Inserted {copper_ore_amount} copper ore into the furnace")

    # Wait for smelting to complete (1 second per ore)
    print(f"Waiting for smelting to complete...")
    sleep(copper_ore_amount)

    # Extract copper plates from the furnace
    initial_copper_plates = inventory[Prototype.CopperPlate]
    max_attempts = 5
    for _ in range(max_attempts):
        extract_item(Prototype.CopperPlate, furnace.position, copper_ore_amount)
        current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        copper_plates_produced = current_copper_plates - initial_copper_plates
        if copper_plates_produced >= copper_ore_amount:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    print(f"Extracted {copper_plates_produced} copper plates from the furnace")

    # Verify that we have the correct amount of copper plates
    final_inventory = inspect_inventory()
    assert final_inventory[Prototype.CopperPlate] >= initial_copper_plates + copper_ore_amount, f"Failed to smelt enough copper plates. Expected at least {copper_ore_amount}, but got {copper_plates_produced}"

    print(f"Successfully smelted {copper_plates_produced} copper plates")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP


def harvest_resources(resource: Resource, amount: int) -> None:
    """
    Harvest the specified amount of a given resource.
    
    :param resource (Resource): The resource to harvest (Resource enum)
    :param amount (int): The amount of resource to harvest
    :return: None
    """
    # [PLANNING]
    # 1. Find the nearest patch of the specified resource
    # 2. Move to the resource patch
    # 3. Harvest the resource
    # 4. Verify that we've harvested the correct amount
    # 5. Print the current inventory for logging purposes
    # [END OF PLANNING]

    # Step 1: Find the nearest patch of the specified resource
    resource_position = nearest(resource)
    assert resource_position, f"No {resource} found nearby"
    print(f"Found {resource} at position: {resource_position}")

    # Step 2: Move to the resource patch
    move_to(resource_position)
    print(f"Moved to {resource} patch at {resource_position}")

    # Step 3: Harvest the resource
    # We'll harvest a bit more than needed to account for any inefficiencies
    harvest_amount = int(amount * 1.2)
    harvested = harvest_resource(resource_position, harvest_amount)
    print(f"Attempted to harvest {harvest_amount} {resource}")

    # Step 4: Verify that we've harvested the correct amount
    inventory = inspect_inventory()
    actual_amount = inventory.get(resource, 0)
    assert actual_amount >= amount, f"Failed to harvest enough {resource}. Expected at least {amount}, but got {actual_amount}"

    # Step 5: Print the current inventory for logging purposes
    print(f"Successfully harvested {actual_amount} {resource}")
    print(f"Current inventory: {inventory}")

    # If we harvested more than needed, we can optionally inform the user
    if actual_amount > amount:
        print(f"Note: Harvested {actual_amount - amount} extra {resource}")


###FUNC SEP


def craft_10_small_electric_poles():
    """
    Objective: Craft 10 small electric poles. The final success should be checked by looking if 10 small electric poles are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for small electric poles
    # 2. Calculate the required resources (copper plates and wood). We do not have any resources in the inventory so we need to mine all of them
    # 3. Mine copper ore, harvest wood and harvest stone for the furnace
    # 4. Smelt copper ore into copper plates
    # 5. Craft copper cables
    # 6. Craft small electric poles
    # 7. Verify the crafting was successful
    # [END OF PLANNING]

    # Print initial inventory
    initial_inventory = inspect_inventory()
    print(f"Initial inventory: {initial_inventory}")

    # Step 1: Check the recipe for small electric poles
    pole_recipe = get_prototype_recipe(Prototype.SmallElectricPole)
    print(f"Small Electric Pole recipe: {pole_recipe}")

    # Step 2: Calculate required resources
    # We need to craft 10 poles, each requiring 1 copper plate and 1 wood
    required_copper_plates = 5  # (10 poles * 1 copper plate per 2 poles)
    required_wood = 10

    # Step 3: Mine copper ore and harvest wood
    # """[SYNTHESISED]
    # Name: harvest_resources
    # Objective: Harvest the specified amount of a given resource
    # Mining setup: No existing mining setup
    # Inventory: Empty
    # :param resource (Resource): The resource to harvest (Resource enum)
    # :param amount (int): The amount of resource to harvest
    # :return: None
    # [END OF SYNTHESISED]"""
    harvest_resources(Resource.CopperOre, required_copper_plates)
    harvest_resources(Resource.Wood, required_wood)
    harvest_resources(Resource.Stone, 5)  # For the furnace

    print(f"Current inventory after harvesting: {inspect_inventory()}")

    # Step 4: Smelt copper ore into copper plates
    # """[SYNTHESISED]
    # Name: smelt_copper_plates
    # Objective: Smelt copper ore into copper plates using a stone furnace
    # We also need to craft a stone furnace and put coal into the furnace for fuel
    # Mining setup: No existing furnaces
    # Inventory: Copper ore and some stone available
    # :param copper_ore_amount (int): The amount of copper ore to smelt
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_copper_plates(required_copper_plates)

    print(f"Current inventory after smelting: {inspect_inventory()}")

    # Step 5: Craft copper cables
    copper_cable_amount = required_copper_plates * 2  # Each copper plate produces 2 copper cables
    craft_item(Prototype.CopperCable, copper_cable_amount)

    print(f"Current inventory after crafting copper cables: {inspect_inventory()}")

    # Step 6: Craft small electric poles
    craft_item(Prototype.SmallElectricPole, 10)

    # Step 7: Verify the crafting was successful
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")

    crafted_poles = final_inventory.get(Prototype.SmallElectricPole, 0)
    assert crafted_poles >= 10, f"Failed to craft 10 small electric poles. Crafted: {crafted_poles}"

    print("Successfully crafted 10 small electric poles!")


###FUNC SEP

craft_10_small_electric_poles()