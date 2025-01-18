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

1. **Mining to a target entity Setup**
When creating factories, put each factory section sufficiently far away from each other to ensure no overlap 
For instance, when creating plate factories, put the furnace smelting area 10 spaces away from the mining area and the chest area 10 places away from the smelting area

The large task of creating a mining factory should be split into multiple policies
POLICY 1 -- Place drill and chest with inserter
```python
# move to the position to place the entity
move_to(iron_ore_position)
# Place drill on iron_ore patch
drill = place_entity(Prototype.BurnerMiningDrill, position=iron_ore_position)
print(f"Placed drill at {drill.position}") # Position(x = 0, y = 10)
# Place a chest 10 spaces away
# Can also use furnaces if want to get plates
target_position = Position(x = drill.position.x + 10, y = drill.position.y + 10)
# move to the position to place the entity
move_to(target_position)
target_chest = place_entity(Prototype.WoodenChest, position=target_position)
print(f"Placed target chest at {target_chest.position}") # Position(x = 20, y = 20)

# place a inserter next to the target chest
# always use 0 spacing for inserters
target_insterter = place_entity_next_to(Prototype.BurnerInserter, 
                                        reference_position=target_chest.position,
                                        direction = Direction.UP,
                                        spacing = 0)
#VERY IMPORTANT: WE ALWAYS NEED TO ROTATE INSERTERS TO PUT ITEMS INTO THE TARGET ENTITY
# BY DEFAULT THEY TAKE ITEMS FROM THE ENTITY THEY ARE PLACED NEXT TO
target_insterter = rotate_entity(target_insterter, Direction.DOWN)
print(f"Placed chest inserter at {target_inserter.position}") #Position (x = 21, y = 20)
```

POLICY 2: Connect drill and chest inserter with transport belts

```python 
# get the drill and chest inserter entities
drill = get_entity(Prototype.BurnerMiningDrill, position = Position(x = 0, y = 10))
target_inserter = get_entity(Prototype.BurnerInserter, position = Position (x = 21, y = 20))
# finally need to cnnect the drop position of the drill to the pickup position of target_inserter
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
belt = connect_entities(drill.drop_position, target_insterter.pickup_position, 
    Prototype.TransportBelt)

# wait for 10 seconds to check if the target entity has ore
sleep(10)
# Then we get the new updated chest entity
chest = get_entity(Prototype.WoodenChest, position = Position(x = 20, y = 20))
# get the chest inventory
chest_inventory = inspect_inventory(chest)
# get the iron ore amount
# We use Resource.IronOre as iron ore is not a prototype but a resource
iron_ore_in_chest = chest_inventory[Resource.IronOre]
print(f"Found {iron_ore_in_chest} ore in chest")
assert iron_ore_in_chest>0, "No iron ore found in chest, connection doesnt work"

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
- Use `drop_position` when connecting output of one entity to another:
```python

miner = place_entity(Prototype.BurnerMiningDrill, position=ore_position)
belts = connect_entities(
    miner.drop_position,
    target_entity.pickup_position,
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

### 4. Entity Chain Construction
When building chains of entities, follow this pattern:
1. Place primary producer (e.g., mining drill) NB: Mining drills do not need inserts, they have a drop position
2. Place destination entity (e.g., furnace) sufficiently far (eg 10 spaces)
3. Place inserters if required into the destination entity
4. Place connectors (e.g.belts, pipes)
5. Add fuel/resources

This long task should also be split into multiple policies
POLICY 1 - Set up drill and furnace
```python
# Example mining-plate-to-chest chain
# get iron ore location
ore_position = nearest(Resource.IronOre)
move_to(ore_position)
drill = place_entity(Prototype.BurnerMiningDrill, position=ore_position)
print(f"Placed drill at {drill.position}") # Position(x = 11, y = -10)
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

POLICY 2 - Set up chest with inserter and connect
```python
# get the furnace output inserter entity
furnace_output_inserter = get_entity(Prototype.BurnerInserter, position = Position(x = 9, y = -10))

# Put chest 10 steps away from the furnace_output_inserter
target_chest = place_entity(Prototype.WoodenChest,
    position=Position(x = furnace_output_inserter.position.x, y = furnace_output_inserter.position.y+10))
print(f"Placed target_chest at {target_chest.position}")


# put a inserter next to the chest
# always use 0 spacing for inserters
chest_input_inserter = place_entity_next_to(Prototype.BurnerInserter,
    reference_position=target_chest.position,
    direction=Direction.RIGHT,
    spacing = 0)

# rotate the inserter as we need to put items into the chest
chest_input_inserter = rotate_entity(chest_input_inserter, direction = Direction.LEFT)
# fuel the inserter
# we also update the inserter variable by returning it from the function
# This ensures it doesnt get stale and the inventory updates are represented in the variable
chest_input_inserter = insert_item(Prototype.Coal, chest_input_inserter, quantity=20)

# connect the furnace output inserter to chest input inserter
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
connect_entities(furnace_output_inserter.drop_position, chest_inserter.pickup_position Prototype.TransportBelt)
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
NB: ALWAYS USE INSERTERS TO INSERT ITEMS INTO DESTINATION

```python
source_position = nearest(Resource.Coal)
# Belt system pattern
move_to(source_position)
source = place_entity(Prototype.BurnerMiningDrill, position=source_position)
print(f"Placed source at {source.position}")
# put destination 10 spaces away
destination_chest = place_entity(Prototype.Chest, 
    position=Position(x = source.position.x + 10, y = source.position.y))
# add inserter
# always use 0 spacing for inserters
destination_inserter = place_entity_next_to(Prototype.BurnerInserter, 
    reference_position=destination_chest.position,
    direction=Direction.LEFT,
    spacing = 0)
print(f"Placed destination_inserter at {destination_inserter.position}")
# VERY IMPORTANT: rotate inserter as by default the inserter takes items from the entity it is placed next to
# We want it to put items into chest
destination_inserter = rotate_entity(destination_inserter, Direction.RIGHT)  # Face inserter toward drill
# IMPORTANT: ALWAYS NEED TO CONNECT TRANSPORT BELTS TO A INSERTER, NEVER DIRECTLY CONNECT TO A CHEST OR FURNACE
belt = connect_entities(source.drop_position, destination_inserter.pickup_position, 
    Prototype.TransportBelt)
```

### 7. Finding Valid Build Locations with nearest_buildable

The nearest_buildable function helps find valid positions to place entities, especially when dealing with resource patches or complex multi-entity layouts:

```python
# Basic usage - find nearest position to place a single entity
position = nearest_buildable(Prototype.BurnerMiningDrill)
drill = place_entity(Prototype.BurnerMiningDrill, position=position)

# Find position for a group of entities using bounding box
drill_layout = BoundingBox(
    left_top=Position(x=0, y=0),
    right_bottom=Position(x=10, y=5),  # Space for multiple drills
    center=Position(x=5, y=2.5)
)
valid_position = nearest_buildable(
    Prototype.ElectricMiningDrill,
    bounding_box=drill_layout
)
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
2. **Space Validation**: Ensures enough clear space for different factory sections, eg smelting area 10 spaces away from mining area

#### Common Patterns

1. **Mining Setup**:
```python
# Find space for a line of 3 miners
mining_area = BoundingBox(
    left_top=Position(x=0, y=0),
    right_bottom=Position(x=9, y=3),  # 3x3 space for each miner
    center=Position(x=4.5, y=1.5)
)
start_pos = nearest_buildable(
    Prototype.ElectricMiningDrill,
    bounding_box=mining_area
)

# Place miners in a line
for i in range(3):
    drill_pos = Position(x=start_pos.x + i*3, y=start_pos.y)
    place_entity(Prototype.ElectricMiningDrill, position=drill_pos)
```

2. **Factory Layout**:
```python
# Find space for a furnace array with belts
layout_box = BoundingBox(
    left_top=Position(x=0, y=0),
    right_bottom=Position(x=15, y=5),  # Space for furnaces and belts
    center=Position(x=7.5, y=2.5)
)
origin = nearest_buildable(
    Prototype.StoneFurnace, 
    bounding_box=layout_box
)

# Use returned position as reference for layout
furnace = place_entity(Prototype.StoneFurnace, position=origin)
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

2. **Resource Patches**:
- Use with get_resource_patch to validate ore coverage
- Check patch size against bounding box
```python
patch = get_resource_patch(Resource.IronOre, nearest(Resource.IronOre))
if patch.size > mining_area.area:  # Check if patch can support layout
    position = nearest_buildable(
        Prototype.ElectricMiningDrill, 
        bounding_box=mining_area
    )
```

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
coal_patch = get_resource_patch(Resource.Coal, nearest(Resource.Coal))
move_to(coal_patch.bounding_box.center)

# 2. Place mining drill
drill = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, coal_patch.bounding_box.center)
print(f"Placed drill at {drill.position}")

# 3. Place inserter to feed coal back into drill
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
    
    # 1. Place drills and their inserters
    for i in range(num_drills):
        # Calculate positions with proper spacing
        drill_position = Position(
            x=coal_patch.bounding_box.left_top.x + i * 2,
            y=coal_patch.bounding_box.center.y
        )
        
        # Place and configure each drill
        drill = place_entity(
            Prototype.BurnerMiningDrill,
            Direction.DOWN,
            drill_position
        )
        
        # Place and configure inserter for fuel
        # always use 0 spacing for inserters
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

5. **Alternative Designs**
   ```python
   # Using chest as buffer
   chest = place_entity(
       Prototype.IronChest,
       Direction.RIGHT,
       drill.drop_position
   )

   inserter = place_entity_next_to(
       Prototype.BurnerInserter,
       chest.position,
       direction=Direction.UP,
       spacing = 0
   )
   #VERY IMPORTANT: rotate inserter to put items into the chest
   inserter = rotate_entity(inserter, Direction.DOWN)
   ```

#### Common Patterns

1. **Linear Mining Array**
   - Place drills in a straight line
   - Use shared belt system
   - Single fuel distribution loop

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
- To create resource mines (stone, coal, iron ore, copper ore), you first need to place burner or electric mining drills as a starting point. Then you need a chest or furnace as an ending point and need to place a burner inserter next to the ending point, that will insert the entities into the ending point. Finally you need to connect the drills drop point with transport belts to the inserters pickup position 
- IMPORTANT: ALWAYS USE INSERTERS WHEN YOU NEED TO INPUT ITEMS INTO CHESTS, FURNACES OR ASSEMBLY MACHINES. NEVER CONNECT TO THE CHEST DIRECTLY
- When mines are created, the ending point cannot be next to the starting point because of collisions. A rule of thumb is atleast 10 tiles away from the mine start position
- IMPORTANT: When placing inserters, they by default take items from the entity they are placed next to. They need to be rotated 180 degrees to put items into the entity they are next to
- To create a working assembling machine for automatic crafting structures (e.g automatic iron gear wheel mine), the assembling machine must be put down, the recipe of the machine must be set, the machine must be powered with electricity, inserters must insert crafting ingredients (iron plates for iron gear wheel) into the machine and one inserter must take the final product (e.g iron gear wheel) out of the machine
- When a entity has status "WAITING_FOR_SPACE_IN_DESTINATION", it means the there is no space in the drop position. For instance, a mining drill will have status WAITING_FOR_SPACE_IN_DESTINATION when the entities it mines are not being properly transported away from drop position with transport belts
- Make sure to always put enough fuel into all entities that require fuel. It's easy to mine more coal, so it's better to insert in abundance 