Some examples of steps are as follows

Global objective
Create a automatic iron ore mining setup into a chest
Map setup
There is one chest at position (17.5, -26.5)
Initial inventory
{{}}
General plan
Here's a general plan to create a burner iron ore mine into a chest:\n\n1. Locate the nearest iron ore patch.\n2. Place a burner mining drill on the iron ore patch.\n3. Fuel the burner mining drill with coal.\n4. Locate the wooden chest at position (17.5, -26.5).\n5. Place an inserter next to the chest to insert items into it.\n6. Rotate the inserter to face the chest.\n7. Fuel the inserter with coal.\n8. Connect the burner mining drill to the inserter using transport belts.\n9. Verify that the setup is working by checking if iron ore is being mined and placed into the chest.

Output 1
PLANNING
To accurately get the number of entities, we need to calculate the distance from the wooden chest at position (17.5, -26.5) to the nearest iron ore patch
OUTPUT
#COMMAND
Print the nearest iron ore patch and calculate the amount of transport belts required for the connection between that and the chest at position (17.5, -26.5) using the get_connection_amount function to get the amount. Only print out the amount required, nothing else, do not check existing ones
#COMMMAND

Output after analysing the result of #COMMAND of output 1
PLANNING
Analysing the general plan, we need one burner mining drill, one burner inserter, 42 transport belts and 10 coal
OUTPUT
#ENTITIES
Burner mining drill - 1
Burner inserter - 1
Transport belts - 42
coal - 10
#ENTITIES

Global objective
Craft 5 offshore pumps
Map setup
There are some entities on the map that you can use
Initial inventory
{{}}
General plan
Here's a general plan to achieve the objective of getting 5 offshore pumps:\n\n1. Print the recipe for offshore pumps:\n   - Each offshore pump requires 1 iron gear wheel, 2 electronic circuits, and 1 pipe.\n   - In total, we need 5 iron gear wheels, 10 electronic circuits, and 5 pipes for 5 offshore pumps.\n\n2. Gather resources from the existing chests:\n   - Move to the chest at position (3.5, 27.5).\n   - Extract 10 electronic circuits from the chest.\n   - Extract 19 coal from the chest for fueling furnaces.\n   - Extract 5 stone from the chest for crafting a stone furnace.\n   - Extract 1 iron plate from the chest.\n   - Extract 5 iron ore from the chest at position (-16.5, -16.5).\n\n3. Craft and set up a stone furnace:\n   - Craft 1 stone furnace using the 5 stone.\n   - Place the stone furnace at a convenient location (e.g., origin or near a chest).\n   - Fuel the furnace with 5 coal.\n\n4. Smelt iron plates:\n   - Insert 5 iron ore into the stone furnace.\n   - Wait for the smelting process to complete (approximately 3.5 seconds for 5 iron plates).\n   - Extract the 5 iron plates from the furnace.\n\n5. Craft intermediate components:\n   - Craft 5 iron gear wheels using 5 iron plates.\n   - Craft 5 pipes using 5 iron plates.\n\n6. Craft the offshore pumps:\n   - Ensure we have all the required materials: 5 iron gear wheels, 10 electronic circuits, and 5 pipes.\n   - Craft 5 offshore pumps.\n\n7. Verify the result:\n   - Check the inventory to confirm we have 5 offshore pumps.\n\nThis plan takes into account the existing resources in the chests, minimizes the need for additional resource gathering, and ensures we have all the necessary components to craft the offshore pumps.

Output 1
PLANNING
We need to craft 5 offshore pumps. There are no offshore pumps on the map so we need to craft them. The only entity we need from the plan is a stone furnace
OUTPUT
#ENTITIES
Stone furnace - 1
#ENTITIES


Global objective
{objective}
General plan
{plan}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
Previous agent outputs
{logs}
Generate the required entities for the global objective