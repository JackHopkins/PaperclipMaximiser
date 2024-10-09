
# move to the iron ore
iron_ore_patch = get_resource_patch(Resource.IronOre, nearest(Resource.IronOre))
move_to(iron_ore_patch.bounding_box.left_top + Position(x=1, y=1))

# harvest 80 iron ore
while inspect_inventory()[Prototype.IronOre] < 80:
    harvest_resource(iron_ore_patch.bounding_box.left_top, quantity=10)
iron_ore_in_inventory = inspect_inventory()[Prototype.IronOre]
assert iron_ore_in_inventory >= 80, f"Failed to mine enough iron ore. Current amount: {iron_ore_in_inventory}"

# move to the stone patch
stone_patch = get_resource_patch(Resource.Stone, nearest(Resource.Stone))

# harvest 10 stone
move_to(stone_patch.bounding_box.left_top + Position(x=1, y=1))
harvest_resource(stone_patch.bounding_box.left_top, quantity=10)
stone_in_inventory = inspect_inventory()[Prototype.Stone]
assert stone_in_inventory >= 10, f"Failed to mine enough stone. Current amount: {stone_in_inventory}"


# move to the coal patch
coal_patch: ResourcePatch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
move_to(coal_patch.bounding_box.left_top + Position(x=1, y=1))

# harvest 30 coal
while inspect_inventory()[Prototype.Coal] < 30:
    harvest_resource(coal_patch.bounding_box.left_top, quantity=10)
coal_in_inventory = inspect_inventory()[Prototype.Coal]
assert coal_in_inventory >= 30, f"Failed to mine enough coal. Current amount: {coal_in_inventory}"

# move to the copper patch
copper_patch: ResourcePatch = get_resource_patch(Resource.CopperOre, nearest(Resource.CopperOre))
move_to(copper_patch.bounding_box.left_top + Position(x=1, y=1))


# harvest 10 copper ore
harvest_resource(copper_patch.bounding_box.left_top, quantity=10)
copper_ore_in_inventory = inspect_inventory()[Prototype.CopperOre]
assert copper_ore_in_inventory >= 10, f"Failed to mine enough copper ore. Current amount: {copper_ore_in_inventory}"

# move to the origin
move_to(Position(x=0, y=0))

# place a stone furnace
stone_furnace = place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))
assert stone_furnace, "Failed to place stone furnace"


# insert 20 coal into the stone furnace
insert_item(Prototype.Coal, stone_furnace, quantity=20)

# insert 80 iron ore into the stone furnace
insert_item(Prototype.IronOre, stone_furnace, quantity=50)
# check if the stone furnace has produced iron plates
while inspect_inventory(stone_furnace)[Prototype.IronPlate] < 50:
    sleep(1)

# extract the iron plates from the stone furnace
extract_item(Prototype.IronPlate, stone_furnace, quantity=50)
assert inspect_inventory()[Prototype.IronPlate] >= 50, "Failed to smelt enough iron plates"

# insert 80 iron ore into the stone furnace
insert_item(Prototype.IronOre, stone_furnace, quantity=30)
# check if the stone furnace has produced iron plates
while inspect_inventory(stone_furnace)[Prototype.IronPlate] < 30:
    sleep(1)

# extract the iron plates from the stone furnace
extract_item(Prototype.IronPlate, stone_furnace, quantity=30)
assert inspect_inventory()[Prototype.IronPlate] >= 30, "Failed to smelt enough iron plates"

# insert 20 copper ore into the stone furnace
insert_item(Prototype.CopperOre, stone_furnace, quantity=20)
# check if the stone furnace has produced copper plates
while inspect_inventory(stone_furnace)[Prototype.CopperPlate] < 20:
    sleep(5)

# extract the copper plates from the stone furnace
extract_item(Prototype.CopperPlate, stone_furnace, quantity=20)
assert inspect_inventory()[Prototype.CopperPlate] >= 20, "Failed to smelt enough copper plates"

# pick up the stone furnace
pickup_entity(stone_furnace)

# craft a burner mining drill
craft_item(Prototype.BurnerMiningDrill)
assert inspect_inventory()[Prototype.BurnerMiningDrill] >= 1, "Failed to craft burner mining drill"

# move to the iron ore patch
move_to(iron_ore_patch.bounding_box.left_top + Position(x=1, y=1))

# place a burner mining drill
burner_mining_drill: BurnerMiningDrill = place_entity(Prototype.BurnerMiningDrill,
                                                               position=iron_ore_patch.bounding_box.left_top)
assert burner_mining_drill, "Failed to place burner mining drill"

# fuel the burner mining drill
insert_item(Prototype.Coal, burner_mining_drill, quantity=5)

# place the stone furnace
stone_furnace = place_entity_next_to(Prototype.StoneFurnace,
                                          reference_position=burner_mining_drill.drop_position,
                                          direction=Direction.UP,
                                          spacing=0)
assert stone_furnace, "Failed to place stone furnace"

# place a burner inserter
burner_inserter = place_entity_next_to(Prototype.BurnerInserter,
                                            reference_position=stone_furnace.position,
                                            direction=Direction.UP,
                                            spacing=1)
assert burner_inserter, "Failed to place burner inserter"

# craft an assembly machine
craft_item(Prototype.AssemblingMachine1)
assert inspect_inventory()[Prototype.AssemblingMachine1] >= 1, "Failed to craft assembly machine"

# place the assembly machine
assembly_machine = place_entity_next_to(Prototype.AssemblingMachine1,
                                             reference_position=burner_inserter.position,
                                             direction=Direction.UP,
                                             spacing=0)
assert assembly_machine, "Failed to place assembly machine"
# set the recipe for the assembly machine to produce iron gears
set_entity_recipe(assembly_machine, Prototype.IronGearWheel)

# craft an offshore pump
craft_item(Prototype.OffshorePump)
assert inspect_inventory()[Prototype.OffshorePump] >= 1, "Failed to craft offshore pump"

# place the offshore pump at nearest water source
move_to(nearest(Resource.Water))
offshore_pump = place_entity(Prototype.OffshorePump,
                                  position=nearest(Resource.Water),
                                  direction=Direction.LEFT)
assert offshore_pump, "Failed to place offshore pump"
    
# craft a boiler
craft_item(Prototype.Boiler)
assert inspect_inventory()[Prototype.Boiler] >= 1, "Failed to craft boiler"


# place the boiler next to the offshore pump
boiler = place_entity_next_to(Prototype.Boiler,
                                   reference_position=offshore_pump.position,
                                   direction=Direction.LEFT,
                                   spacing=2)
assert boiler, "Failed to place boiler"


# craft a steam engine
craft_item(Prototype.SteamEngine)
assert inspect_inventory()[Prototype.SteamEngine] >= 1, "Failed to craft steam engine"

# place the steam engine next to the boiler
steam_engine = place_entity_next_to(Prototype.SteamEngine,
                                         reference_position=boiler.position,
                                         direction=Direction.LEFT,
                                         spacing=2)
assert steam_engine, "Failed to place steam engine"

# connect the steam engine and assembly machine with power poles
# harvest nearby trees for wood
tree_patch = get_resource_patch(Resource.Wood, nearest(Resource.Wood))
move_to(tree_patch.bounding_box.left_top + Position(x=1, y=1))
harvest_resource(tree_patch.bounding_box.left_top, quantity=10)
assert inspect_inventory()[Resource.Wood] >= 10, "Failed to harvest enough wood"


# craft 5 small electric poles
craft_item(Prototype.SmallElectricPole, quantity=5)
assert inspect_inventory()[Prototype.SmallElectricPole] >= 5, "Failed to craft small electric poles"

# place connect the steam engine and assembly machine with power poles
connect_entities(steam_engine, assembly_machine, connection_type=Prototype.SmallElectricPole)

# place connective pipes between the boiler and steam engine
connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)

# place connective pipes between the boiler and offshore pump
connect_entities(boiler, offshore_pump, connection_type=Prototype.Pipe)

# insert coal into the boiler
insert_item(Prototype.Coal, boiler, quantity=15)
insert_item(Prototype.Coal, burner_inserter, quantity=15)
insert_item(Prototype.Coal, stone_furnace, quantity=15)
sleep(5)

# check if the assembly machine has produced iron gears
inventory = inspect_inventory(entity=assembly_machine)
assert inventory.get(Prototype.IronGearWheel) >= 0