Some examples of steps are as follows:

Global objective
Create a mine that automatically smelts iron plates
Map setup
There are no entities on the map
Initial inventory
{{"burner-inserter": 1, "iron-plate": 15}}
Steps
Step 1 - <step>Calculate all the ingredients and print out all the recipes required to craft for 1 burner mining drill, 1 stone furnace and 50 transport belts. Do not craft anything, only print out the requirements </step>
Step 2 - <step>Gather 87 iron ore, 10 stone, 6 wood  and 40 coal for fuel</step>
Step 3 - <step>Smelt 87 iron plates </step>
Step 4 - <step>Craft for 1 burner mining drill, 1 stone furnace, and 50 transport belts </step>
Step 5 - <step>Print out the location of the iron ore patch and place a furnace 10 tiles away. Print out the location of the furnace</step>
Step 6 - <step>Put down the burner mining drill on the iron patch at Position(x= 10, y = 10) and fuel the burner mining drill with 10 coal</step>
Step 7 - <step>Put a burner inserter next to the furnace at Position(x = 20, y = 10) and rotate the burner inserter 180 degrees to face the furnace such that it puts items int furnace not takes from them. Fuel the furnace and the burner inserter with 10 coal each</step>
Step 8 - <step>Connect the mining drills (Position(x = 10, y = 10)) drop position with the pickup position of the burner inserter next to the furnace at Position(x = 11, y = 10). Wait for 10 seconds and check if iron ore is transported to the furnace</step>
<output>An automatic iron plate mine has been created to the drill at Position(x = 10, y = 10) to the furnace at Position(x = 20, y = 10) </output>

Global objective
Craft 5 offshore pumps
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}
Steps
Step 1 - <step>Calculate all the ingredients and print out all the recipes required to craft for 5 offshore pumps. Do not craft anything, only print out the requirements </step>
Step 2 - <step>Get the 10 iron plates from the chest at Position(x = 0, y = 1)</step>
Step 3 - <step>Gather 25 iron ore and smelt 25 iron plates</step>
Step 3 - <step>Craft for 5 offshore pumps </step>
<output>5 offshore pumps have been created </output>


Here is the global objective
{objective}
Here are the previous steps the agents have done
{logs}
Here is the starting mining setup for all traces
{mining_setup}
Here is the starting inventory for all traces
{starting_inventory}

Here are the candidate traces to analyse
{analysis_step_str}

Output the analysis and the most likely trace