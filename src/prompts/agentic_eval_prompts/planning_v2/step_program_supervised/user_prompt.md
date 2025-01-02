Examples of API usage to achieve various tasks

Example task
Print out the recipes of a 3 boilers and 5 iron pipes
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

Example task
Mine 25 iron ore
```python
"""
Step 1: 
Get the iron ore patch position and move to it
"""
iron_position = nearest(Resource.IronOre)
# move to the iron position as you need to be close to the entities to interact with them
move_to(iron_position)

"""
Step 2
Harvest 25 iron ore
"""
harvested_iron = harvest_resource(iron_position, 25)
print(f"Mined {{harvested_iron}} iron ore")
```

Example task
Get the copper plates from the chest and craft 5 copper cables
Mining setup
The following entities are on the map [{{"name": "wooden-chest", "type": Prototype.WoodenChest, "inventory": [("copper-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}
```python
"""
Step 1: 
Get the copper plates from the chest at Position(x = 0, y = 1) 
"""
# first get the chest entity
chest = get_entity(Prototype.WoodenChest, Position(x = 0, y = 1))
# move to the chest as you need to be close to the entities to interact with them
move_to(chest.position)
"""
Step 2
Get the 10 copper plates from the chest
"""
extract_item(Prototype.CopperPlate, chest.position, 10)
# check that we got the correct amount in player inventory
copper_plates_in_inventory = inspect_inventory()[Prototype.CopperPlate]
assert copper_plates_in_inventory>=10

"""
Step 3
Craft the 5 copper cable
"""
craft_item(Prototype.CopperCable, 5)
```

Example task
Smelt 25 iron plates
Mining setup
There are no entities on the map
Initial inventory
{{"iron-ore": 25, "coal": 10}}
```python
"""
Step 1: 
As there are no furnaces on the map, we need to craft one
The recipe for stone furnace is 5 stone
We need to get 5 stone and then craft the Prototype.StoneFurnace
"""
# First move to the stone position and harvest 5 stone
stone_position = nearest(Resource.Stone)
# move to the stone position as you need to be close to the entities to interact with them
move_to(stone_position)
# harvest 5 stone
harvested_stone = harvest_resource(stone_position, 5)
print(f"Mined {{harvested_stone}} stone")
# craft the stone furnace
craft_item(Prototype.StoneFurnace, 1)
"""
Step 2
Place the stone furnace at Position (x = 1, y = 0)
"""
furnace_position = Position(x = 1, y=0)
# first move to the stone furnace position
move_to(furnace_position)
place_entity(Prototype.StoneFurnace, Direction.UP, furnace_position)


"""
Step 3
Smelt the 25 iron ore
"""
expected_iron_plates = 25
# Fuel the Stone Furnace with coal
coal_to_insert = 10
# get the furnace entity
furnace = get_entity(Prototype.StoneFurnace, furnace_position)
# insert the 10 coal
# We also need to update the entity when we insert into it 
furnace = insert_item(Prototype.Coal, furnace, coal_to_insert)
print(f"Inserted {{coal_to_insert}} coal into the Stone Furnace")

# Insert iron ore into the Stone Furnace
iron_ore_to_insert = inspect_inventory()[Resource.IronOre]
# We need to update the entity when we insert into it
furnace = insert_item(Prototype.IronOre, furnace, iron_ore_to_insert)
print(f"Inserted {{iron_ore_to_insert}} iron ore into the Stone Furnace")

# Wait for smelting to complete (0.7 seconds per iron ore)
sleep(iron_ore_to_insert * 0.7)

# Extract iron plates from the Stone Furnace
expected_iron_plates = iron_ore_to_insert  # Assuming 1:1 ratio for ore to plate
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.IronPlate, furnace.position, expected_iron_plates)
    iron_plates_in_inventory = inspect_inventory()[Prototype.IronPlate]
    if iron_plates_in_inventory >= expected_iron_plates:
        break
    sleep(5)  # Wait a bit more if not all plates are ready

print(f"Extracted {{iron_plates_in_inventory}} iron plates from the Stone Furnace")

# Check if we have the expected number of iron plates
assert iron_plates_in_inventory >= expected_iron_plates, f"Failed to smelt enough iron plates. Expected {{expected_iron_plates}}, but got {{iron_plates_in_inventory}}"

print(f"Successfully crafted Stone Furnace and smelted {{iron_plates_in_inventory}} iron plates")
```


Example task
Put down the burner mining drill on the iron patch at Position(x= 10, y = 10) and fuel it with 30 coal
Mining setup
There are no entities on the map
Initial inventory
{{"iron-ore": 25, "coal": 40, "burner-mining-drill": 3, "burner-inserter": 3, "copper-plate": 112}}
```python
"""
Step 1: 
We first need to move to the iron patch. 
We are given the position so we do not need to find it out ourselves
"""
# First move to the iron position 
iron_position = Position(x= 10, y = 10)
# move to the iron position as you need to be close to the entities to interact with them
move_to(iron_position)

"""
Step 2
Place the burner mining drill and fuel it with 30 coal
"""
place_entity(Prototype.BurnerMiningDrill, Direction.UP, iron_position)
# get the new burner mining drill entity
drill = get_entity(Prototype.BurnerMiningDrill, iron_position)
print(f"Placed a drill at position {{drill.position}}")
# insert the 30 coal
# We also need to update the entity when we insert into it 
drill = insert_item(Prototype.Coal, furnace, 30)
print(f"Inserted 30 coal into the drill")
```

Example task
Put a burner inserter next to the chest at Position(x = 0, y = 1) and rotate the burner inserter 180 degrees to face the chest such that it puts items into the chest not takes from them. Fuel the burner inserter with 10 coal
Mining setup
The following entities are on the map [{{"name": "wooden-chest", "type": Prototype.WoodenChest, "inventory": [("copper-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{"iron-ore": 25, "coal": 40, "burner-mining-drill": 3, "burner-inserter": 3, "copper-plate": 112}}
```python
"""
Step 1: 
We first need to move to the chest. 
We need to get the chest entity and then move to it
"""
# First get the chest entity
chest = get_entity(Prototype.WoodenChest, Position(x = 0, y = 1))
# move to the chest position as you need to be close to the entities to interact with them
move_to(chest.position)

"""
Step 2
Place the burner inserter next to the chest, rotate it and fuel it with 10 coal
"""
# place the inserter
# We also get the new inserter entity as the position is relative
# We use 0 spacing as we want it to be right next to the reference chest position
chest_inserter = place_entity_next_to(Prototype.BurnerInserter, spacing = 0, direction = direction.UP, reference_position = chest.position)
print(f"Placed an inserter at {{chest_inserter.position}} next to the chest")
# rotate the chest inserter
# By default inserters take items not put items into entities so we need to rotate them
chest_inserter = rotate_entity(chest_inserter, direction = direction.DOWN)
print(f"Rotated the inserter to input items into the chest at position {{chest_inserter.position}}")
# insert the 10 coal
# We also need to update the entity when we insert into it 
chest_inserter = insert_item(Prototype.Coal, chest_inserter, 10)
print(f"Inserted 10 coal into the chest inserter")
```

Example task
Calculate and print out the amount of connections needed to connect the mining drills (Position(x = 10, y = 10)) drop position with the pickup position of the burner inserter next to the chest at Position(x = 19, y = 10). Check if you have enough in inventory
Mining setup
The following entities are on the map [{{"name": "wooden-chest", "type": Prototype.WoodenChest, "inventory": [("copper-plate", 10)], "position": Position(x = 20, y = 10)}}, {{"name": "burner-inserter", "type": Prototype.BurnerInserter, "position": Position(x = 19, y = 10)}}, {{"name": "burner-mining-drill", "type": Prototype.BurnerMiningDrill, "position": Position(x = 10, y = 10)}}]
Initial inventory
{{"iron-ore": 25, "coal": 40, "burner-mining-drill": 3, "burner-inserter": 3, "copper-plate": 112, "transport-belt": 50}}
```python
"""
Step 1: 
We first need to calculate the amount of transport belts needed to connect the drills drop position and the chest
"""
# First get the drill entity
drill = get_entity(Prototype.BurnerMiningDrill, Position(x = 10, y = 10))
# Then get the burner inserter entity
inserter = get_entity(Prototype.BurnerInserter, Position(x = 19, y = 10))
# Then get the amount of tansport belts needed
amount_needed = get_connection_amount(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)
print(f"Transport belts required {{amount_needed}}")
"""
Step 2: 
Check if we have enough transport belts in our inventory
"""
belts_in_inventory = copper_plates_in_inventory = inspect_inventory()[Prototype.TransportBelt]
if belts_in_inventory >= amount_needed:
    print(f"We have enough transport belts for the connection")
else:
    print(f"We do not have enougn transport belts. Needed {{amount_needed}}, currently in inventory {{belts_in_inventory}}. Need {{amount_needed - belts_in_inventory}} more")
```

Example task
Connect the mining drills (Position(x = 10, y = 10)) drop position with the pickup position of the burner inserter at Position(x = 19, y = 10) that puts items into the chest. Wait for 10 seconds and check if iron ore is transported to the furnace
Mining setup
The following entities are on the map [{{"name": "wooden-chest", "type": Prototype.WoodenChest, "inventory": [("copper-plate", 10)], "position": Position(x = 20, y = 10)}}, {{"name": "burner-inserter", "type": Prototype.BurnerInserter, "position": Position(x = 19, y = 10)}}, {{"name": "burner-mining-drill", "type": Prototype.BurnerMiningDrill, "position": Position(x = 10, y = 10)}}]
Initial inventory
{{"iron-ore": 25, "coal": 40, "burner-mining-drill": 3, "burner-inserter": 3, "copper-plate": 112, "transport-belt": 50}}
```python
"""
Step 1: 
We first need to get the drill and burner inserter entities
They are the starting and end points of the connections
"""
# First get the drill entity
drill = get_entity(Prototype.BurnerMiningDrill, Position(x = 10, y = 10))
# Then get the burner inserter entity
inserter = get_entity(Prototype.BurnerInserter, Position(x = 19, y = 10))

"""
Step 2: 
Connect the drill and inserter with each other
We will use the transport belts we have in our inventory
We already have enough transport belts as the distance is less than 20 tiles but we have 50 which is more than enough
"""
connect_entities(source = drill.drop_position, target = inserter.pickup_position, connection_type = Prototype.TransportBelt)
print(f"Connected the drill at {{drill.position}} with the burner inserter at {{inserter.position}} with transport belts")

"""
Step 3: 
Wait for 10 seconds and check if the chest has iron ore in it
After sleeping we first get the chest inventory and then check for ore
"""
# first sleep for 10 seconds
sleep(10)
# Then we get the new chest entity
chest = get_entity(Prototype.WoodenChest, position = Position(x = 20, y = 10))
# get the chest inventory
chest_inventory = inspect_inventory(chest)
# get the iron ore
# We use Resource.IronOre as irn ore is not a prototype but a resource
iron_ore_in_chest = chest_inventory[Resource.IronOre]
assert iron_ore_in_chest>0, "No iron ore found in chest"
print(f"Iron ore has been found in chest at {{chest.position}}. Connection has been successful")

```


Your starting inventory is {starting_inventory}.
Your initial mining setup is: {mining_setup}.
Previous tasks that have been carried out
{game_logs}

Create a step by step plan and a python script that achieves the following task
{task}

