from factorio_instance import *


def smelt_plates(ore_type: Prototype, amount: int, furnace: Entity) -> None:
    """
    Smelt the specified amount of plates using a stone furnace.
    Mining setup: One stone furnace available. Coal has already been added to the furnace for fuel
    Inventory: Contains iron ore, copper ore, and stone furnace
    :param ore_type (Prototype): The type of ore to smelt (e.g., Prototype.IronOre)
    :param amount (int): The amount of plates to smelt
    :param furnace (Entity): The furnace entity to use for smelting
    :return: None
    """
    # [PLANNING]
    # 1. Determine the corresponding plate type based on the ore type
    # 2. Check if we have enough ore in the inventory
    # 3. Place the stone furnace if not already placed
    # 4. Insert ore into the furnace
    # 5. Wait for smelting to complete
    # 6. Extract the plates from the furnace
    # 7. Verify that we have the correct amount of plates in the inventory
    # [END OF PLANNING]

    # Determine the corresponding plate type
    if ore_type == Prototype.IronOre:
        plate_type = Prototype.IronPlate
    elif ore_type == Prototype.CopperOre:
        plate_type = Prototype.CopperPlate
    else:
        raise ValueError(f"Unsupported ore type: {ore_type}")

    print(f"Starting to smelt {amount} {plate_type} from {ore_type}")
    
    # Check if we have enough ore in the inventory
    initial_ore_count = inspect_inventory()[ore_type]
    assert initial_ore_count >= amount, f"Not enough {ore_type} in inventory. Need {amount}, have {initial_ore_count}"
    
    # move to the furnace position
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Insert ore into the furnace
    insert_item(ore_type, furnace, amount)
    print(f"Inserted {amount} {ore_type} into the furnace")

    # Wait for smelting to complete (1 second per ore)
    sleep(amount)
    print(f"Waiting {amount} seconds for smelting to complete")

    # Extract the plates from the furnace
    initial_plate_count = inspect_inventory()[plate_type]
    extract_item(plate_type, furnace.position, amount)
    
    # Verify that we have the correct amount of plates in the inventory
    final_plate_count = inspect_inventory()[plate_type]
    plates_smelted = final_plate_count - initial_plate_count
    assert plates_smelted >= amount, f"Failed to smelt enough plates. Expected {amount}, but got {plates_smelted}"
    
    print(f"Successfully smelted {plates_smelted} {plate_type}")
    print(f"Current inventory: {inspect_inventory()}")


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

def craft_offshore_pump():
    """
    Objective: Craft one OffshorePump. The final success should be checked by looking if a OffshorePump is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft an OffshorePump, we need:
    # 1. 2 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # 2. 1 iron gear wheel (requiring 2 iron plates)
    # 3. 1 pipe (requiring 1 iron plate)
    # In total, we need to mine and craft:
    # - 5 iron ore (for 5 iron plates)
    # - 3 copper ore (for 3 copper plates)
    # We'll mine a bit extra to account for any inefficiencies.
    # We also need 5 coal for fuel and 5 stone for the furnace

    # Step 1 - First we'll mine the necessary resources. We need to mine everything as we don't have any resources in the inventory
    # Step 2 - Then we'll craft the furnace and fuel it
    # Step 3 - Next, we'll smelt the iron plates and copper plates
    # Step 4 - After that, we'll craft the copper cables, electronic circuits, iron gear wheel, and pipe  
    # [END OF PLANNING]

    print("Starting to craft an OffshorePump")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine necessary resources
    # We need 5 iron plates and 3 copper plates
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
    mine_resources(resource=Resource.IronOre, amount=7)
    mine_resources(resource=Resource.CopperOre, amount=5)
    mine_resources(resource=Resource.Stone, amount=5)
    mine_resources(resource=Resource.Coal, amount=10)


    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft a stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count == 1, f"Failed to craft stone furnace. Expected 1, but got {furnace_count}"
    print("Crafted 1 stone furnace")

    # place and fuel the furnace
    furnace_pos = Position(x=0, y=0)  # Put the furnace at the origin
    # move to the furnace position
    move_to(furnace_pos)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_pos)

    # add enough coal to the furnace for the copper and iron plates
    insert_item(Prototype.Coal, furnace, 10)
    print("Inserted 10 coal into the furnace")

    # Step 3: Smelt iron plates and copper plates
    """[SYNTHESISED]
    # Name: smelt_plates
    # Objective: Smelt the specified amount of plates
    # Mining setup: One stone furnace available. Coal has already been added to the furnace for fuel
    # Inventory: Contains iron ore and copper ore
    # :param ore_type (Prototype): The type of ore to smelt (e.g., Prototype.IronOre)
    # :param amount (int): The amount of plates to smelt
    # :param furnace (Entity): The furnace entity to use for smelting
    # :return: None
    [END OF SYNTHESISED]"""
    smelt_plates(ore_type=Prototype.IronOre, amount=7, furnace=furnace)
    smelt_plates(ore_type=Prototype.CopperOre, amount=5, furnace=furnace)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 5: Craft copper cables
    craft_item(Prototype.CopperCable, 6)
    copper_cable_count = inspect_inventory()[Prototype.CopperCable]
    assert copper_cable_count >= 6, f"Failed to craft enough copper cables. Expected 6, got {copper_cable_count}"
    print(f"Crafted {copper_cable_count} copper cables")

    # Step 6: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 2)
    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
    assert circuit_count >= 2, f"Failed to craft enough electronic circuits. Expected 2, got {circuit_count}"
    print(f"Crafted {circuit_count} electronic circuits")

    # Step 7: Craft iron gear wheel
    craft_item(Prototype.IronGearWheel, 1)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count >= 1, f"Failed to craft iron gear wheel. Expected 1, got {gear_count}"
    print(f"Crafted {gear_count} iron gear wheel")

    # Step 8: Craft pipe
    craft_item(Prototype.Pipe, 1)
    pipe_count = inspect_inventory()[Prototype.Pipe]
    assert pipe_count >= 1, f"Failed to craft pipe. Expected 1, got {pipe_count}"
    print(f"Crafted {pipe_count} pipe")

    # Step 9: Craft OffshorePump
    craft_item(Prototype.OffshorePump, 1)
    pump_count = inspect_inventory()[Prototype.OffshorePump]
    assert pump_count >= 1, f"Failed to craft OffshorePump. Expected 1, got {pump_count}"
    print(f"Successfully crafted {pump_count} OffshorePump")

    print(f"Final inventory: {inspect_inventory()}")
    print("Objective completed: Crafted one OffshorePump")


###FUNC SEP

craft_offshore_pump()