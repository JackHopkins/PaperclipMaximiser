Some examples of steps are as follows

Global objective
Create a automatic iron plate mining setup into a chest
Map setup
There are no entities on the map
Initial inventory
{{}}
Steps
Step 1 - #STEP Calculate all the ingredients and print out all the recipes required to craft for 1 burner mining drill, 1 burner inserter, 1 wooden chest, 1 stone furnace and 50 transport belts. Do not craft anything, only print out the requirements #STEP
Step 2 - #STEP Get 87 iron plates, 10 stone and 2 wood #STEP
Step 3 - #STEP Craft for 1 burner mining drill, 1 burner inserter, 1 stone furnace, 1 wooden chest and 50 transport belts #STEP
Step 4 - #STEP Put down the drill at the iron ore location and a furnace at the drop position of the drill. Add coal to the furnace and drill. Print out the drill and furnace position #STEP
Step 5 - #STEP Put a inserter that takes items from the furnace. Add coal to the inserter. Print out the drill and furnace position #STEP
Step 6 - #STEP Put down a chest 10 steps away from the furnace and a inserter that puts items into the chest and rotate it. Add coal to the inserter. Print out chests position #STEP
Step 7 - #STEP Connect the furnace inserter to the chests inserter with transport belts. Check that plates are correctly sent to the chest #STEP
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
There are no entities on the map
Initial inventory
{{"burner-mining-drill": 3,
                            "stone-furnace": 9,
                            "transport-belt": 100,
                            "burner-inserter": 5,
                            "wooden-chest": 2,
                            "coal": 10}}
Steps
Step 1 - #STEP Put down the drill at the coal location. Add coal to the drill. Print out the drill #STEP
Step 2 - #STEP Put down the chest approximately 10 tiles away from the drill and the inserter that puts items into the chest and rotate it. Add coal to the inserter. Print out chests position #STEP
Step 3 - #STEP Connect the drills drop position to the chests inserter with transport belts. Check that coal is correctly sent to the chest #STEP
#OUTPUT An automatic coal mine has been created to the drill at Position(x = 11, y = 12) to the chest at Position(x = 5, y = 9) #OUTPUT


Generate the next step for the following objective
{objective}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
Game Logs
{logs}