Some examples of steps are as follows

Global objective
Create a automatic iron plate mining setup into a chest
Map setup
There are no entities on the map
Initial inventory
{{}}
Objective analysis
To create an automatic iron plate mine into a chest we need a burner mining drill, inserters, transport belts and a furnace. As there are no entities on the map, we need to place a chest on the map where the plates will be sent to. We then need one burner mining drill, two inserters for the chest and furnace, one chest that we will put 10 spaces away from the drill, one stone furnace for the plates and 20 transport belts to move items from the furnace to the chest (we know the exact number as we know we will place the final chest 10 tiles away). We then need to create the plate mining setup from a burner mining drill to a chest we place 10 steps away
Required entities
Burner mining drill - 1, needs to be crafted
Burner inserter - 2, needs to be crafted
Transport belts - 20, needs to be crafted
Wooden chest - 1, needs to be crafted
Stone furnace - 1, needs to be crafted

Global objective
Craft 5 offshore pumps
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-plate", 10)], "position": Position(x = 0, y = 1)}}]
Initial inventory
{{}}
Objective analysis
We need to craft 5 offshore pumps. There are no offshore pumps on the map so we need to craft them
Required entities
offshore pumps - 5, need to be crafted

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
Objective analysis
To create an automatic coal mine into a chest we need a burner mining drill, inserters, transport belts. As there are no entities on the map, we need to place a chest on the map where the plates will be sent to. We then need one burner mining drill, one inserter for the chest, one chest that we will put 10 spaces away from the drill and 20 transport belts to move items from the drill to the chest (we know the exact number as we know we will place the final chest 10 tiles away). We then need to create the coal mining setup from a burner mining drill to a chest we place 10 steps away
Required entities
Burner mining drill - 1, in our inventory
Burner inserter - 2, in our inventory
Transport belts - 20, in our inventory
Wooden chest - 1, in our inventory

Global objective
Move iron ore from the chest to the furnace to smelt it
Map setup
The following entities are on the map [{{"name": "wooden-chest", "inventory": [("iron-ore", 10),("burner-inserter", 5), ("transport-belt": 50)], "position": Position(x = 0, y = 1)}}, {{"name": "stone-furnace", "position": Position(x = 12, y = 1)}}]
Initial inventory
{{}}
Objective analysis
To move iron ore from the chest to the furnace on the map to smelt it we need inserters and transport belts. Both entities are on the map so we need to only inserters and transport belts. We need 2 inserts, one to take items from the chest and other to put items into the furnace. We also need transport belts but we need to calculate the amount of transport belts. We have 50 transport belts in the chest at Position(x = 0, y = 1) but might need more, this needs to be calculated precicely later
Required entities
Transport belts - amount unknown. The precise amount needs to be calculated. If less than 50, can use belts directly from the chest at Position(x = 0, y = 1), all belts more than 50 need to be additionally calculated
Burner inserter - 2, in inventory of chest at Position(x = 0, y = 1)

Global Objective
{objective}
Mining setup
{mining_setup}
Inventory
{starting_inventory}
Here's a more detailed plan of the objective for the current map
{objective}
Generate the Objective analysis and the required entities for the global objective.