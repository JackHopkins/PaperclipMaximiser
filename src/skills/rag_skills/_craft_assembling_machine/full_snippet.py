from factorio_instance import *


def smelt_ore(furnace: Entity, ore_type: str, amount: int, coal_needed: int) -> None:
    """
    Objective: Smelt ore into plates using a furnace. 
    Mining setup: A furnace is placed on the map. The furnace has not been fueled
    Inventory: We have ore and coal in the inventory
    :param furnace (entity): The furnace entity to use for smelting
    :param ore_type (Resource.IronOre ore Resource.CopperOre): The type of ore to smelt (iron or copper)
    :param amount (int): The amount of ore to smelt
    :param coal_needed (int): The amount of coal needed for smelting
    :return: None
    """
    # [PLANNING]
    # 2. Check inventory for required resources
    # 3. Insert coal into the furnace
    # 4. Insert ore into the furnace
    # 5. Wait for smelting to complete
    # 6. Extract plates from the furnace
    # 7. Verify the smelting process was successful
    # [END OF PLANNING]


    # Step 2: Check inventory for required resources
    inventory = inspect_inventory()
    ore_prototype = Prototype.IronOre if ore_type == Resource.IronOre else Prototype.CopperOre
    plate_prototype = Prototype.IronPlate if ore_type == Resource.IronOre else Prototype.CopperPlate
    
    print(f"Current inventory: {inventory}")
    assert inventory[ore_prototype] >= amount, f"Not enough {ore_type} ore in inventory. Required: {amount}, Available: {inventory[ore_prototype]}"

    # move to furnace position
    move_to(furnace.position)
    print(f"Moved to furnace at position {furnace.position}")

    # Step 3: Insert coal into the furnace
    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Inserted {coal_needed} coal into the furnace")

    # Step 4: Insert ore into the furnace
    insert_item(ore_prototype, furnace, amount)
    print(f"Inserted {amount} {ore_type} ore into the furnace")

    # Step 5: Wait for smelting to complete
    # Wait for smelting to complete (assuming 1 seconds per iron plate)
    smelting_time = amount * 1
    print(f"Waiting {smelting_time} seconds for smelting to complete")
    sleep(smelting_time)
    max_attempts = 5
    # get the initial number of irom plates in the inventory
    initial_plates = inspect_inventory()[plate_prototype]
    for _ in range(max_attempts):
        extract_item(plate_prototype, furnace.position, amount)
        current_plates = inspect_inventory()[plate_prototype]
        plates_produced = current_plates - initial_plates
        if plates_produced >= amount:
            break
        sleep(2)  # Wait a bit more if not all plates are ready

    # Step 7: Verify the smelting process was successful
    final_inventory = inspect_inventory()
    plates_produced = final_inventory[plate_prototype] - initial_plates
    print(f"Plates produced: {plates_produced}")
    assert plates_produced == amount, f"Failed to produce the expected number of plates. Expected: {amount}, Produced: {plates_produced}"

    print(f"Successfully smelted {amount} {ore_type} ore into {plates_produced} {ore_type} plates")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP


def mine_resources(iron_amount: int, 
                   copper_amount: int, 
                   stone_amount: int,
                   coal_amount: int) -> None:
    """
    Mine iron ore, copper ore, and stone and coal for fuel
    :param iron_amount (int): Amount of iron ore to mine
    :param copper_amount (int): Amount of copper ore to mine
    :param stone_amount (int): Amount of stone to mine
    :param coal_amount (int): Amount of coal to mine
    :return: None
    """
    # [PLANNING]
    # 1. Find and mine iron ore
    # 2. Find and mine copper ore
    # 3. Find and mine stone
    # 4. Verify that we have mined the correct amounts
    # [END OF PLANNING]

    print(f"Starting mining operation. Target amounts - Iron: {iron_amount}, Copper: {copper_amount}, Stone: {stone_amount}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Mine iron ore
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    print(f"Moving to iron ore patch at {iron_position}")
    iron_mined = harvest_resource(iron_position, iron_amount)
    print(f"Mined {iron_mined} iron ore")

    # Mine copper ore
    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    print(f"Moving to copper ore patch at {copper_position}")
    copper_mined = harvest_resource(copper_position, copper_amount)
    print(f"Mined {copper_mined} copper ore")

    # Mine stone
    stone_position = nearest(Resource.Stone)
    move_to(stone_position)
    print(f"Moving to stone patch at {stone_position}")
    stone_mined = harvest_resource(stone_position, stone_amount)
    print(f"Mined {stone_mined} stone")

    # Mine coal
    coal_position = nearest(Resource.Coal)
    move_to(coal_position)
    print(f"Moving to coal patch at {coal_position}")
    coal_mined = harvest_resource(coal_position, coal_amount)
    print(f"Mined {coal_mined} coal")

    # Verify mined amounts
    inventory = inspect_inventory()
    iron_in_inventory = inventory.get(Resource.IronOre, 0)
    copper_in_inventory = inventory.get(Resource.CopperOre, 0)
    stone_in_inventory = inventory.get(Resource.Stone, 0)
    coal_in_inventory = inventory.get(Resource.Coal, 0)

    print(f"Final inventory: {inventory}")

    assert iron_in_inventory >= iron_amount, f"Failed to mine enough iron ore. Expected {iron_amount}, but got {iron_in_inventory}"
    assert copper_in_inventory >= copper_amount, f"Failed to mine enough copper ore. Expected {copper_amount}, but got {copper_in_inventory}"
    assert stone_in_inventory >= stone_amount, f"Failed to mine enough stone. Expected {stone_amount}, but got {stone_in_inventory}"
    assert coal_in_inventory >= coal_amount, f"Failed to mine enough coal. Expected {coal_amount}, but got {coal_in_inventory}"

    print(f"Successfully mined {iron_in_inventory} iron ore, {copper_in_inventory} copper ore, {coal_in_inventory} coal and {stone_in_inventory} stone.")


###FUNC SEP


def craft_assembling_machine():
    """
    Objective: Craft one AssemblingMachine1. The final success should be checked by looking if a AssemblingMachine is in inventory
    Mining setup: There are no entities on the map
    Inventory: {}
    """
    # [PLANNING]
    # 1. Check the recipe for AssemblingMachine1
    # 2. Mine necessary resources: iron ore, copper ore, stonefor a furnace and coal for fuel. We need to mine everything as we don't have any resources in the inventory
    # 3. Craft stone furnaces for smelting
    # 4. Smelt iron plates and copper plates
    # 5. Craft intermediate products: iron gear wheels, electronic circuits
    # 6. Craft the AssemblingMachine1
    # 7. Verify success by checking inventory
    # [END OF PLANNING]

    # Print initial information
    assembling_machine_recipe = get_prototype_recipe(Prototype.AssemblingMachine1)
    print(f"AssemblingMachine recipe: {assembling_machine_recipe}")
    print(f"Initial inventory: {inspect_inventory()}")

    # Step 1: Mine necessary resources
    # We need more than required to account for inefficiencies
    # We also need coal, 5 for iron plates and 5 for copper plates
    """[SYNTHESISED]
    Name: mine_resources
    Objective: Mine iron ore, copper ore, and stone and coal
    Mining setup: No entities on the map
    Inventory: Empty inventory
    :param iron_amount (int): Amount of iron ore to mine
    :param copper_amount (int): Amount of copper ore to mine
    :param stone_amount (int): Amount of stone to mine
    :param coal_amount (int): Amount of coal to mine
    :return: None
    [END OF SYNTHESISED]"""
    mine_resources(iron_amount=35, copper_amount=10, stone_amount=10, coal_amount=10)

    print(f"Inventory after mining: {inspect_inventory()}")

    # Step 2: Craft stone furnaces
    craft_item(Prototype.StoneFurnace, 2)
    furnace_count = inspect_inventory()[Prototype.StoneFurnace]
    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"
    print(f"Crafted {furnace_count} stone furnaces")

    # Step 3: Smelt iron plates and copper plates
    iron_position = nearest(Resource.IronOre)
    move_to(iron_position)
    furnace_iron = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
    
    """[SYNTHESISED]
    Name: smelt_ore
    Objective: Smelt ore into plates using a furnace
    Mining setup: A furnace is placed on the map. The furnace has not been fueled
    Inventory: We have ore and coal in the inventory
    :param furnace (Entity): The furnace entity to use for smelting
    :param ore_type (Resource.IronOre ore Resource.CopperOre): The type of ore to smelt (iron or copper)
    :param amount (int): The amount of ore to smelt
    :param coal_needed (int): The amount of coal needed for smelting
    :return: None
    [END OF SYNTHESISED]"""
    smelt_ore(furnace=furnace_iron, ore_type=Resource.IronOre, amount=30,
              coal_needed=5)

    copper_position = nearest(Resource.CopperOre)
    move_to(copper_position)
    furnace_copper = place_entity(Prototype.StoneFurnace, Direction.UP, copper_position)
    smelt_ore(furnace=furnace_copper, ore_type=Resource.CopperOre, amount=10, coal_needed=5)

    print(f"Inventory after smelting: {inspect_inventory()}")

    # Step 4: Craft intermediate products
    craft_item(Prototype.IronGearWheel, 5)
    gear_count = inspect_inventory()[Prototype.IronGearWheel]
    assert gear_count >= 5, f"Failed to craft iron gear wheels. Expected 5, but got {gear_count}"
    print(f"Crafted {gear_count} iron gear wheels")

    craft_item(Prototype.ElectronicCircuit, 3)
    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]
    assert circuit_count >= 3, f"Failed to craft electronic circuits. Expected 3, but got {circuit_count}"
    print(f"Crafted {circuit_count} electronic circuits")

    # Step 5: Craft the AssemblingMachine
    craft_item(Prototype.AssemblingMachine1, 1)
    
    # Verify success
    final_inventory = inspect_inventory()
    assembling_machine_count = final_inventory.get(Prototype.AssemblingMachine1, 0)
    assert assembling_machine_count >= 1, f"Failed to craft AssemblingMachine. Expected 1, but got {assembling_machine_count}"
    
    print(f"Successfully crafted 1 AssemblingMachine!")
    print(f"Final inventory: {final_inventory}")


###FUNC SEP

craft_assembling_machine()