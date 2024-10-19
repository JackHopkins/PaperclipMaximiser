from factorio_instance import *


def harvest_resources(resource: Resource, amount: int) -> None:
    """
    Harvest the specified amount of a given resource.
    
    Objective: Harvest the specified amount of a given resource
    Mining setup: No existing mining setup
    Inventory: Empty
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

def smelt_resource(resource: Resource, quantity: int, furnace: Entity) -> None:
    """
    Objective: Smelt a resource into plates
    Mining setup: A fueled furnace is available
    Inventory: Inventory has the copper or iron ore needed for smelting
    :param resource (Resource): The resource to smelt (Resource.CopperOre or Resource.IronOre)
    :param quantity (int): The number of plates to produce
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Determine the corresponding plate type and furnace recipe
    # 2. Smelt the ore into plates
    # 3. Verify the correct number of plates have been produced
    # [END OF PLANNING]

    # Step 1: Determine the corresponding plate type and furnace recipe
    if resource == Resource.CopperOre:
        plate_type = Prototype.CopperPlate
        ore_type = Prototype.CopperOre
    elif resource == Resource.IronOre:
        plate_type = Prototype.IronPlate
        ore_type = Prototype.IronOre
    else:
        raise ValueError("Invalid resource type. Must be CopperOre or IronOre.")

    print(f"Starting to mine and smelt {quantity} {plate_type.value[0]}s")
    print(f"Initial inventory: {inspect_inventory()}")
    
    # Step 2: Smelt the ore into plates
    insert_item(ore_type, furnace, quantity)
    print(f"Inserted and {quantity} {ore_type.value[0]} into the furnace")

    # Wait for smelting to complete
    sleep(quantity * 0.7)  # Assuming it takes about 0.7 seconds to smelt each ore

    # Step 3: Verify the correct number of plates have been produced
    max_attempts = 5
    plates_extracted = 0
    for _ in range(max_attempts):
        extract_item(plate_type, furnace.position, quantity - plates_extracted)
        plates_in_inventory = inspect_inventory()[plate_type]
        if plates_in_inventory >= quantity:
            plates_extracted = plates_in_inventory
            break
        sleep(5)  # Wait a bit more if not all plates are ready

    assert plates_extracted >= quantity, f"Failed to smelt enough {plate_type.value[0]}s. Expected {quantity}, but got {plates_extracted}"
    print(f"Successfully mined and smelted {plates_extracted} {plate_type.value[0]}s")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP


def craft_20_electronic_circuits():
    """
    Objective: Craft 20 electronic circuits. The final success should be checked by looking if 10 electronic circuits are in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for electronic circuits
    # 2. Calculate the required resources (copper plates and iron plates)
    # 3. Mine the necessary copper ore and iron ore. We will need to mine all of the resources as we don't have any in our inventory
    # Also mine coal and stone for the furnace and smelting
    # 4. Craft a stone furnace to smelt the ores
    # 5. Smelt copper plates and iron plates
    # 6. Craft copper cables
    # 7. Craft the electronic circuits
    # 8. Verify the success of the operation
    # [END OF PLANNING]

    # Print initial inventory
    print(f"Initial inventory: {inspect_inventory()}")

    # Check the recipe for electronic circuits
    circuit_recipe = get_prototype_recipe(Prototype.ElectronicCircuit)
    print(f"Electronic circuit recipe: {circuit_recipe}")

    # Calculate required resources
    copper_plates_needed = 20 * 2  # 2 copper plates per circuit (3 cables = 1.5 plates, rounded up to 2)
    iron_plates_needed = 20 * 1   # 1 iron plate per circuit

    # Mine the necessary resources
    # We need to mine iron, copper, stone and coal
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
    harvest_resources(Resource.CopperOre, copper_plates_needed)
    harvest_resources(Resource.IronOre, iron_plates_needed)
    
    # mine coal and stone for furnace
    harvest_resources(Resource.Coal, 5)
    harvest_resources(Resource.Stone, 5)

    # craft and fuel the furnace
    furnace = craft_item(Prototype.StoneFurnace, 1)
    # put the furnace near the stone
    furnace_position = nearest(Resource.Stone)
    # move to the furnace position
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, position=furnace_position)

    # put the coal into the furnace
    insert_item(Prototype.Coal, furnace, 5)

    # """[SYNTHESISED]
    # Name: smelt_resource
    # Objective: Smelt a resource into plates. Use the furnace variable
    # Mining setup: A fueled furnace is available
    # Inventory: Inventory has the copper or iron ore needed for smelting
    # :param resource (Resource): The resource to smelt (Resource.CopperOre or Resource.IronOre)
    # :param quantity (int): The number of plates to produce
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None
    # [END OF SYNTHESISED]"""
    smelt_resource(resource=Resource.CopperOre, quantity=copper_plates_needed, furnace = furnace)
    smelt_resource(resource=Resource.IronOre, quantity=iron_plates_needed, furnace = furnace)

    print(f"Inventory after mining and smelting: {inspect_inventory()}")

    # Craft copper cables
    copper_cables_needed = 20 * 3  # 3 copper cables per circuit
    craft_item(Prototype.CopperCable, copper_cables_needed // 2)  # Crafting produces 2 cables at a time
    
    print(f"Inventory after crafting copper cables: {inspect_inventory()}")

    # Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 20)

    # Verify the success of the operation
    final_inventory = inspect_inventory()
    print(f"Final inventory: {final_inventory}")
    
    circuits_crafted = final_inventory.get(Prototype.ElectronicCircuit, 0)
    assert circuits_crafted >= 20, f"Failed to craft 20 electronic circuits. Only crafted {circuits_crafted}"
    
    print("Successfully crafted 20 electronic circuits!")



###FUNC SEP

craft_20_electronic_circuits()