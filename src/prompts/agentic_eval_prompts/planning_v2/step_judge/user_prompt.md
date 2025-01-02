Some examples of steps are as follows:

Global objective
Create a mine that automatically smelts iron plates
Map setup
There are no entities on the map
Initial inventory
{{"burner-inserter": 1, "iron-plate": 15}}
Steps
Step 1 - <step>Calculate all the ingredients and print out all the recipes required to craft for 1 burner mining drill, 1 stone furnace and 50 transport belts. </step>
Step 2 - <step>Calculate all the ingredients and print out all the recipes required to craft iron gear wheels. </step>
Step 3 - <step>Gather 160 iron ore, 20 stone, 6 wood and 80 coal for fuel for the mine</step>
Step 4 - <step>Craft one stone furnace for smelting and smelt 160 iron plates </step>
Step 5 - <step>Craft 1 burner mining drill, 1 stone furnace for mining operation, and 50 transport belts </step>
Step 6 - <step>Print out the location of the iron ore patch and place a furnace 10 tiles away. Print out the location of the furnace</step>
Step 7 - <step>Put down the burner mining drill on the iron patch at Position(x= 10, y = 10) and fuel the burner mining drill with 30 coal</step>
Step 8 - <step>Put a burner inserter next to the furnace at Position(x = 20, y = 10) and rotate the burner inserter 180 degrees to face the furnace such that it puts items into the furnace not takes from them. Fuel the furnace and the burner inserter with 10 coal each</step>
Step 9 - <step>Calculate and print out the amount of connections needed to connect the mining drills (Position(x = 10, y = 10)) drop position with the pickup position of the burner inserter next to the furnace at Position(x = 11, y = 10). Check if you have enough in inventory</step>
Step 10 - <step>Connect the mining drills (Position(x = 10, y = 10)) drop position with the pickup position of the burner inserter next to the furnace at Position(x = 11, y = 10). Wait for 10 seconds and check if iron ore is transported to the furnace</step>
Step 11 - <objective_completed>An automatic iron plate mine has been created to the drill at Position(x = 10, y = 10) to the furnace at Position(x = 20, y = 10) </objective_completed>

Global objective
Craft 5 offshore pumps
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}
Steps
Step 1 - <step>Calculate all the ingredients and print out all the recipes required to craft for 5 offshore pumps</step>
Step 2 - <step>Get the 10 iron plates from the chest at Position(x = 0, y = 1)</step>
Step 3 - <step>Gather 25 iron ore and smelt 25 iron plates</step>
Step 3 - <step>Craft for 5 offshore pumps </step>


Here is the global objective
{objective}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
Game Logs
{logs}

Here are the candidate input steps to analyse
{analysis_step_str}

Output the analysis and your final step