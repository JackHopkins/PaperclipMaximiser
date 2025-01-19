# Manual

## Core Interaction Patterns

### 0. Recipe printing
Before crafting any item, you must print the recipes of said items:
```python
# Print recipe for Boiler
print("Recipe for 3 Boilers:")
boiler_recipe = get_prototype_recipe(Prototype.Boiler)
ingredients = boiler_recipe.ingredients
for ingredient in ingredients:
    # need to multiply by 3 as we need 3 boilers
    count = ingredient.count*3
    print(f"Need: {{count}} {{ingredient.name}} for 3 boilers")

```

### 1. Material Processing Requirements
Before crafting any items requiring or copper plates, ores MUST be smelted first:
```python
# Wrong:
# Can't craft directly from ore!
craft_item(Prototype.IronGearWheel)  # Will fail - needs iron plates, not ore

# Correct:
# 1. Get ore
move_to(nearest(Resource.IronOre))
harvest_resource(nearest(Resource.IronOre), quantity=10)
print(f"Harvested 10 iron ore")

# 2. Smelt ore into plates
# move to the position to place the entity
move_to(position)
furnace = place_entity(Prototype.StoneFurnace, position=position)
print(f"Placed the furnace at {furnace.position}")

# we also update the furnace variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
furnace = insert_item(Prototype.Coal, furnace, quantity=5)  # Don't forget fuel
furnace = insert_item(Prototype.IronOre, furnace, quantity=10)

# 3. Wait for smelting (with safety timeout)
for _ in range(30):  # Maximum 30 seconds wait
    if inspect_inventory(furnace)[Prototype.IronPlate] >= 10:
        break
    sleep(1)
else:
    raise Exception("Smelting timeout - check fuel and inputs")

# final check for the inventory of furnace
iron_plates_in_furnace = inspect_inventory(furnace)[Prototype.IronPlate]
assert iron_plates_in_furnace>=10, "Not enough iron plates in furnace"
print(f"Smelted 10 iron plates")
# 4. Now you can craft
craft_item(Prototype.IronGearWheel)
print(f"Crafted on gear wheels")
```

### 2. Inventory Requirements
Before placing any entity, ensure it exists in the inventory. Many beginners miss this crucial step:
```python
# Wrong:
drill = place_entity(Prototype.BurnerMiningDrill, position=position)  # Will fail if not in inventory!

# Correct:
inventory = inspect_inventory()
burner_drills_in_inventry = inventory[Prototype.BurnerMiningDrill]
assert burner_drills_in_inventry > 0, "No drills in inventory 
# move to the position to place the entity
move_to(position)
drill = place_entity(Prototype.BurnerMiningDrill, position=position)
print(f"Placed drill at {drill.position}")
```

You can inspect your own inventory, or the inventory of an entity:
```python
# Check player inventory
player_inv = inspect_inventory()
iron_plates = player_inv[Prototype.IronPlate]

# Check entity inventory
# move to the position to place the entity
move_to(pos)
furnace = place_entity(Prototype.StoneFurnace, position=pos)
print(f"Placed furnace at {furnace.position}")
furnace_inv = inspect_inventory(furnace)
coal_in_furnace = furnace_inv[Prototype.Coal]
```

### 2. Resource Location & Movement
Before any entity placement or interaction, you must first move to the target location:
```python
# Always locate resources first
resource_position = nearest(Resource.Coal)
print(f"Found iron at {resource_position}")
move_to(resource_position)  # Must move before placing/interacting
```

### 3. Entity Placement Prerequisites

#### Basic Entity Placement
Entities must be placed in a valid location after moving there:
```python
# Basic placement pattern
move_to(target_position) 
entity = place_entity(Prototype.Entity, position=target_position)
print(f"Placed entity at {entity.position}")
```

#### Using place_entity_next_to
The `place_entity_next_to` method is crucial for building organized factory layouts. It handles:
- Automatic position calculation based on entity dimensions
- Proper spacing between entities
- Direction-aware placement

Key parameters:
- `entity_prototype`: The type of entity to place
- `reference_position`: Position of the entity to place next to
- `direction`: Which direction to place relative to reference (UP, DOWN, LEFT, RIGHT)
- `spacing`: Additional tiles of space between entities (0 or more)

```python
# Basic usage
# move to the position to place the entity
move_to(drill_position)
ref_entity = place_entity(Prototype.BurnerMiningDrill, position=drill_position)
connected_entity = place_entity_next_to(
    Prototype.BurnerInserter,
    reference_position=ref_entity.position,
    direction=Direction.UP,
    spacing=0
)
print(f"Placed entity at {connected_entity.position}")
```

#### Common Patterns and Use Cases

1. **Resource factory**
- When creating factories, you must plan out the size requirements of the factory sections. Use the BuildingBox for this. You can set the height and width of the area you need for a specific entity placement. For instance, for a single drill, the height and width requirements are 2 so it buildingbox = BuildingBox(height = 2, width = 2). For a drill line, you can do BuildingBox(height = 2, width = 2*drill_line).
- When knowing the size, use nearest_buildable to get the center coordinate of the area where the BuildingBox would fit. Use the center_position argument, where you can send in the position around where you need to find the buildable area. The returns of the nearest_buildable is a dictionary containing the top left position and bottom right position of the buildable area 
            left_top - The top left position of the buildable area
            right_bottom - The bottom right position of the buildable area
- Use the Buildingbox to plan out all factory areas, use one for mining, one for assembling machine area etc. 
- Put each factory section sufficiently far away from each other to ensure no overlap. For instance, when creating plate factories going into an assembling machine, put the assembling machine 10 spaces away from the drills

Example: Iron ore mine
```python
# move to the position to place the entity
move_to(iron_ore_position)
# define the BuildingBox for the drills.
# A BurnerMiningDrill is 2 tiles wide and ElectricMiningDrill is 3 tiles wide so we need to take that into account
# We also need to put a chest at the drop point of the drill so the height needs to be 2
building_box = BuildingBox(width = 2, height = 2)
# get the nearest buildable area around the iron_ore_position
buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, iron_ore_position)
# Place drill on the left_top of the buildable_coordinates
drill_pos = buildable_coordinates["left_top"]
move_to(drill_pos)
drill = place_entity(Prototype.BurnerMiningDrill, position=drill_pos)
print(f"Placed drill at {drill.position}") # Position(x = 0, y = 10)

# place a chest at the drop position of the drill to catch the ore
collection_chest = place_entity(Prototype.WoodenChest, position = drill.position)
print(f"Put a collection chest at {collection_chest.position}")
# wait 10 seconds to check if the construct works and chest has ore
sleep(10)

# get the updated chest entity
collection_chest = get_entity(Prototype.WoodenChest, position = collection_chest.position)
# get the inventory
chest_inventory = inspect_inventory(collection_chest)
# get the iron ore in inventory
iron_ore_in_chest = chest_inventory[Resource.IronOre]
# check for iron onre
assert iron_ore_in_chest > 0, "No iron ore in chest"
```

2. **Power Infrastructure**

Power typically involves:
-> Water Source + OffshorePump
-> Boiler (burning coal)
-> SteamEngine
-> Electrical Poles connecting to consumers
NB: Use atleast spacing of 3 to ensure there is enough room for pipes
Always use connect_entities with power poles
```python
# move to the position to place the entity
move_to(water_position)
# Connect water pump to boiler to steam engine
offshore_pump = place_entity(Prototype.OffshorePump, position=water_position)
boiler = place_entity_next_to(
    Prototype.Boiler,
    reference_position=offshore_pump.position,
    direction=Direction.UP,
    spacing=3  # Extra space for pipes
)
steam_engine = place_entity_next_to(
    Prototype.SteamEngine,
    reference_position=boiler.position,
    direction=Direction.RIGHT,
    spacing=3
)
print(f"Placed steam engine at {steam_engine.position}")
```

#### Special Considerations

1. **Entity Rotation**
- Some entities (like steam engines) auto-rotate based on connection points
- Others need manual rotation after placement:
```python
drill = place_entity_next_to(Prototype.ElectricMiningDrill, 
    reference_position=position,
    direction=Direction.RIGHT) # This places the drill to the RIGHT the position
drill = rotate_entity(drill, Direction.DOWN) # This orients the drill downwards
```

2. **Entity Dimensions**
- Account for different entity sizes when planning layouts
- Use `tile_dimensions` for reference:
```python
print(f"Entity dimensions: {entity.tile_dimensions}")
assert entity.position.is_close(expected_position, tolerance=1)
```

3. **Drop Positions**
- Use `drop_position` when connecting output of one entity to another
- When connecting to a inserter, use the pickup_position of target inserter
For example, if you want to connect inserter_1 at Position(x = 12, y = 11) to inserter_2 at Position(x = 0, y = 0)
```python
# get the inserter entities
inserter_1 = get_entity(Prototype.BurnerInserter, position = Position(x = 12, y = 11))
inserter_2 = get_entity(Prototype.BurnerInserter, position = Position(x = 0, y = 0))
# connect the two inserters
belts = connect_entities(
    inserter_1.drop_position,
    inserter_2.pickup_position,
    Prototype.TransportBelt
)
```

4. **Spacing Guidelines**
- Use 0 spacing for flush connections and when placing inserters
- Use 1 spacing for entities that need space for inserters between them
- Use 3+ spacing for power setups (boiler to steam engine) or where you need extra space for pipes or belts.


5. **Position Handling**
The Position class provides helpful methods for working with coordinates:
```python
# Position arithmetic
new_pos = pos1 + Position(x=2, y=0)  # Move right 2 units
```

### 4. Multiple section Construction
When building with multiple factory sections, follow this pattern:
1. Place primary producer (e.g., mining drill) NB: Mining drills do not need inserts, they have a drop position
2. Place destination entity if required (e.g., assembling machine). NB: Put destination entity sufficiently far away from target (eg 10 spaces)
3. Place inserters if required into the destination entity
4. Place connectors (e.g.belts, pipes)
5. Add fuel/resources

Example:
Create a iron plate mine into a assembling machine
The target is the furnace at the drop position of drill and destionation is the assembling machine
This long task should also be split into multiple policies
POLICY 1 - Set up drill and furnace
```python
# Example mining-plate-to-chest chain
# get iron ore location
ore_position = nearest(Resource.IronOre)
move_to(ore_position)
# define the BuildingBox for the drill.
# A BurnerMiningDrill is 2 tiles wide and ElectricMiningDrill is 3 tiles wide so we need to take that into account
# We need furnaces at the drop position so we put height as 2
building_box = BuildingBox(width = 2, height = 2)
# get the nearest buildable area around the iron_ore_position
buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, ore_position)
# Place drill on the left_top of the buildable_coordinates
drill_pos = buildable_coordinates["left_top"]
move_to(drill_pos)
drill = place_entity(Prototype.BurnerMiningDrill, position=drill_pos)
print(f"Placed drill at {drill.position}") # Position(x = 11, y = -10)
# place a furnace at the drop position of the drill
# This will get the furnace to automatically produce plates
furnace = place_entity(Prototype.StoneFurnace, 
    position = drill.drop_position)
print(f"Placed furnace at {furnace.position}") # Position(x = 10, y = -10)

# Always fuel burner entities after placement
# we also update the drill variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
drill = insert_item(Prototype.Coal, drill, quantity=29)

# Always fuel burner entities after placement
# we also update the furnace variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
furnace = insert_item(Prototype.Coal, furnace, quantity=20)

# Place inserter next to furnace to take from the furnace
# No need to rotate as it needs to take from furnace
# always use 0 spacing for inserters
furnace_output_inserter = place_entity_next_to(Prototype.BurnerInserter,
    reference_position=furnace.position,
    direction=Direction.RIGHT,
    spacing = 0)
print(f"Placed furnace_output_inserter at {furnace_output_inserter.position}") # Position(x = 9, y = -10)
```

POLICY 2 - Set up assembling machine with inserter and connect
```python
# get the furnace output inserter entity
furnace_output_inserter = get_entity(Prototype.BurnerInserter, position = Position(x = 9, y = -10))

# Place a chest 10 spaces away
target_position = Position(x = furnace_output_inserter.position.x + 10, y = furnace_output_inserter.position.y)
# move to the position to place the entity
move_to(target_position)
# define the buildable area for the assembling machine, assembling machine is 3 wide
# Put 2 as width as we need to account for the inserter
building_box = BuildingBox(width = 2, height = 3)
# get the nearest buildable area around the iron_ore_position
buildable_coordinates = nearest_buildable(Prototype.WoodenChest, building_box, iron_ore_position)
# use the left_top coordinate to put the target_machine
assembly_pos = buildable_coordinates["left_top"]
move_to(assembly_pos)
target_machine = place_entity(Prototype.AssemblingMachine, position=assembly_pos)
print(f"Placed target_machine at {target_machine.position}")


# put a inserter next to the assembly machine
# always use 0 spacing for inserters
# direction is RIGHT as we put 2 at the width of the buildable coordinates
machine_input_inserter = place_entity_next_to(Prototype.BurnerInserter,
    reference_position=target_machine.position,
    direction=Direction.RIGHT,
    spacing = 0)

# rotate the inserter as we need to put items into the chest
machine_input_inserter = rotate_entity(machine_input_inserter, direction = Direction.LEFT)
# fuel the inserter
# we also update the inserter variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
machine_input_inserter = insert_item(Prototype.Coal, machine_input_inserter, quantity=20)

# connect the furnace output inserter to chest input inserter
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
connect_entities(furnace_output_inserter.drop_position, machine_input_inserter.pickup_position Prototype.TransportBelt)
```

### 5. Power Systems
Power systems follow a specific order:
1. Water source connection
2. Power generation
3. Power distribution
4. Consumer connection

This should also be done in 2 policies
POLICY 1 - Set up power system
```python
# Power system pattern
move_to(water_position)
# first place offshore pump on the water system
offshore_pump = place_entity(Prototype.OffshorePump, position=water_position)

# Then place the boiler next to the offshore pump 
# use a spacing of atlest 3 as the entities are large and otherwise won't fit
boiler = place_entity_next_to(Prototype.Boiler, 
    reference_position=offshore_pump.position,
    spacing=3)

# Finally we need to place the steam engine next to the boiler
# Using the spacing of 3 again
steam_engine = place_entity_next_to(Prototype.SteamEngine,
    reference_position=boiler.position,
    spacing=3)
print(f"Placed steam_engine at {steam_engine.position}") # Position(x=4, y = -21)
# Connect entities in order
water_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)
steam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)

# check that the steam engine is generating power
assert steam_engine.energy > 0, f"Steam engine is not generating power"
```

POLICY 2 - Power target entity
```python
# get the steam engine
steam_engine = get_entity(Prototype.SteamEngine, position = Position(x=4, y = -21))

# To power electric mining drills or assembling machines, the engine needs to be connected with electricpoles
# for example, if one exists in Position(x = 1, y = 19), we first get the entity
assembling_machine = get_entity(Prototype.AssemblingMachine1, position = Position(x = 1, y = 19))

# We then connect with connect entities
connect_entities(assembling_machine.position, steam_engine.position, Prototype.SmallElectricPole)
# wait for 10 seconds to power up
sleep(10)
# check that the power was successful
# first refresh entity
assembling_machine = get_entity(Prototype.AssemblingMachine1, position = Position(x = 1, y = 19))
# check for power
assert assembling_machine.energy > 0, f"assembling machine is not getting"
```

### 6. Belt Systems
When creating belt systems:
1. Establish source
2. Place destination
3. Connect with belts
NB: ALWAYS USE INSERTERS TO INSERT ITEMS INTO DESTINATION OR TAKE FROM SOURCE
Only difference are drills as they have a drop_position that automatically drops resources

Example
Move items from a chest to a furnace
```python
source_position = Position(0, 0)
# Belt system pattern
move_to(source_position)
# define the BuildingBox for the chest. 
# A chest is one tile wide
# We add 2 as height as we want to add a inserter
building_box = BuildingBox(width = 1, height = 2)
# get the nearest buildable area around the iron_ore_position
buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, source_position)
# Place chest on the left_top of the buildable_coordinates
source_pos = buildable_coordinates["left_top"]
move_to(source_pos)
source = place_entity(Prototype.WoodenChest, position=source_pos)
print(f"Placed chest at {source.position}")
# add inserter
# always use 0 spacing for inserters
# direction is UP as we put 2 at the height of the buildable coordinates
# we do not need to rotate the inserter as it takes from the chest not puts to it
source_inserter = place_entity_next_to(Prototype.BurnerInserter, 
    reference_position=destination_chest.position,
    direction=Direction.UP,
    spacing = 0)

# Place a furnace 10 spaces away
target_position = Position(x = source.position.x, y = source.position.y)
# move to the position to place the entity
move_to(target_position)
# define the buildable area for the furnace, furnace needs only one width
# Also need to account for inserter so width is 2
building_box = BuildingBox(width = 2, height = 1)
# get the nearest buildable area around the iron_ore_position
buildable_coordinates = nearest_buildable(Prototype.WoodenChest, building_box, iron_ore_position)
# use the left_top coordinate to put the furnace
furnace_pos = buildable_coordinates["left_top"]
move_to(furnace_pos)
destination_furnace = place_entity(Prototype.WoodenChest, position=furnace_pos)
print(f"Placed destination_furnace at {destination_furnace.position}")
# add inserter
# always use 0 spacing for inserters
# direction is LEFT as we put 2 at the width of the buildable coordinates
destination_inserter = place_entity_next_to(Prototype.BurnerInserter, 
    reference_position=destination_furnace.position,
    direction=Direction.LEFT,
    spacing = 0)
print(f"Placed destination_inserter at {destination_inserter.position}")
# VERY IMPORTANT: rotate inserter as by default the inserter takes items from the entity it is placed next to
# We want it to put items into the destination furnace
destination_inserter = rotate_entity(destination_inserter, Direction.RIGHT)  # Face inserter toward furnace
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
belt = connect_entities(source.drop_position, destination_inserter.pickup_position, 
    Prototype.TransportBelt)
```

### 8. Using assembling machines
To create automatic item crafting mines (copper cable, electronic circuits etc), you need to use a assembling machine that automatically crafts the entities.
To use assembling machines for automatic crafting mines, you need to power them and set their recipe
The recipe will be set to the entity the machine needs to craft
You also need to add inserters that input crafting ingredients into the machine and inserters that take the crafted item out of the machine

```python
# Assume there's an assembling machine at Position(x = 2, y = -19) and a steam engine generating power at Position(x = -10, y = 0)

# first get the assembling machine and steam engine entities
assembling_machine = get_entity(Prototype.AssemblingMachine1, position = Position(x = 2, y = -19))
steam_engine = get_entity(Prototype.SteamEngine, position = Position(x = -10, y = 0))

# connect the steam engine and assembling machine with power poles to power the assembling machine
# We use connect entities as we're dealing with power poles
connect_entities(assembling_machine.position, steam_engine.position, Prototype.SmallElectricPole)
# wait for 10 sec to assure assembling machine is powered
sleep(10)
# update the assembling machine entity
assembling_machine = get_entity(Prototype.AssemblingMachine1, position = Position(x = 2, y = -19))
assert assembling_machine.energy>0, "Assembling machine is not powered"

# set the recipe for assembling machine to iron gear wheels
set_entity_recipe(entity = assembly_machine, prototype = Prototype.CopperCable)
print(f"Set the recipe of assembly machine at {{assembly_machine.position}} to Prototype.CopperCable")

# add inserter that inputs ingredients that will be crafted to the target entity
# always use 0 spacing for inserters
ingredient_input_inserter = place_entity_next_to(
    Prototype.BurnerInserter, 
    assembling_machine.position,
    direction=Direction.UP,
    spacing = 0
)
#VERY IMPORTANT:  Need to rotate the inserter as it needs to put itms into assembling machine
ingredient_input_inserter = rotate_entity(ingredient_input_inserter, Direction.DOWN)  # Face inserter towards the assembling machine

# add inserter that takes the cables away
# always use 0 spacing for inserters
output_inserter = place_entity_next_to(
    Prototype.BurnerInserter, 
    assembling_machine.position,
    direction=Direction.LEFT,
    spacing = 0
)
```


#### Key Features
1. **Resource Requirements**: Automatically considers entity placement requirements (e.g., miners must be on ore patches)
2. **Space Validation**: Ensures enough clear space for different factory sections, eg assembling machine area 10 spaces away from furnaces

#### Common Patterns

1. **Mining Setup**:
Example: Create a resource mining line
```python
# Find space for a line of 3 miners
move_to(source_position)
# define the BuildingBox for the drill. 
# A BurnerMiningDrill is 2 tiles wide and ElectricMiningDrill is 3 tiles wide so we need to take that into account
# We need 3 drills so width is 3*3
building_box = BuildingBox(width = 3*3, height = 1)
# get the nearest buildable area around the source_position
buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, source_position)

# Place miners in a line
# we first get the leftmost coordinate of the buildingbox to start building from
left_top = buildable_coordinates["left_top"]
# first lets move to the left_top to ensure building
move_to(left_top)
for i in range(3):
    # we now iterate from the leftmost point towards the right
    # take steps of 2 as drills have width of 2
    drill_pos = Position(x=left_top.x + 2*i, y=left_top.y)
    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)
    print(f"Placed drill {i} at {drill.position}")
    # place a chest to catch the ore
    chest = place_entity(Prototype.WoodenChest, position = drill.drop_position)
    print(f"Placed chest to catch drill {i} ore at {chest.position}")
```

#### Error Handling
The function raises an exception if no valid position is found. Always wrap usage in try/except when placement requirements are uncertain:

```python
try:
    position = nearest_buildable(
        Prototype.ElectricMiningDrill,
        bounding_box=large_area
    )
except Exception as e:
    print(f"Could not find valid placement: {e}")
    # Handle alternative placement strategy
```

#### Best Practices

1. **Size Calculation**:
- Include margins in bounding box calculations
- Account for entity dimensions and spacing
- Consider connection points for belts/inserters


3. **Placement Verification**:
- Always verify placement after finding position
- Use can_place_entity for additional validation
```python
position = nearest_buildable(Prototype.StoneFurnace)
if can_place_entity(Prototype.StoneFurnace, position=position):
    furnace = place_entity(Prototype.StoneFurnace, position=position)
```

### Self-Fueling Mining Systems

Self-fueling mining systems are essential for automating resource collection, particularly for coal mining. These systems use the mined coal to power themselves, creating a sustainable loop.

#### Basic Self-Fueling Mine Pattern
```python
# 1. Find suitable coal patch
coal_patch = nearest(Resource.Coal)
# define the BuildingBox for the drill. 
# A BurnerMiningDrill is 2 tiles wide and ElectricMiningDrill is 3 tiles wide so we need to take that into account
# We need to put 2 as height as we account for the inserter 
building_box = BuildingBox(width = 2, height = 2)
# get the nearest buildable area around the source_position
buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, source_position)

# 2. Place mining drill
# place in left_top of buildable_coordinates
target_pos = buildable_coordinates["left_top"]
move_to(target_pos)
drill = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, target_pos)
print(f"Placed drill at {drill.position}")

# 3. Place inserter to feed coal back into drill
# direction is UP as we put 2 at the height of the buildable coordinates
coal_input_inserter = place_entity_next_to(
    Prototype.BurnerInserter, 
    drill.position,
    direction=Direction.UP,
    spacing=0
)
print(f"Placed coal_input_inserter at {coal_input_inserter.position}")
# VERY IMPORTANT: rotate input inserter to put items into drill
coal_input_inserter = rotate_entity(coal_input_inserter, Direction.DOWN)  # Face inserter toward drill

# 4. Connect with transport belt
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
belts = connect_entities(
    drill.drop_position,
    inserter.pickup_position,
    Prototype.TransportBelt
)

# 5. Bootstrap system with initial fuel
# we also update the drill variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
drill = insert_item(Prototype.Coal, drill, quantity=20)
```

#### Multi-Drill Self-Fueling Systems

For larger operations, you can create systems with multiple drills sharing a common fuel belt:

```python
    """
    Build a self-fueling coal mining system with multiple drills.
    """
    num_drills = 5
    drills = []
    inserters = []
    # define the BuildingBox for the drill. 
    # A BurnerMiningDrill is 2 tiles wide and ElectricMiningDrill is 3 tiles wide so we need to take that into account
    # need 5 drills
    # Also need to put 2 as the height to take into account inserter
    building_box = BuildingBox(width = 2*5, height = 2)
    # get the nearest buildable area around the source_position
    buildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, source_position)

    # 1. Place drills and their inserters
    # we first get the leftmost coordinate of the buildingbox to start building from
    left_top = buildable_coordinates["left_top"]
    # first move to the left_top
    move_to(left_top)
    for i in range(num_drills):
        # Calculate positions with proper spacing
        drill_position = Position(
            x=left_top.x + i * 2,
            y=left_top.y
        )
        move_to(drill_position)
        # Place and configure each drill
        drill = place_entity(
            Prototype.BurnerMiningDrill,
            Direction.DOWN,
            drill_position
        )
        
        # Place and configure inserter for fuel
        # always use 0 spacing for inserters
        # direction is UP as we put 2 at the height of the buildable coordinates
        inserter = place_entity_next_to(
            Prototype.BurnerInserter,
            drill_position,
            direction=Direction.UP,
            spacing=0
        )
        # VERY IMPORTANT: Rotate inserter to put items into drill
        inserter = rotate_entity(inserter, Direction.DOWN)
        
        drills.append(drill)
        inserters.append(inserter)
    
    # 2. Create main transport belt
    belt_start = Position(
        x=drills[0].drop_position.x,
        y=drills[0].drop_position.y
    )
    belt_end = Position(
        x=drills[-1].drop_position.x,
        y=drills[0].drop_position.y
    )
    
    # 3. Connect belt in a loop
    main_belt = connect_entities(
        belt_start,
        belt_end,
        Prototype.TransportBelt
    )
    
    # Connect to last inserter
    connect_entities(
        belt_end,
        inserters[-1].pickup_position,
        Prototype.TransportBelt
    )
    
    # Connect between inserters
    connect_entities(
        inserters[-1].pickup_position,
        inserters[0].pickup_position,
        Prototype.TransportBelt
    )
    
    # Close the loop
    connect_entities(
        inserters[0].pickup_position,
        belt_start,
        Prototype.TransportBelt
    )
    
    # 4. Bootstrap the system
    # we also update the drill variable by returning it from the function
    # This ensures it doesnt get stale and the inventory updates are represented in the variable
    drills[0] = insert_item(Prototype.Coal, drills[0], quantity=10)
```

#### Best Practices for Self-Fueling Systems

1. **Resource Verification**
   - Always verify coal patch size before building
   - Ensure patch is large enough for planned number of drills
   ```python
   assert coal_patch.size >= num_drills * 5, "Coal patch too small"
   ```

2. **Proper Belt Loops**
   - Create complete loops without gaps
   - Verify belt connections after placement
   - Use proper belt directions at corners

3. **System Bootstrap**
   - Add initial fuel to at least one drill
   - Verify fuel reaches all drills
   - Monitor system startup to ensure proper operation

4. **Error Handling**
   ```python
   try:
       drill = place_entity(Prototype.BurnerMiningDrill, position)
       # always use 0 spacing for inserters
       inserter = place_entity_next_to(
           Prototype.BurnerInserter,
           drill.position,
           direction=Direction.UP,
           spacing = 0
       )
   except Exception as e:
       print(f"Failed to build mining system: {e}")
       # Clean up partial construction
   ```

#### Common Patterns

1. **Linear Mining Array**
   - Place drills in a straight line
   - Place chests or furnaces at the drop positions

2. **Compact Design**
   - Minimal spacing between components
   - Direct inserter connections
   - Efficient belt routing

3. **Redundant Systems**
   - Multiple fuel paths
   - Backup inserters
   - Buffer chests for stability

#### Troubleshooting

1. **System Stalls**
   - Check belt continuity
   - Verify inserter directions
   - Ensure adequate initial fuel

2. **Inefficient Operation**
   - Optimize belt paths
   - Balance drill placement
   - Adjust inserter positions

3. **Startup Issues**
   - Add more initial fuel
   - Verify all connections
   - Check entity rotation

4. **Logging**
   - Log your actions as you go along
   - Make sure to log placing or interactions with the map that give information about your environment
   - Log all unknown information as that will be seen in the future steps and used for debugging or planning

5. **Outdated variables**
   - Always update your variables you want to use to ensure the variable state is not outdated
   - Whenever you use insert_item, make sure to override the input entity with the return
   - Always use inspect_inventory to get the inventories, as that gets the latest inventory
   - Regularly update your variables using entity = get_entity(Prototype.X, entity.position)


## Common Antipatterns to Avoid

1. **Missing Movement**
```python
# Wrong:
entity = place_entity(Prototype.Entity, position=position)

# Correct:
move_to(position)
entity = place_entity(Prototype.Entity, position=position)
```

2. **Incorrect Order Dependencies**
```python
# Wrong:
inserter = place_entity(Prototype.Inserter, position=position)
chest = place_entity(Prototype.WoodenChest, position=chest_position)

# Correct:
# move to the position to place the entity
move_to(chest_position)
chest = place_entity(Prototype.WoodenChest, position=chest_position)
inserter = place_entity_next_to(Prototype.Inserter, 
    reference_position=chest.position, spacing = 0)
```

3. **Unfueled Burner Entities**
```python
# Wrong:
drill = place_entity(Prototype.BurnerMiningDrill, position=position)
# Missing fuel!

# Correct:
drill = place_entity(Prototype.BurnerMiningDrill, position=position)

# we also update the drill variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
drill = insert_item(Prototype.Coal, drill, quantity=20)
```

## Best Practices

1. **Resource Discovery**
- Always use `nearest()` to find resources
- Cache resource patch information when multiple entities will use it
```python
coal_patch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
```

2. **Entity Positioning and Crafting**
- Verify inventory contains entity before attempting placement
- Craft required entities and materials before starting construction
- Check recipe requirements recursively for complex entities
- Always print the recipes to know what are the dependencies
- Maintain consistent spacing patterns for similar entity types


3. **Resource Management**
- Pre-calculate resource requirements
- Verify inventory contents before placement
- Use consistent fuel quantities for similar entity types

4. **Error Handling**
- Always check return values from placement functions
- Verify entity states after important operations
- Clean up partially constructed systems on failure


## INSTRUCTIONS WHEN CREATING STRUCTURES
- To create resource mines (stone, coal, iron ore, copper ore), you first need to place burner or electric mining drills as a starting point. Then you need to place chests or furnaces at the drop position of the drill to catch the resources and store (chest) or smelt (furnace) them
- When multiple section mines are created (for instance assembly machines), the ending point cannot be next to the starting point because of collisions. A rule of thumb is atleast 10 tiles away from the mine start position. ALWAYS use nearest_buildable when building different sections of the mines. You might otherwise try to put entities cannot be put due to water of overlapping sections
- IMPORTANT: When placing inserters, they by default take items from the entity they are placed next to. They need to be rotated 180 degrees to put items into the entity they are next to
- To create a working assembling machine for automatic crafting structures (e.g automatic iron gear wheel mine), the assembling machine must be put down, the recipe of the machine must be set, the machine must be powered with electricity, inserters must insert crafting ingredients (iron plates for iron gear wheel) into the machine and one inserter must take the final product (e.g iron gear wheel) out of the machine
- When a entity has status "WAITING_FOR_SPACE_IN_DESTINATION", it means the there is no space in the drop position. For instance, a mining drill will have status WAITING_FOR_SPACE_IN_DESTINATION when the entities it mines are not being properly collected by a furnace or a chest or transported away from drop position with transport belts
- Make sure to always put enough fuel into all entities that require fuel. It's easy to mine more coal, so it's better to insert in abundance 
- Keep it simple! Minimise the usage of transport belts if you don't need them. Use chests and furnaces to catch the ore directly from drills