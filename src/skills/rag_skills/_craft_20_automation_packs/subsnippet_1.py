def smelt_ores(iron_ore_count: int, copper_ore_count: int) -> None:
    """
    Smelt iron and copper ores into plates
    :param iron_ore_count: The number of iron ores to smelt
    :param copper_ore_count: The number of copper ores to smelt
    :return: None
    """
    # [PLANNING]
    # 1. Check if we have enough ores in the inventory
    # 2. Find or create a stone furnace
    # 3. Fuel the furnace with coal
    # 4. Smelt iron ores
    # 5. Smelt copper ores
    # 6. Extract the smelted plates
    # 7. Verify the results
    # [END OF PLANNING]

    print(f"Starting to smelt {iron_ore_count} iron ores and {copper_ore_count} copper ores")
    print(f"Initial inventory: {inspect_inventory()}")

    # Check if we have enough ores in the inventory
    inventory = inspect_inventory()
    assert inventory[Prototype.IronOre] >= iron_ore_count, f"Not enough iron ore. Required: {iron_ore_count}, Available: {inventory[Prototype.IronOre]}"
    assert inventory[Prototype.CopperOre] >= copper_ore_count, f"Not enough copper ore. Required: {copper_ore_count}, Available: {inventory[Prototype.CopperOre]}"

    # Find or create a stone furnace
    furnaces = inspect_entities().get_entities(Prototype.StoneFurnace)
    if not furnaces:
        print("No existing furnace found. Crafting a new one.")
        craft_item(Prototype.StoneFurnace, 1)
        furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))
    else:
        furnace = furnaces[0]
    
    print(f"Using furnace at position: {furnace.position}")
    move_to(furnace.position)

    # Fuel the furnace with coal
    coal_needed = (iron_ore_count + copper_ore_count) // 4 + 1  # Assuming 1 coal can smelt 4 ores
    if inventory[Prototype.Coal] < coal_needed:
        coal_to_mine = coal_needed - inventory[Prototype.Coal]
        coal_position = nearest(Resource.Coal)
        move_to(coal_position)
        harvest_resource(coal_position, coal_to_mine)
        move_to(furnace.position)
    
    insert_item(Prototype.Coal, furnace, coal_needed)
    print(f"Inserted {coal_needed} coal into the furnace")

    # """[SYNTHESISED]
    # Name: smelt_ore
    # Objective: Smelt a specific type of ore into plates
    # Mining setup: We have a fueled furnace
    # Inventory: We have the required ore in the inventory
    # :param ore_type: The type of ore to smelt (Prototype.IronOre or Prototype.CopperOre)
    # :param ore_count: The number of ores to smelt
    # :param furnace: The furnace entity to use for smelting
    # :return: None
    # [END OF SYNTHESISED]"""

    # Smelt iron ores
    smelt_ore(ore_type=Prototype.IronOre, ore_count=iron_ore_count, furnace=furnace)

    # Smelt copper ores
    smelt_ore(ore_type=Prototype.CopperOre, ore_count=copper_ore_count, furnace=furnace)

    # Verify the results
    final_inventory = inspect_inventory()
    iron_plates_smelted = final_inventory[Prototype.IronPlate] - inventory[Prototype.IronPlate]
    copper_plates_smelted = final_inventory[Prototype.CopperPlate] - inventory[Prototype.CopperPlate]

    print(f"Iron plates smelted: {iron_plates_smelted}")
    print(f"Copper plates smelted: {copper_plates_smelted}")
    print(f"Final inventory: {final_inventory}")

    assert iron_plates_smelted >= iron_ore_count, f"Failed to smelt enough iron plates. Expected at least {iron_ore_count}, but got {iron_plates_smelted}"
    assert copper_plates_smelted >= copper_ore_count, f"Failed to smelt enough copper plates. Expected at least {copper_ore_count}, but got {copper_plates_smelted}"

    print("Successfully smelted all ores into plates!")