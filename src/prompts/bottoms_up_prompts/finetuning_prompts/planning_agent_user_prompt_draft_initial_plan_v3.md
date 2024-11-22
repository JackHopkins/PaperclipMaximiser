Some examples of steps are as follows

Global objective
Create a automatic iron plate mining setup into a chest
Map setup
There are no entities on the map
Initial inventory
{{}}

Output 1
PLANNING
To create an automatic iron plate mine into a chest we need a burner mining drill, inserters, transport belts and a furnace. As there are no entities on the map, we need to place a chest on the map where the plates will be sent to. We then need one burner mining drill, two inserters for the chest and furnace, one chest that we will put 10 spaces away from the drill, one stone furnace for the plates and 20 transport belts to move items from the furnace to the chest (we know the exact number as we know we will place the final chest 10 tiles away). To find out where to place the burner mining drill, we need to first print out the location of the iron ore patch
OUTPUT
#COMMAND
print out the location of the nearest iron ore patch
#COMMMAND

Output after analysing the result of #COMMAND of output 1
PLANNING
We have all the information we need for the entities
OUTPUT
#ENTITIES
Burner mining drill - 1, needs to be crafted. Will be placed on the iron ore patch at Position(x=0, y = 11)
Burner inserter - 2, need to be crafted. Will be used to with transport belts to connect furnace to chest
Transport belts - 20, needs to be crafted. Will be used to with inserters to connect furnace to chest
Wooden chest - 1, needs to be crafted. Will be placed 10 steps away from the drill
Stone furnace - 1, needs to be crafted. Will be placed at the drop position of the drill
#ENTITIES

Global objective
Craft 5 offshore pumps
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}

Output 1
PLANNING
We need to craft 5 offshore pumps. There are no offshore pumps on the map so we need to craft them
OUTPUT
#ENTITIES
offshore pumps - 5, need to be crafted
#ENTITIES


Global objective
Create a automatic coal mining setup into a chest
Map setup
There are no entities on the map
Initial inventory
{{"burner-mining-drill": 3,
                            "stone-furnace": 9,
                            "transport-belt": 100,
                            "burner-inserter": 5,
                            "wooden-chest": 2,
                            "coal": 10}}
                            
Output 1
PLANNING
To create an automatic coal mine into a chest we need a burner mining drill, inserters, transport belts. As there are no entities on the map, we need to place a chest on the map where the plates will be sent to. We then need one burner mining drill, one inserter for the chest, one chest that we will put 10 spaces away from the drill and 20 transport belts to move items from the drill to the chest (we know the exact number as we know we will place the final chest 10 tiles away). To find out where to place the burner mining drill, we need to first print out the location of the coal patch
OUTPUT
#COMMAND
print out the location of the nearest coal patch
#COMMMAND

Output after analysing the result of #COMMAND of output 1
PLANNING
We have all the information we need for the entities
OUTPUT
#ENTITIES
Burner mining drill - 1, in our inventory. Will be placed at the coal patch at Position(x= 5, y = -11)
Burner inserter - 2, in our inventory. Will be used to with transport belts to connect furnace to chest
Transport belts - 20, in our inventory. Will be used to with inserters to connect furnace to chest
Wooden chest - 1, in our inventory. Will be placed 10 steps away from the drill
#ENTITIES

Global objective
Move iron ore from the chest to the furnace to smelt it
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-ore", 10),("burner-inserter", 5), ("transport-belt": 50)], "position": Position(x = 0, y = 1)}}, {{"name": "stone-furnace", "position": Position(x = 12, y = 1)}}]
Initial inventory
{{}}

Output 1
PLANNING
To move iron ore from the chest to the furnace on the map to smelt it we need inserters and transport belts. Both entities are on the map so we need to only inserters and transport belts. We need 2 inserts, one to take items from the chest and other to put items into the furnace. We also need transport belts but we need to calculate the amount of transport belts.
OUTPUT
#COMMAND
Calculate the distance between Position(x = 0, y = 1) and Position(x = 12, y = 1) using get_connection_amount function. Print out if there are enough transport belts to make the connection
#COMMAND

Output after analysing the result of #COMMAND of output 1
PLANNING
From the logs we have found out we need 15 transport belts. We have all information for the plan
OUTPUT
#ENTITIES
Transport belts - 15, in inventory of chest at Position(x = 0, y = 1)
Burner inserter - 2, in inventory of chest at Position(x = 0, y = 1)
#ENTITIES

Global objective
{objective}
The overly detailed plan how to achieve this objective
{plan}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
Previous agent outputs
{logs}
Generate the required entities for the global objective