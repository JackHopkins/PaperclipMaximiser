Some examples of steps are as follows

Global objective
Create a automatic iron plate mining setup into a chest
Map setup
There are no entities on the map
Initial inventory
{{}}
Steps
Step 1 - #STEP Print out the location of the nearest iron patch #STEP
Step 2 - #STEP Calculate all the ingredients and print out all the recipes required to craft for 1 burner mining drill, 1 burner inserter, 1 wooden chest, 1 stone furnace and 50 transport belts. Do not craft anything, only print out the requirements #STEP
Step 3 - #STEP Get 87 iron plates, 10 stone and 2 wood #STEP
Step 4 - #STEP Craft for 1 burner mining drill, 1 burner inserter, 1 stone furnace, 1 wooden chest and 50 transport belts #STEP
Step 6 - #STEP Create a iron plate mine from a drill at Position(x = 11, y = 12) to a chest 10 spaces away. Check the construct by looking if the chest has iron plates in them #STEP
#OUTPUT An automatic iron plate mine has been created to the drill at Position(x = 11, y = 12) to the chest at Position(x = 5, y = 9) #OUTPUT

Global objective
Craft 5 offshore pumps
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}
Steps
Step 1 - #STEP Calculate all the ingredients and print out all the recipes required to craft for 5 offshore pumps. Do not craft anything, only print out the requirements #STEP
Step 2 - #STEP Get the 10 iron plates from the chest at Position(x = 0, y = 1) and get 25 more iron plates #STEP
Step 3 - #STEP Craft for 5 offshore pumps #STEP
#OUTPUT 5 offshore pumps have been created #OUTPUT

Global objective
Create a automatic coal mining setup into a chest
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{"burner-mining-drill": 3,
                            "stone-furnace": 9,
                            "transport-belt": 150,
                            "burner-inserter": 5,
                            "coal": 10}}
Steps
Step 1 - #STEP Print out the location of the nearest coal patch and calculate the distance from that to the chest at Position(x = 0, y = 1) using the get_connection_amount function. Print out if we have enough transport belts to cover the distance #STEP
Step 2 - #STEP Create a coal mine from a drill at center of coal patch to a chest placed 10 spaces away. Check the coal mine by looking if the chest has coal #STEP
#OUTPUT An automatic coal mine has been created to the drill at Position(x = 11, y = 12) to the chest at Position(x = 5, y = 9) #OUTPUT

Global objective
Move iron ore from the chest to the furnace to smelt it
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-ore", 10),("burner-inserter", 5), ("transport-belt": 50)], "position": Position(x = 0, y = 1)}}, {{"name": "stone-furnace", "position": Position(x = 12, y = 1)}}]
Initial inventory
{{}}
Steps
Step 1 - #STEP Get the burner inserters and transport belts from the chest at Position(x = 0, y =  1). #STEP
Step 2 - #STEP Calculate the distance between Position(x = 0, y = 1) and Position(x = 12, y = 1) using get_connection_amount function. Print out if there are enough transport belts to make the connection #STEP
Step 2 - #STEP Create a connection that moves iron ore from chest at Position(x=0, y=1) to the furnace at Position(x=12, y=1). Check the connection by looking if the furnace has smelted iron plates in it #STEP
#OUTPUT Connection that moves items from chest at Position(x=0, y=1) to furnace at Position(x=12, y=1) has been created #OUTPUT


Generate the next step for the following objective
{objective}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
You have also been given a analysis of required entities for the objective
{entity_analysis}
Game Logs
{logs}