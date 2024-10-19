from factorio_instance import *


def smelt_plates(copper_plates_needed: int, iron_plates_needed: int):
    """
    Objective: Smelt copper and iron plates using the stone furnace.
    We need to put down the furnace from inventory and fuel it as well
    Mining setup: There are no entities on the map
    Inventory: Raw ores, coal and a furnace available
    :param copper_plates_needed (int): Number of copper plates to smelt
    :param iron_plates_needed (int): Number of iron plates to smelt
    :return: None (plates will be added to inventory)
    """
    # [PLANNING]
    # 1. Place the stone furnace
    # 2. add in existing coal
    # 3. Smelt copper plates
    # 4. Smelt iron plates
    # 5. Verify the smelted plates are in the inventory
    # [END OF PLANNING]

    print(f"Starting to smelt {copper_plates_needed} copper plates and {iron_plates_needed} iron plates")
    print(f"Initial inventory: {inspect_inventory()}")

    # Place the stone furnace
    furnace_position = nearest(Resource.Stone)
    move_to(furnace_position)
    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)
    assert furnace, "Failed to place stone furnace"

    # add in existing coal
    coal_needed_in_inventory = inspect_inventory().get(Prototype.Coal, 0)
    assert coal_needed_in_inventory >= 0, "No coal in inventory"
    # place the coal in the furnace
    insert_item(Prototype.Coal, furnace, coal_needed_in_inventory)

    # check that we have the required amount of copper and iron ore
    inventory = inspect_inventory()
    assert inventory[Prototype.CopperOre] >= copper_plates_needed, f"Not enough copper ore. Required: {copper_plates_needed}, Available: {inventory[Prototype.CopperOre]}"
    assert inventory[Prototype.IronOre] >= iron_plates_needed, f"Not enough iron ore. Required: {iron_plates_needed}, Available: {inventory[Prototype.IronOre]}"

    # Smelt copper plates
    if copper_plates_needed > 0:
        print(f"Smelting {copper_plates_needed} copper plates")
        insert_item(Prototype.CopperOre, furnace, copper_plates_needed)
        sleep(copper_plates_needed)  # Wait for smelting (1 second per ore)

        max_attempts = 5
        # get the initial number of copper plates in the inventory
        initial_copper_plates = inspect_inventory()[Prototype.CopperPlate]
        for _ in range(max_attempts):
            extract_item(Prototype.CopperPlate, furnace.position, copper_plates_needed)
            current_copper_plates = inspect_inventory()[Prototype.CopperPlate]
            copper_plates_produced = current_copper_plates - initial_copper_plates
            if copper_plates_produced >= copper_plates_needed:
                break
            sleep(2)
        

    # Smelt iron plates
    if iron_plates_needed > 0:
        print(f"Smelting {iron_plates_needed} iron plates")
        insert_item(Prototype.IronOre, furnace, iron_plates_needed)
        sleep(iron_plates_needed)  # Wait for smelting (1 second per ore)
        max_attempts = 5
        # get the initial number of irom plates in the inventory
        initial_iron_plates = inspect_inventory()[Prototype.IronPlate]
        for _ in range(max_attempts):
            extract_item(Prototype.IronPlate, furnace.position, iron_plates_needed)
            current_iron_plates = inspect_inventory()[Prototype.IronPlate]
            iron_plates_produced = current_iron_plates - initial_iron_plates
            if iron_plates_produced >= iron_plates_needed:
                break
            sleep(2)

    # Verify the smelted plates are in the inventory
    final_inventory = inspect_inventory()
    copper_plates_smelted = final_inventory[Prototype.CopperPlate] - inventory[Prototype.CopperPlate]
    iron_plates_smelted = final_inventory[Prototype.IronPlate] - inventory[Prototype.IronPlate]

    print(f"Smelted {copper_plates_smelted} copper plates and {iron_plates_smelted} iron plates")
    assert copper_plates_smelted >= copper_plates_needed, f"Failed to smelt enough copper plates. Needed {copper_plates_needed}, smelted {copper_plates_smelted}"
    assert iron_plates_smelted >= iron_plates_needed, f"Failed to smelt enough iron plates. Needed {iron_plates_needed}, smelted {iron_plates_smelted}"

    print("Successfully smelted all required plates!")
    print(f"Final inventory: {final_inventory}")


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


def craft_lab():
    """
    Objective: Craft one Lab. The final success should be checked by looking if a Lab is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # To craft a Lab, we need:
    # - 10 electronic circuits (each requiring 3 copper cables and 1 iron plate)
    # - 10 iron gear wheels (each requiring 2 iron plates)
    # - 4 transport belts (each requiring 1 iron gear wheel and 1 iron plate)
    # 
    # Total raw materials needed:
    # - 15 copper plates (for electronic circuits)
    # - 36 iron plates (for electronic circuits, iron gear wheels, and transport belts)
    # - 5 stone (for a stone furnace to smelt the plates)
    # 
    # Steps:
    # 1. Mine raw resources (copper ore, iron ore, stone, coal)
    # We need to mine everything as we don't have any resources in the inventory
    # 2. Craft stone furnace
    # 3. Smelt copper and iron plates
    # 4. Craft copper cables
    # 5. Craft electronic circuits
    # 6. Craft iron gear wheels
    # 7. Craft transport belts
    # 8. Finally, craft the Lab
    # [END OF PLANNING]

    print("Starting to craft a Lab from scratch.")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine necessary resources
    # We need 36 iron plates and 15 copper plates and 5 stone for the furnace
    # We also need 15 coal for fuel 
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
    mine_resources(resource=Resource.IronOre, amount=45)
    mine_resources(resource=Resource.CopperOre, amount=20)
    mine_resources(resource=Resource.Stone, amount=10)
    mine_resources(resource=Resource.Coal, amount=20)

    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft stone furnace
    craft_item(Prototype.StoneFurnace, 1)
    assert inspect_inventory()[Prototype.StoneFurnace] >= 1, "Failed to craft stone furnace"
    print("Crafted 1 stone furnace")

    # Step 3: Smelt copper and iron plates
    """[SYNTHESISED]
    Name: smelt_plates
    Objective: Smelt copper and iron plates using the stone furnace.
    We need to put down the furnace from inventory and fuel it
    Mining setup: There are no entities on the map
    Inventory: Raw ores, coal and a furnace available
    :param copper_plates_needed (int): Number of copper plates to smelt
    :param iron_plates_needed (int): Number of iron plates to smelt
    :return: None (plates will be added to inventory)
    [END OF SYNTHESISED]"""
    smelt_plates(copper_plates_needed=15, iron_plates_needed=36)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft copper cables
    craft_item(Prototype.CopperCable, 30)  # We need 30 copper cables for 10 electronic circuits
    assert inspect_inventory()[Prototype.CopperCable] >= 30, "Failed to craft enough copper cables"
    print("Crafted 30 copper cables")

    # Step 5: Craft electronic circuits
    craft_item(Prototype.ElectronicCircuit, 10)
    assert inspect_inventory()[Prototype.ElectronicCircuit] >= 10, "Failed to craft enough electronic circuits"
    print("Crafted 10 electronic circuits")

    # Step 6: Craft iron gear wheels
    craft_item(Prototype.IronGearWheel, 14)  # 10 for the Lab, 4 for transport belts
    assert inspect_inventory()[Prototype.IronGearWheel] >= 14, "Failed to craft enough iron gear wheels"
    print("Crafted 14 iron gear wheels")

    # Step 7: Craft transport belts
    craft_item(Prototype.TransportBelt, 4)
    assert inspect_inventory()[Prototype.TransportBelt] >= 4, "Failed to craft enough transport belts"
    print("Crafted 4 transport belts")

    # Step 8: Craft the Lab
    craft_item(Prototype.Lab, 1)
    lab_count = inspect_inventory()[Prototype.Lab]
    assert lab_count >= 1, f"Failed to craft a Lab. Current count: {lab_count}"
    print("Successfully crafted 1 Lab!")

    print(f"Final inventory: {inspect_inventory()}")
    print("Lab crafting process completed successfully.")


###FUNC SEP

craft_lab()