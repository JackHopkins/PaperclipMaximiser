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


def craft_gun_turret():
    """
    Objective: Craft one GunTurret. The final success should be checked by looking if a GunTurret is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for GunTurret. We need to mine everything as we don't have any resources in the inventory
    # 2. Mine necessary resources: iron ore and copper ore and coal for fuel
    # 3. Craft a stone furnace to smelt the ores
    # 4. Smelt iron plates and copper plates
    # 5. Craft iron gear wheels
    # 6. Craft the GunTurret
    # 7. Verify that the GunTurret is in the inventory
    # [END OF PLANNING]

    # Print initial inventory and recipe
    print(f"Initial inventory: {inspect_inventory()}")
    gun_turret_recipe = get_prototype_recipe(Prototype.GunTurret)
    print(f"GunTurret recipe: {gun_turret_recipe}")

    # Step 1: Mine necessary resources
    # We need 40 iron plates (20 for plates, 20 for gear wheels) and 10 copper plates
    # We also need 10 coal for fuel and 10 stone for the furnace
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
    mine_resources(resource=Resource.IronOre, amount=50)
    mine_resources(resource=Resource.CopperOre, amount=15)
    mine_resources(resource=Resource.Stone, amount=10)
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
    smelt_plates(ore_type=Prototype.IronOre, amount=40, furnace=furnace)
    smelt_plates(ore_type=Prototype.CopperOre, amount=10, furnace=furnace)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 10)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count == 10, f"Failed to craft iron gear wheels. Expected 10, but got {gear_count}"
    print("Crafted 10 iron gear wheels")

    # Step 5: Craft the GunTurret
    craft_item(Prototype.GunTurret, 1)

    # Step 6: Verify that the GunTurret is in the inventory
    gun_turret_count = inspect_inventory()[Prototype.GunTurret]
    assert gun_turret_count == 1, f"Failed to craft GunTurret. Expected 1, but got {gun_turret_count}"
    
    print("Successfully crafted 1 GunTurret!")
    print(f"Final inventory: {inspect_inventory()}")


###FUNC SEP

craft_gun_turret()