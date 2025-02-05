import unittest
import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")

from factorio_instance import FactorioInstance
from utils import eval_program_with_achievements
from search.model.game_state import GameState
def test_achievements():
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27000,
                                fast=True,
                                #cache_scripts=False,
                                inventory={})
        instance.speed(10)

        test_string_1 = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.IronOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.IronOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(16)\nextract_item(Prototype.IronPlate, furnace.position, 10)"
        _, _, _, achievements = eval_program_with_achievements(instance, test_string_1)
        ground_truth_achievement = {'static': {'stone-furnace': 1, 'coal': 10, 'stone': 10, 'iron-ore': 10}, 'dynamic': {'iron-plate': 5}}
       
        assert achievements == ground_truth_achievement
        test_string = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.CopperOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.CopperOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(16)"
        _, _, _, achievements = eval_program_with_achievements(instance, test_string)
        ground_truth_achievement = {'static': {'stone-furnace': 1, 'coal': 10, 'stone': 10, 'copper-ore': 10}, 'dynamic': {'copper-plate': 5}}
        assert achievements == ground_truth_achievement
        test_string = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.CopperOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.CopperOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(16)"
        _, _, _, achievements = eval_program_with_achievements(instance, test_string)
        ground_truth_achievement = {'static': {'stone-furnace': 1, 'coal': 10, 'stone': 10, 'copper-ore': 10}, 'dynamic': {'copper-plate': 5}}
        assert achievements == ground_truth_achievement






def test_achievements_1():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)
        instance.speed(10)
        

        test_string_1 = 'move_to(Position(x=10, y=10))\n \n# Place offshore pump near water\nwater_position = nearest(Resource.Water)\nassert water_position, "No water source found nearby"\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, Direction.DOWN, water_position)\nassert offshore_pump, "Failed to place offshore pump"\n# Place boiler next to offshore pump\n# Important: The boiler needs to be placed with a spacing of 2 to allow for pipe connections\nboiler = place_entity_next_to(Prototype.Boiler, offshore_pump.position, Direction.DOWN, spacing=2)\nassert boiler, "Failed to place boiler"\n# add coal to the boiler\n# need to update the boiler var after insert\nboiler = insert_item(Prototype.Coal, boiler, quantity=5)\n# Connect offshore pump to boiler with pipes\npipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nassert pipes, "Failed to connect offshore pump to boiler"\n# Place steam engine next to boiler\n# Important: The steam engine needs to be placed with a spacing of 2 to allow for pipe connections\nsteam_engine = place_entity_next_to(Prototype.SteamEngine, boiler.position, Direction.LEFT, spacing=2)\nassert steam_engine, "Failed to place steam engine"\n# Connect boiler to steam engine with pipes\npipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\nassert pipes, "Failed to connect boiler to steam engine"\n# check if the boiler is receiving electricity\n# if it says not connected to power network, then it is working\n# it just isnt connected to any power poles\nmove_to(Position(x=0, y=0))\nass_machine = place_entity(Prototype.AssemblingMachine1, Direction.UP, Position(x=0, y=0))\nconnect_entities(ass_machine, steam_engine, Prototype.SmallElectricPole)'
        _, _, _, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '"""\nLet\'s analyze what we need for an iron gear wheel factory:\n\n1. Recipe check for iron gear wheel:\n- 2 iron plates per iron gear wheel\n- For 1 iron gear wheel per minute, need 2 iron plates per minute\n- Stone furnace can produce 18 plates/min, so 1 furnace is enough\n- Need iron ore mining to feed the furnace\n- Burner mining drill (15/min) is sufficient for ore\n\n2. Steps:\na) Set up iron ore mining with burner drill\nb) Connect ore to furnace with inserter/belt\nc) Connect plates to assembling machine\nd) Power the assembling machine\ne) Set up output collection\n\nLet\'s implement step by step:\n"""\n\n# First find iron ore patch\niron_pos = nearest(Resource.IronOre)\nmove_to(iron_pos)\n\n# Place burner mining drill\ndrill = place_entity(Prototype.BurnerMiningDrill, position=iron_pos)\n# Add initial fuel\ninsert_item(Prototype.Coal, drill, quantity=5)\n\n# Place furnace with some spacing for belts\nfurnace = place_entity_next_to(\n    Prototype.StoneFurnace,\n    reference_position=drill.position,\n    direction=Direction.RIGHT,\n    spacing=5\n)\n# Add fuel to furnace\ninsert_item(Prototype.Coal, furnace, quantity=5)\n\n# Add inserter to move ore from belt to furnace\nfurnace_input = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace.position,\n    direction=Direction.LEFT\n)\nfurnace_input = rotate_entity(furnace_input, Direction.RIGHT)\n# Fuel the inserter\ninsert_item(Prototype.Coal, furnace_input, quantity=1)\n\n# Connect drill to furnace with belt\nbelt = connect_entities(drill.drop_position, furnace_input.pickup_position, Prototype.TransportBelt)\n\nprint("Initial mining and smelting setup complete. Will check production after a few seconds.")\nsleep(10)\nass_macine = get_entity(Prototype.AssemblingMachine1, position=Position(x=0, y=0))\n# place inserter to move plates to assembling machine\nfurn_out = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position  = furnace.position,\n    direction = Direction.RIGHT)\nass_in = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position  = ass_macine.position,\n    direction = Direction.RIGHT)\nass_in = rotate_entity(ass_in, Direction.LEFT)\nset_entity_recipe(ass_macine, Prototype.IronGearWheel)\nconnect_entities( furn_out,ass_in, Prototype.TransportBelt)\nsleep(60)'
        _, _, _, achievements = eval_program_with_achievements(instance, test_string_1)

        print(achievements)

def test_achievements_3():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)
        test_string_1 = 'connect_entities(Position(x = -4.5, y = -1.5), Position(x = -11.5, y = 22.5), Prototype.SmallElectricPole)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_4():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)

        #test_string_1 = '# Find copper ore patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_pos}")\n\n# Move there and place first drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.BurnerMiningDrill, position=copper_pos)\ndrill1 = insert_item(Prototype.Coal, drill1, quantity=5)\nprint(f"Placed first drill at {drill1.position}")\n\n# Place second drill\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\nmove_to(drill2_pos)\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos)\ndrill2 = insert_item(Prototype.Coal, drill2, quantity=5)\nprint(f"Placed second drill at {drill2.position}")\n\n# Place third drill\ndrill3_pos = Position(x=drill2.position.x + 3, y=drill2.position.y)\nmove_to(drill3_pos)\ndrill3 = place_entity(Prototype.BurnerMiningDrill, position=drill3_pos)\ndrill3 = insert_item(Prototype.Coal, drill3, quantity=5)\nprint(f"Placed third drill at {drill3.position}")\n\n# Log the positions for next step\nprint(f"Drill positions: {drill1.position}, {drill2.position}, {drill3.position}")\n# Place first furnace north of middle drill\nfurnace1_pos = Position(x=22.0, y=10.0)\nmove_to(furnace1_pos)\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace1_pos)\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=5)\nprint(f"Placed first furnace at {furnace1.position}")\n\n# Place second furnace next to first\nfurnace2_pos = Position(x=24.0, y=10.0)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=5)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Get the drill entities again to ensure fresh state\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=20.0, y=20.0))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=23.0, y=20.0))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=26.0, y=20.0))\n\n# Connect drills with transport belts to create a collection line\nbelts1 = connect_entities(drill1.drop_position, drill2.drop_position, Prototype.TransportBelt)\nbelts2 = connect_entities(drill2.drop_position, drill3.drop_position, Prototype.TransportBelt)\n\n# Connect the collection line to both furnaces using inserters\n# Place inserter for first furnace\ninserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter1 = insert_item(Prototype.Coal, inserter1, quantity=1)\nprint(f"Placed first inserter at {inserter1.position}")\n\n# Place inserter for second furnace\ninserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter2 = insert_item(Prototype.Coal, inserter2, quantity=1)\nprint(f"Placed second inserter at {inserter2.position}")\n\n# Connect collection line to furnace inserters\nconnect_entities(drill2.drop_position, inserter1.pickup_position, Prototype.TransportBelt)\nconnect_entities(drill3.drop_position, inserter2.pickup_position, Prototype.TransportBelt)\n\n# Log current state\n# Get existing inserters\ninserter1 = get_entity(Prototype.BurnerInserter, Position(x=22.5, y=11.5))\ninserter2 = get_entity(Prototype.BurnerInserter, Position(x=24.5, y=11.5))\n\n# Rotate input inserters to pick up from belts and insert into furnaces\ninserter1 = rotate_entity(inserter1, Direction.UP)\ninserter2 = rotate_entity(inserter2, Direction.UP)\n\n# Add output inserters for furnaces\n# First furnace output inserter\noutput_inserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=22.0, y=16.0),  # first furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter1 = insert_item(Prototype.Coal, output_inserter1, quantity=1)\nprint(f"Placed first output inserter at {output_inserter1.position}")\n\n# Second furnace output inserter\noutput_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=24.0, y=16.0),  # second furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter2 = insert_item(Prototype.Coal, output_inserter2, quantity=1)\nprint(f"Placed second output inserter at {output_inserter2.position}")\n\n# Place a chest to collect copper plates\ncollection_chest = place_entity(\n    Prototype.WoodenChest,\n    position=Position(x=26.0, y=16.0)  # Right of second furnace\n)\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Connect output inserters to chest with belts\nconnect_entities(output_inserter1.drop_position, collection_chest.position, Prototype.TransportBelt)\nconnect_entities(output_inserter2.drop_position, collection_chest.position, Prototype.TransportBelt)\n\n# Log current state'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        #print("asda")
        test_string_1 = '# Find copper ore patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_pos}")\n\n# Move there and place first drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.BurnerMiningDrill, position=copper_pos)\ndrill1 = insert_item(Prototype.Coal, drill1, quantity=5)\nprint(f"Placed first drill at {drill1.position}")\n\n# Place second drill\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\nmove_to(drill2_pos)\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos)\ndrill2 = insert_item(Prototype.Coal, drill2, quantity=5)\nprint(f"Placed second drill at {drill2.position}")\n\n# Place third drill\ndrill3_pos = Position(x=drill2.position.x + 3, y=drill2.position.y)\nmove_to(drill3_pos)\ndrill3 = place_entity(Prototype.BurnerMiningDrill, position=drill3_pos)\ndrill3 = insert_item(Prototype.Coal, drill3, quantity=5)\nprint(f"Placed third drill at {drill3.position}")\n\n# Log the positions for next step\nprint(f"Drill positions: {drill1.position}, {drill2.position}, {drill3.position}")\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Place first furnace north of middle drill\nfurnace1_pos = Position(x=22.0, y=10.0)\nmove_to(furnace1_pos)\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace1_pos)\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=5)\nprint(f"Placed first furnace at {furnace1.position}")\n\n# Place second furnace next to first\nfurnace2_pos = Position(x=24.0, y=10.0)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=5)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Get the drill entities again to ensure fresh state\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=20.0, y=20.0))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=23.0, y=20.0))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=26.0, y=20.0))\n\n# Connect drills with transport belts to create a collection line\nbelts1 = connect_entities(drill1.drop_position, drill2.drop_position, Prototype.TransportBelt)\nbelts2 = connect_entities(drill2.drop_position, drill3.drop_position, Prototype.TransportBelt)\n\n# Connect the collection line to both furnaces using inserters\n# Place inserter for first furnace\ninserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter1 = insert_item(Prototype.Coal, inserter1, quantity=1)\nprint(f"Placed first inserter at {inserter1.position}")\n\n# Place inserter for second furnace\ninserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter2 = insert_item(Prototype.Coal, inserter2, quantity=1)\nprint(f"Placed second inserter at {inserter2.position}")\n\n# Connect collection line to furnace inserters\nconnect_entities(drill2.drop_position, inserter1.pickup_position, Prototype.TransportBelt)\nconnect_entities(drill3.drop_position, inserter2.pickup_position, Prototype.TransportBelt)\n\n# Log current state\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities: {get_entities()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Get existing inserters\ninserter1 = get_entity(Prototype.BurnerInserter, Position(x=22.5, y=11.5))\ninserter2 = get_entity(Prototype.BurnerInserter, Position(x=24.5, y=11.5))\n\n# Rotate input inserters to pick up from belts and insert into furnaces\ninserter1 = rotate_entity(inserter1, Direction.UP)\ninserter2 = rotate_entity(inserter2, Direction.UP)\n\n# Add output inserters for furnaces\n# First furnace output inserter\noutput_inserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=22.0, y=16.0),  # first furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter1 = insert_item(Prototype.Coal, output_inserter1, quantity=1)\nprint(f"Placed first output inserter at {output_inserter1.position}")\n\n# Second furnace output inserter\noutput_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=24.0, y=16.0),  # second furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter2 = insert_item(Prototype.Coal, output_inserter2, quantity=1)\nprint(f"Placed second output inserter at {output_inserter2.position}")\n\n# Place a chest to collect copper plates\ncollection_chest = place_entity(\n    Prototype.WoodenChest,\n    position=Position(x=26.0, y=16.0)  # Right of second furnace\n)\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Connect output inserters to chest with belts\nconnect_entities(output_inserter1.drop_position, collection_chest.position, Prototype.TransportBelt)\nconnect_entities(output_inserter2.drop_position, collection_chest.position, Prototype.TransportBelt)\n\n# Log current state\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities: {get_entities()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print("asda")


def test_achievements_5():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)

        #test_string_1 = '# Find copper ore patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_pos}")\n\n# Move there and place first drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.BurnerMiningDrill, position=copper_pos)\ndrill1 = insert_item(Prototype.Coal, drill1, quantity=5)\nprint(f"Placed first drill at {drill1.position}")\n\n# Place second drill\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\nmove_to(drill2_pos)\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos)\ndrill2 = insert_item(Prototype.Coal, drill2, quantity=5)\nprint(f"Placed second drill at {drill2.position}")\n\n# Place third drill\ndrill3_pos = Position(x=drill2.position.x + 3, y=drill2.position.y)\nmove_to(drill3_pos)\ndrill3 = place_entity(Prototype.BurnerMiningDrill, position=drill3_pos)\ndrill3 = insert_item(Prototype.Coal, drill3, quantity=5)\nprint(f"Placed third drill at {drill3.position}")\n\n# Log the positions for next step\nprint(f"Drill positions: {drill1.position}, {drill2.position}, {drill3.position}")\n# Place first furnace north of middle drill\nfurnace1_pos = Position(x=22.0, y=10.0)\nmove_to(furnace1_pos)\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace1_pos)\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=5)\nprint(f"Placed first furnace at {furnace1.position}")\n\n# Place second furnace next to first\nfurnace2_pos = Position(x=24.0, y=10.0)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=5)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Get the drill entities again to ensure fresh state\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=20.0, y=20.0))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=23.0, y=20.0))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=26.0, y=20.0))\n\n# Connect drills with transport belts to create a collection line\nbelts1 = connect_entities(drill1.drop_position, drill2.drop_position, Prototype.TransportBelt)\nbelts2 = connect_entities(drill2.drop_position, drill3.drop_position, Prototype.TransportBelt)\n\n# Connect the collection line to both furnaces using inserters\n# Place inserter for first furnace\ninserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter1 = insert_item(Prototype.Coal, inserter1, quantity=1)\nprint(f"Placed first inserter at {inserter1.position}")\n\n# Place inserter for second furnace\ninserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter2 = insert_item(Prototype.Coal, inserter2, quantity=1)\nprint(f"Placed second inserter at {inserter2.position}")\n\n# Connect collection line to furnace inserters\nconnect_entities(drill2.drop_position, inserter1.pickup_position, Prototype.TransportBelt)\nconnect_entities(drill3.drop_position, inserter2.pickup_position, Prototype.TransportBelt)\n\n# Log current state\n# Get existing inserters\ninserter1 = get_entity(Prototype.BurnerInserter, Position(x=22.5, y=11.5))\ninserter2 = get_entity(Prototype.BurnerInserter, Position(x=24.5, y=11.5))\n\n# Rotate input inserters to pick up from belts and insert into furnaces\ninserter1 = rotate_entity(inserter1, Direction.UP)\ninserter2 = rotate_entity(inserter2, Direction.UP)\n\n# Add output inserters for furnaces\n# First furnace output inserter\noutput_inserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=22.0, y=16.0),  # first furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter1 = insert_item(Prototype.Coal, output_inserter1, quantity=1)\nprint(f"Placed first output inserter at {output_inserter1.position}")\n\n# Second furnace output inserter\noutput_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=24.0, y=16.0),  # second furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter2 = insert_item(Prototype.Coal, output_inserter2, quantity=1)\nprint(f"Placed second output inserter at {output_inserter2.position}")\n\n# Place a chest to collect copper plates\ncollection_chest = place_entity(\n    Prototype.WoodenChest,\n    position=Position(x=26.0, y=16.0)  # Right of second furnace\n)\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Connect output inserters to chest with belts\nconnect_entities(output_inserter1.drop_position, collection_chest.position, Prototype.TransportBelt)\nconnect_entities(output_inserter2.drop_position, collection_chest.position, Prototype.TransportBelt)\n\n# Log current state'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        #print("asda")
        test_string_1 = '# Find copper patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper at {copper_pos}")\n\n# Find water for power\nwater_pos = nearest(Resource.Water) \nprint(f"Found water at {water_pos}")\n\n# Place power infrastructure\nmove_to(water_pos)\npump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed pump at {pump.position}")\n\n# Place boiler with spacing for pipes\nboiler = place_entity_next_to(\n    Prototype.Boiler,\n    reference_position=pump.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed boiler at {boiler.position}")\n\n# Add steam engine with spacing\nsteam_engine = place_entity_next_to(\n    Prototype.SteamEngine,\n    reference_position=boiler.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed steam engine at {steam_engine.position}")\n\n# Connect with pipes\nconnect_entities(pump, boiler, Prototype.Pipe)\nconnect_entities(boiler, steam_engine, Prototype.Pipe)\n\n# Add fuel to boiler\nboiler = insert_item(Prototype.Coal, boiler, quantity=50)\n\n# Place first electric mining drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.ElectricMiningDrill, position=copper_pos)\nprint(f"Placed first drill at {drill1.position}")\n\n# Connect power to drill\nconnect_entities(steam_engine.position, drill1.position, Prototype.SmallElectricPole)\n\n# Log key positions for next steps\nprint(f"Steam engine at: {steam_engine.position}")\nprint(f"First drill at: {drill1.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Get updated drill1 entity\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\n\n# Place first furnace ~10 spaces away from drill1\'s drop position\nfurnace_pos = Position(x=drill1.position.x + 10, y=drill1.position.y)\nmove_to(furnace_pos)\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace_pos)\nprint(f"Placed first furnace at {furnace1.position}")\n\n# Place inserter next to furnace\n# Always use 0 spacing for inserters\nfurnace1_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\nprint(f"Placed furnace inserter at {furnace1_inserter.position}")\n\n# Rotate inserter to put items into furnace (180 degrees from default)\nfurnace1_inserter = rotate_entity(furnace1_inserter, Direction.RIGHT)\n\n# Add fuel to inserter and furnace\nfurnace1_inserter = insert_item(Prototype.Coal, furnace1_inserter, quantity=20)\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=20)\n\n# Connect drill output to furnace inserter with belts\n# IMPORTANT: Always connect belts to inserter pickup position, never directly to furnace\nconnect_entities(\n    drill1.drop_position,\n    furnace1_inserter.pickup_position,\n    Prototype.TransportBelt\n)\n\n# Log positions and status\nprint(f"First furnace at: {furnace1.position}")\nprint(f"First furnace inserter at: {furnace1_inserter.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Get updated drill1 position\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\n\n# Place second drill 3 tiles to the right of first drill (accounting for 3x3 size)\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\nmove_to(drill2_pos)\ndrill2 = place_entity(Prototype.ElectricMiningDrill, position=drill2_pos)\nprint(f"Placed second drill at {drill2.position}")\n\n# Connect power to second drill\nconnect_entities(drill1.position, drill2.position, Prototype.SmallElectricPole)\n\n# Get first furnace position\nfurnace1 = get_entity(Prototype.StoneFurnace, Position(x=30.0, y=20.0))\n\n# Place second furnace 2 tiles to the right of first furnace (accounting for 2x2 size)\nfurnace2_pos = Position(x=furnace1.position.x + 2, y=furnace1.position.y)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Place inserter for second furnace\n# Always use 0 spacing for inserters\nfurnace2_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\nprint(f"Placed second furnace inserter at {furnace2_inserter.position}")\n\n# Rotate inserter to put items into furnace\nfurnace2_inserter = rotate_entity(furnace2_inserter, Direction.RIGHT)\n\n# Add fuel to new entities\nfurnace2_inserter = insert_item(Prototype.Coal, furnace2_inserter, quantity=20)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=20)\n\n# Connect second drill to second furnace inserter\nconnect_entities(\n    drill2.drop_position,\n    furnace2_inserter.pickup_position,\n    Prototype.TransportBelt\n)\n\n# Log positions and status\nprint(f"Second drill at: {drill2.position}")\nprint(f"Second furnace at: {furnace2.position}")\nprint(f"Second furnace inserter at: {furnace2_inserter.position}")'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# First pickup the misplaced furnace\npickup_entity(Prototype.StoneFurnace, Position(x=32.0, y=20.0))\n\n# Place second furnace with more spacing (3 tiles) from first furnace\nfurnace1 = get_entity(Prototype.StoneFurnace, Position(x=30.0, y=20.0))\nfurnace2_pos = Position(x=furnace1.position.x + 3, y=furnace1.position.y)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Place inserter for second furnace\n# Always use 0 spacing for inserters\nfurnace2_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\nprint(f"Placed second furnace inserter at {furnace2_inserter.position}")\n\n# Rotate inserter to put items into furnace\nfurnace2_inserter = rotate_entity(furnace2_inserter, Direction.RIGHT)\n\n# Add fuel to new entities\nfurnace2_inserter = insert_item(Prototype.Coal, furnace2_inserter, quantity=20)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=20)\n\n# Get second drill\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=22.5, y=19.5))\n\n# Connect second drill to second furnace inserter\nconnect_entities(\n    drill2.drop_position,\n    furnace2_inserter.pickup_position,\n    Prototype.TransportBelt\n)\n\n# Log positions and status\nprint(f"Second furnace at: {furnace2.position}")\nprint(f"Second furnace inserter at: {furnace2_inserter.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print("asda")

def test_achievements_6():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)

        #test_string_1 = '# Find copper ore patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_pos}")\n\n# Move there and place first drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.BurnerMiningDrill, position=copper_pos)\ndrill1 = insert_item(Prototype.Coal, drill1, quantity=5)\nprint(f"Placed first drill at {drill1.position}")\n\n# Place second drill\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\nmove_to(drill2_pos)\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos)\ndrill2 = insert_item(Prototype.Coal, drill2, quantity=5)\nprint(f"Placed second drill at {drill2.position}")\n\n# Place third drill\ndrill3_pos = Position(x=drill2.position.x + 3, y=drill2.position.y)\nmove_to(drill3_pos)\ndrill3 = place_entity(Prototype.BurnerMiningDrill, position=drill3_pos)\ndrill3 = insert_item(Prototype.Coal, drill3, quantity=5)\nprint(f"Placed third drill at {drill3.position}")\n\n# Log the positions for next step\nprint(f"Drill positions: {drill1.position}, {drill2.position}, {drill3.position}")\n# Place first furnace north of middle drill\nfurnace1_pos = Position(x=22.0, y=10.0)\nmove_to(furnace1_pos)\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace1_pos)\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=5)\nprint(f"Placed first furnace at {furnace1.position}")\n\n# Place second furnace next to first\nfurnace2_pos = Position(x=24.0, y=10.0)\nmove_to(furnace2_pos)\nfurnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=5)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Get the drill entities again to ensure fresh state\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=20.0, y=20.0))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=23.0, y=20.0))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=26.0, y=20.0))\n\n# Connect drills with transport belts to create a collection line\nbelts1 = connect_entities(drill1.drop_position, drill2.drop_position, Prototype.TransportBelt)\nbelts2 = connect_entities(drill2.drop_position, drill3.drop_position, Prototype.TransportBelt)\n\n# Connect the collection line to both furnaces using inserters\n# Place inserter for first furnace\ninserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter1 = insert_item(Prototype.Coal, inserter1, quantity=1)\nprint(f"Placed first inserter at {inserter1.position}")\n\n# Place inserter for second furnace\ninserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\ninserter2 = insert_item(Prototype.Coal, inserter2, quantity=1)\nprint(f"Placed second inserter at {inserter2.position}")\n\n# Connect collection line to furnace inserters\nconnect_entities(drill2.drop_position, inserter1.pickup_position, Prototype.TransportBelt)\nconnect_entities(drill3.drop_position, inserter2.pickup_position, Prototype.TransportBelt)\n\n# Log current state\n# Get existing inserters\ninserter1 = get_entity(Prototype.BurnerInserter, Position(x=22.5, y=11.5))\ninserter2 = get_entity(Prototype.BurnerInserter, Position(x=24.5, y=11.5))\n\n# Rotate input inserters to pick up from belts and insert into furnaces\ninserter1 = rotate_entity(inserter1, Direction.UP)\ninserter2 = rotate_entity(inserter2, Direction.UP)\n\n# Add output inserters for furnaces\n# First furnace output inserter\noutput_inserter1 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=22.0, y=16.0),  # first furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter1 = insert_item(Prototype.Coal, output_inserter1, quantity=1)\nprint(f"Placed first output inserter at {output_inserter1.position}")\n\n# Second furnace output inserter\noutput_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=Position(x=24.0, y=16.0),  # second furnace position\n    direction=Direction.RIGHT,\n    spacing=0\n)\noutput_inserter2 = insert_item(Prototype.Coal, output_inserter2, quantity=1)\nprint(f"Placed second output inserter at {output_inserter2.position}")\n\n# Place a chest to collect copper plates\ncollection_chest = place_entity(\n    Prototype.WoodenChest,\n    position=Position(x=26.0, y=16.0)  # Right of second furnace\n)\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Connect output inserters to chest with belts\nconnect_entities(output_inserter1.drop_position, collection_chest.position, Prototype.TransportBelt)\nconnect_entities(output_inserter2.drop_position, collection_chest.position, Prototype.TransportBelt)\n\n# Log current state'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        #print("asda")
        test_string_1 = '# Find copper ore patch\ncopper_pos = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_pos}")\n\n# Place first electric mining drill\nmove_to(copper_pos)\ndrill1 = place_entity(Prototype.ElectricMiningDrill, position=copper_pos)\nprint(f"Placed first drill at {drill1.position}")\n\n# Place second drill next to it\ndrill2 = place_entity_next_to(\n    Prototype.ElectricMiningDrill,\n    reference_position=drill1.position,\n    direction=Direction.RIGHT,\n    spacing=1\n)\nprint(f"Placed second drill at {drill2.position}")\n\n# Log the drill positions for future reference\nprint(f"Drill 1 drop position: {drill1.drop_position}")\nprint(f"Drill 2 drop position: {drill2.drop_position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Find water and place offshore pump\nwater_pos = nearest(Resource.Water)\nprint(f"Found water at {water_pos}")\nmove_to(water_pos)\npump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed offshore pump at {pump.position}")\n\n# Place boiler with spacing for pipes\nboiler = place_entity_next_to(\n    Prototype.Boiler,\n    reference_position=pump.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed boiler at {boiler.position}")\n\n# Place steam engine\nsteam_engine = place_entity_next_to(\n    Prototype.SteamEngine,\n    reference_position=boiler.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed steam engine at {steam_engine.position}")\n\n# Connect pump to boiler with pipes\nwater_pipes = connect_entities(pump, boiler, Prototype.Pipe)\nprint("Connected pump to boiler")\n\n# Connect boiler to steam engine with pipes\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\nprint("Connected boiler to steam engine")\n\n# Add fuel to boiler\nboiler = insert_item(Prototype.Coal, boiler, quantity=50)\nprint("Added fuel to boiler")\n\n# Connect power to drills using small electric poles\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=23.5, y=19.5))\n\nconnect_entities(steam_engine.position, drill1.position, Prototype.SmallElectricPole)\nconnect_entities(drill1.position, drill2.position, Prototype.SmallElectricPole)\n\nprint("Connected power to drills")\nsleep(5)  # Wait for power to stabilize\n\n# Verify power status\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=23.5, y=19.5))\nprint(f"Drill 1 status: {drill1.status}")\nprint(f"Drill 2 status: {drill2.status}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Place furnaces 10 spaces south of drill1\'s drop position\nfurnace_start_pos = Position(x=drill1.position.x, y=drill1.position.y + 10)\nmove_to(furnace_start_pos)\n\n# Place two furnaces side by side\nfurnace1 = place_entity(Prototype.StoneFurnace, position=furnace_start_pos)\nprint(f"Placed first furnace at {furnace1.position}")\n\nfurnace2 = place_entity_next_to(\n    Prototype.StoneFurnace,\n    reference_position=furnace1.position,\n    direction=Direction.RIGHT,\n    spacing=1\n)\nprint(f"Placed second furnace at {furnace2.position}")\n\n# Add input inserters for both furnaces\n# always use 0 spacing for inserters\nfurnace1_input = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.UP,\n    spacing=0\n)\nprint(f"Placed furnace1 input inserter at {furnace1_input.position}")\n\nfurnace2_input = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.UP,\n    spacing=0\n)\nprint(f"Placed furnace2 input inserter at {furnace2_input.position}")\n\n# Add fuel to inserters\nfurnace1_input = insert_item(Prototype.Coal, furnace1_input, quantity=20)\nfurnace2_input = insert_item(Prototype.Coal, furnace2_input, quantity=20)\n\n# Add fuel to furnaces\nfurnace1 = insert_item(Prototype.Coal, furnace1, quantity=20)\nfurnace2 = insert_item(Prototype.Coal, furnace2, quantity=20)\n\n# Connect drill1\'s output to furnace input inserters with belts\nbelts1 = connect_entities(\n    drill1.drop_position,\n    furnace1_input.pickup_position,\n    Prototype.TransportBelt\n)\n\n# Connect drill2\'s output to furnace input inserters with belts\nbelts2 = connect_entities(\n    drill2.drop_position,\n    furnace2_input.pickup_position,\n    Prototype.TransportBelt\n)\n\nprint("Connected drills to furnaces with belts")\n\n# Place wooden chest for output 5 spaces south of furnaces\nchest_pos = Position(x=furnace1.position.x + 1, y=furnace1.position.y + 5)\nmove_to(chest_pos)\noutput_chest = place_entity(Prototype.WoodenChest, position=chest_pos)\nprint(f"Placed output chest at {output_chest.position}")\n\n# Add output inserters for both furnaces\n# always use 0 spacing for inserters\nfurnace1_output = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace1.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nfurnace1_output = rotate_entity(furnace1_output, Direction.DOWN)\nfurnace1_output = insert_item(Prototype.Coal, furnace1_output, quantity=20)\n\nfurnace2_output = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace2.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nfurnace2_output = rotate_entity(furnace2_output, Direction.DOWN)\nfurnace2_output = insert_item(Prototype.Coal, furnace2_output, quantity=20)\n\n# Connect output inserters to chest with belts\nconnect_entities(furnace1_output.drop_position, output_chest.position, Prototype.TransportBelt)\nconnect_entities(furnace2_output.drop_position, output_chest.position, Prototype.TransportBelt)\n\nprint("Connected furnaces to output chest")'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        test_string_1 = '# Get current entities\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=23.5, y=19.5))\nfurnace1 = get_entity(Prototype.StoneFurnace, Position(x=20.0, y=30.0))\nfurnace2 = get_entity(Prototype.StoneFurnace, Position(x=23.0, y=30.0))\nfurnace1_input = get_entity(Prototype.BurnerInserter, Position(x=20.5, y=28.5))\nfurnace2_input = get_entity(Prototype.BurnerInserter, Position(x=23.5, y=28.5))\n\n# Fix input inserter rotations - they need to face DOWN to put items into furnaces\nfurnace1_input = rotate_entity(furnace1_input, Direction.DOWN)\nfurnace2_input = rotate_entity(furnace2_input, Direction.DOWN)\n\n# Reconnect belts from drills to furnace input inserters\n# First remove any existing belts by picking them up\nprint("Reconnecting belts from drills to furnaces")\n\n# Connect drill1 to furnace1 input inserter\nbelts1 = connect_entities(\n    drill1.drop_position,\n    furnace1_input.pickup_position,\n    Prototype.TransportBelt\n)\n\n# Connect drill2 to furnace2 input inserter\nbelts2 = connect_entities(\n    drill2.drop_position,\n    furnace2_input.pickup_position,\n    Prototype.TransportBelt\n)\n\nprint("Fixed belt connections and inserter rotations")\n\n# Wait to see if ore starts flowing\nsleep(10)\n\n# Check status of components\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=19.5, y=19.5))\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=23.5, y=19.5))\nfurnace1 = get_entity(Prototype.StoneFurnace, Position(x=20.0, y=30.0))\nfurnace2 = get_entity(Prototype.StoneFurnace, Position(x=23.0, y=30.0))\n\nprint(f"Drill 1 status: {drill1.status}")\nprint(f"Drill 2 status: {drill2.status}")\nprint(f"Furnace 1 status: {furnace1.status}")\nprint(f"Furnace 2 status: {furnace2.status}")\nprint(f"Furnace 1 contents: {inspect_inventory(furnace1)}")\nprint(f"Furnace 2 contents: {inspect_inventory(furnace2)}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print("asda")


def test_achievements_7():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY)


        #test_string_1 = 'move_to(Position(x = 28, y = 2))\nbuilding_box = BuildingBox(width = 4, height = 4)\nbbox = nearest_buildable(Prototype.WoodenChest, building_box, Position(x = -10, y = 0))\nprint(bbox)\nmove_to(bbox)'
        test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_ore_pos}")\n\n# Create building box for 3 drills\nbuilding_box = BuildingBox(width=9, height=2)\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n\n# Get leftmost position to start placing drills\ncenter = buildable_coordinates["centre"]\nwidth_margin = buildable_coordinates["width_margin"]\nleftmost_point = Position(x=center.x - width_margin, y=center.y)\n\n# Move to center first\nmove_to(center)\n\n# Place 3 drills in a line\ndrills = []\nfor i in range(3):\n    drill_pos = Position(x=leftmost_point.x + 2*i, y=leftmost_point.y)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)\n    drills.append(drill)\n    print(f"Placed drill {i+1} at {drill_pos}")\n\n# Place chest 10 spaces away from last drill\nchest_pos = Position(x=drills[-1].position.x + 10, y=drills[-1].position.y)\nmove_to(chest_pos)\n\n# Use building box for chest\nchest_box = BuildingBox(width=1, height=1)\nchest_coordinates = nearest_buildable(Prototype.WoodenChest, chest_box, chest_pos)\nchest = place_entity(Prototype.WoodenChest, position=chest_coordinates["centre"])\nprint(f"Placed collection chest at {chest.position}")\n\n# Place inserter next to chest\ninserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=chest.position, \n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\ninserter = rotate_entity(inserter, Direction.RIGHT)\nprint(f"Placed and rotated inserter at {inserter.position}")\n\n# Connect drills to inserter with transport belts\nfor drill in drills:\n    connect_entities(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)\n\n# Log positions for next step\nprint(f"Drills positioned at: {[d.position for d in drills]}")\nprint(f"Chest positioned at: {chest.position}")'
        
        #test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_ore_pos}")\nmove_to(Position(x=-19, y=29))\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-19.5, y=28.5))\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-17.5, y=28.5))\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-15.5, y=28.5))'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print(f"asda")
        

def test_achievements_7():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find water and place offshore pump\nwater_pos = nearest(Resource.Water)\nprint(f"Found water at {water_pos}")\nmove_to(water_pos)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed offshore pump at {offshore_pump.position}")\n\n# Place boiler with spacing for pipes\nboiler = place_entity_next_to(\n    Prototype.Boiler,\n    reference_position=offshore_pump.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed boiler at {boiler.position}")\n\n# Add steam engine with spacing\nsteam_engine = place_entity_next_to(\n    Prototype.SteamEngine,\n    reference_position=boiler.position,\n    direction=Direction.RIGHT,\n    spacing=3\n)\nprint(f"Placed steam engine at {steam_engine.position}")\n\n# Connect with pipes\npipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\n\n# Fuel the boiler\nboiler = insert_item(Prototype.Coal, boiler, quantity=50)\n\n# Log positions for future reference\nprint(f"Power system positions - Pump: {offshore_pump.position}, Boiler: {boiler.position}, Engine: {steam_engine.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        #test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Get steam engine position for power connection\nsteam_engine = get_entity(Prototype.SteamEngine, Position(x=-2.5, y=-1.5))\n\n# Define building box for 3 drills (each electric drill is 3 wide)\nbuilding_box = BuildingBox(width=9, height=3)  # 3 drills * 3 width each\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_pos)\nprint(f"Found buildable area at {buildable_coordinates}")\n\n# Place drills in a line\ndrills = []\ncentre = buildable_coordinates["centre"]\nwidth_margin = buildable_coordinates["width_margin"]\nleftmost_point = Position(x=centre.x - width_margin, y=centre.y)\nmove_to(centre)\n\nfor i in range(3):\n    drill_pos = Position(x=leftmost_point.x + i*3, y=leftmost_point.y)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)\n    drills.append(drill)\n    print(f"Placed drill {i+1} at {drill.position}")\n\n# Connect power from steam engine to drills\n# First place pole near steam engine\nmove_to(steam_engine.position)\nfirst_pole = place_entity(Prototype.SmallElectricPole, \n    position=Position(x=steam_engine.position.x, y=steam_engine.position.y-3))\nprint(f"Placed first power pole at {first_pole.position}")\n\n# Connect power to all drills\nlast_pole = connect_entities(first_pole.position, drills[0].position, Prototype.SmallElectricPole)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Get steam engine position for power connection\nsteam_engine = get_entity(Prototype.SteamEngine, Position(x=-2.5, y=-1.5))\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13.5 ,y=25.5))\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-13.5 ,y=25.5))\ndrills.append(drill)\nmove_to(Position(x=-14.5 ,y=21.5))\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-14.5 ,y=21.5))\ndrills.append(drill)\ndrill = place_entity(Prototype.ElectricMiningDrill, position=Position(x=-17.5 ,y=26.5))\ndrills.append(drill)\n# Connect power from steam engine to drills\n# First place pole near steam engine\nmove_to(steam_engine.position)\nfirst_pole = place_entity(Prototype.SmallElectricPole, \n    position=Position(x=steam_engine.position.x, y=steam_engine.position.y-3))\nprint(f"Placed first power pole at {first_pole.position}")\n\n# Connect power to all drills using small electric poles\nfor drill in drills:\n    connect_entities(first_pole.position, drill.position, Prototype.SmallElectricPole)\n    print(f"Connected power to drill at {drill.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.ElectricMiningDrill, Position(x=-13.5, y=25.5))\ndrill2 = get_entity(Prototype.ElectricMiningDrill, Position(x=-14.5, y=21.5))\ndrill3 = get_entity(Prototype.ElectricMiningDrill, Position(x=-17.5, y=26.5))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nfor drill in [drill1, drill2, drill3]:\n    belts = connect_entities(\n        drill.drop_position,\n        chest_inserter.pickup_position,\n        Prototype.TransportBelt\n    )\n    print(f"Connected drill at {drill.position} to collection system")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_8():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13.5 ,y=25.5))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13.5 ,y=25.5))\ndrills.append(drill)\nmove_to(Position(x=-14.5 ,y=21.5))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-14.5 ,y=21.5))\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-17.5 ,y=26.5))\ndrills.append(drill)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.5, y=25.5))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-14.5, y=21.5))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-17.5, y=26.5))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nfor drill in [drill1, drill2, drill3]:\n    belts = connect_entities(\n        drill.drop_position,\n        chest_inserter.pickup_position,\n        Prototype.TransportBelt\n    )\n    print(f"Connected drill at {drill.position} to collection system")'
        test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.5, y=25.5))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-14.5, y=21.5))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-17.5, y=26.5))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill3.drop_position,chest_inserter.pickup_position, Prototype.TransportBelt)\n\n# connect the first drill to the connection system\nbelts = connect_entities(drill2.drop_position,main_connection[0], Prototype.TransportBelt)\n\n# connect the first drill to the connection system\nbelts = connect_entities(drill1.drop_position,main_connection[0], Prototype.TransportBelt)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)



def test_achievements_9():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=25), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=21), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.5, y=25.5))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-14.5, y=21.5))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-17.5, y=26.5))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nfor drill in [drill1, drill2, drill3]:\n    belts = connect_entities(\n        drill.drop_position,\n        chest_inserter.pickup_position,\n        Prototype.TransportBelt\n    )\n    print(f"Connected drill at {drill.position} to collection system")'
        test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter.pickup_position, Prototype.TransportBelt)\n\n# connect the first drill to the connection system\nbelts = connect_entities(drill1.drop_position,main_connection[0], Prototype.TransportBelt)\n\n# connect the first drill to the connection system\nbelts = connect_entities(drill3.drop_position,main_connection[0], Prototype.TransportBelt)'
        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill1.drop_position,chest_inserter.pickup_position, Prototype.TransportBelt)'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_10():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=25), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=21), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13.5, y=25.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-17.5, y=26.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-14.5, y=21.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.0 ,y=26.0))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-17.0 ,y=27.0))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-14.0 ,y=22.0))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-23.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-23.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nbelts = connect_entities(drill2.drop_position,chest_inserter.pickup_position,Prototype.TransportBelt)\nprint(f"Connected drill at {drill.position} to collection")\nbelts = connect_entities(drill1.drop_position,belts[0],Prototype.TransportBelt)\nprint(f"Connected drill at {drill.position} to collection system")\nbelts = connect_entities(drill3.drop_position,belts[0],Prototype.TransportBelt)'
        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill1 = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13.5, y=25.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill1.position}")\nmove_to(Position(x=-13 ,y=23))\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-17.5, y=26.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill2.position}")\ndrill3 = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-14.5, y=21.5), direction = Direction.LEFT)\nprint(f"placed drill at {drill3.position}")\nmove_to(Position(x=-23.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-23.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nbelts = connect_entities(drill2.drop_position,chest_inserter.pickup_position,Prototype.TransportBelt)\nprint(f"Connected drill at {drill2.position} to collection")\nbelts = connect_entities(drill1.drop_position,belts[0],Prototype.TransportBelt)\nprint(f"Connected drill at {drill1.position} to collection system")\nbelts = connect_entities(drill3.drop_position,belts[0],Prototype.TransportBelt)'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print(f"asda")

def test_achievements_11():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=25), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=21), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.5, y=25.5))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-14.5, y=21.5))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-17.5, y=26.5))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n\n# Connect all drills to the inserter\'s pickup position using transport belts\nfor drill in [drill1, drill2, drill3]:\n    belts = connect_entities(\n        drill.drop_position,\n        chest_inserter.pickup_position,\n        Prototype.TransportBelt\n    )\n    print(f"Connected drill at {drill.position} to collection system")'
        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\ncollection_chest2 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=18))\nprint(f"Placed collection chest at {collection_chest2.position}")\n\n# Place inserter next to chest\nchest_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter2 = rotate_entity(chest_inserter2, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter2.position}")\n\ncollection_chest3 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=28))\nprint(f"Placed collection chest at {collection_chest3.position}")\n\n# Place inserter next to chest\nchest_inserter3 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest3.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter3 = rotate_entity(chest_inserter3, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter3.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter2.pickup_position, Prototype.TransportBelt)\n# extend connection\nmain_connection = connect_entities(main_connection[0],chest_inserter.pickup_position ,Prototype.TransportBelt)\nprint(main_connection)'
        test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\ncollection_chest2 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=18))\nprint(f"Placed collection chest at {collection_chest2.position}")\n\n# Place inserter next to chest\nchest_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter2 = rotate_entity(chest_inserter2, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter2.position}")\n\ncollection_chest3 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=28))\nprint(f"Placed collection chest at {collection_chest3.position}")\n\n# Place inserter next to chest\nchest_inserter3 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest3.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter3 = rotate_entity(chest_inserter3, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter3.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter2.pickup_position, Prototype.TransportBelt)\nprint(main_connection)\n# extend connection\nmain_connection = connect_entities(main_connection[0],chest_inserter.pickup_position ,Prototype.TransportBelt)\nprint(main_connection)'
        
        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill1.drop_position,chest_inserter.pickup_position, Prototype.TransportBelt)'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)



def test_achievements_12():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=25), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=21), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")
        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3.5, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter.pickup_position, Prototype.TransportBelt)'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_13():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Place drills individually with smaller building boxes\ndrills = []\nmove_to(Position(x=-13 ,y=25))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=25), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\nmove_to(Position(x=-13 ,y=23))\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=21), direction = Direction.LEFT)\nprint(f"placed drill at {drill.position}")\ndrills.append(drill)'
        #test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\n# Place drills individually with smaller building boxes\nmove_to(Position(x=-13 ,y=23))\nndrill = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)'
        #
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Get the drill positions\ndrill1 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13, y=25))\ndrill2 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=23))\ndrill3 = get_entity(Prototype.BurnerMiningDrill, Position(x=-13 ,y=21))\n\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\ncollection_chest2 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=18))\nprint(f"Placed collection chest at {collection_chest2.position}")\n\n# Place inserter next to chest\nchest_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter2 = rotate_entity(chest_inserter2, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter2.position}")\n\ncollection_chest3 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=28))\nprint(f"Placed collection chest at {collection_chest3.position}")\n\n# Place inserter next to chest\nchest_inserter3 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest3.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter3 = rotate_entity(chest_inserter3, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter3.position}")\n\n# Add fuel to inserter\nchest_inserter = insert_item(Prototype.Coal, chest_inserter, quantity=50)\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter2.pickup_position, Prototype.TransportBelt)\n# extend connection\nmain_connection = connect_entities(main_connection[0],chest_inserter.pickup_position ,Prototype.TransportBelt)'
        test_string_1 = '# Find iron ore patch\niron_pos = nearest(Resource.IronOre)\nmove_to(Position(x=-13 ,y=23))\n# Place drills individually with smaller building boxes\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=Position(x=-13 ,y=23), direction = Direction.LEFT)\n# Place chest about 10 spaces away from the middle drill\nmove_to(Position(x=-3.5, y=22.5))\ncollection_chest = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=22.5))\nprint(f"Placed collection chest at {collection_chest.position}")\n\n# Place inserter next to chest\nchest_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter = rotate_entity(chest_inserter, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter.position}")\n\ncollection_chest2 = place_entity(Prototype.WoodenChest, position=Position(x=-3, y=18))\nprint(f"Placed collection chest at {collection_chest2.position}")\n\n# Place inserter next to chest\nchest_inserter2 = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=collection_chest2.position,\n    direction=Direction.LEFT,\n    spacing=0\n)\n# Rotate inserter to put items into chest\nchest_inserter2 = rotate_entity(chest_inserter2, Direction.RIGHT)\nprint(f"Placed chest inserter at {chest_inserter2.position}")\n# connect the first drill to the connection system\nmain_connection= connect_entities(drill2.drop_position,chest_inserter2.pickup_position, Prototype.TransportBelt)\n# extend connection\nmain_connection = connect_entities(main_connection[0],chest_inserter.pickup_position ,Prototype.TransportBelt)'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)




def test_achievements_14():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'iron_ore_position = nearest(Resource.IronOre)\nmove_to(iron_ore_position)\nbuilding_box = BuildingBox(width = 1, height = 4)\n# get the nearest buildable area around the iron_ore_position\nbuildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, iron_ore_position)\nprint(buildable_coordinates)\nmove_to(buildable_coordinates["right_bottom"])'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_15():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = 'belt_end_position = Position(x=-11.5, y=26.5)\nchest_central_pos = Position(x = belt_end_position.x+10, y = belt_end_position.y)\nbuilding_box = BuildingBox(width = 3, height = 1)\nbuildable_coordinates = nearest_buildable(Prototype.WoodenChest, building_box, chest_central_pos)\nmove_to(buildable_coordinates["right_bottom"])'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        #print("asda")
        #test_string_1 = 'bottom_drill = place_entity(Prototype.BurnerMiningDrill,position=Position(0, 0), direction = Direction.UP)\nbottom_drill = place_entity(Prototype.ElectricMiningDrill,position=Position(3, 0), direction = Direction.UP)\nmove_to(Position(0, 5))'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        #
#
        #test_string_1 = 'iron_ore_pos = nearest(Resource.IronOre)\nnum_drills = 3\ndrills = []\nbuilding_box = BuildingBox(width = 3*num_drills, height = 7)\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\nleft_top = buildable_coordinates["left_top"]\nleft_bottom = buildable_coordinates["left_bottom"]\nupper_drills = []\nfor i in range(num_drills):\n        upper_drill_position = Position(x=left_top.x + 1 + i * 3,y=left_top.y)\n        move_to(upper_drill_position)\n        # Place and configure each drill\n        upper_drill = place_entity(Prototype.ElectricMiningDrill,position=upper_drill_position)\n        upper_drill = rotate_entity(upper_drill, direction = Direction.DOWN)\n        print(f"Placed upper drill {i} at {upper_drill.position}")\n        upper_drills.append(upper_drill)\n        bottom_drill_position = Position(x=left_bottom.x + i * 3 + 1,y=left_bottom.y-1)\n        bottom_drill = place_entity(Prototype.ElectricMiningDrill,position=bottom_drill_position, direction = Direction.UP)\nbelt_start = upper_drills[0].drop_position\nbelt_end = upper_drills[-1].drop_position\nmain_belt = connect_entities(belt_start,belt_end,Prototype.TransportBelt)\nprint(f"Created the main belt: {main_belt}")'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
         

        test_string_1 = 'iron_ore_pos = nearest(Resource.IronOre)\nnum_drills = 5\ndrills = []\nbuilding_box = BuildingBox(width = 2*num_drills, height = 5)\nbuildable_coordinates = nearest_buildable(Prototype.BurnerMiningDrill, building_box, iron_ore_pos)\nleft_top = buildable_coordinates["left_top"]\ndrills = []\nfor i in range(num_drills):\n        upper_drill_position = Position(x=left_top.x + i * 2,y=left_top.y)\n        move_to(upper_drill_position)\n        # Place and configure each drill\n        upper_drill = place_entity(Prototype.BurnerMiningDrill,position=upper_drill_position, direction = Direction.DOWN)\n        print(f"Placed upper drill {i} at {upper_drill.position}")\n        drills.append(upper_drill)\n        bottom_drill = place_entity_next_to(Prototype.BurnerMiningDrill,reference_position=upper_drill.position, direction = Direction.DOWN, spacing = 1)\n        bottom_drill = rotate_entity(bottom_drill, direction = Direction.UP)\n        drills.append(bottom_drill)\nx_coordinates = [drill.drop_position.x for drill in drills]\nstart_x = min(x_coordinates)\nend_x = max(x_coordinates)\nshared_y_coordinate = drills[0].drop_position.y\nbelt_start = Position(x = start_x, y = shared_y_coordinate)\nbelt_end = Position(x = end_x, y = shared_y_coordinate)\nmain_belt = connect_entities(belt_start,belt_end,Prototype.TransportBelt)\nprint(f"Created the main belt: {main_belt}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        test_string_1 = 'belt_end_position = Position(x=-11.5, y=26.5)\nchest_central_pos = Position(x = belt_end_position.x+10, y = belt_end_position.y)\nbuilding_box = BuildingBox(width = 3, height = 1)\nbuildable_coordinates = nearest_buildable(Prototype.WoodenChest, building_box, chest_central_pos)\nleft_top = buildable_coordinates["left_top"]\nchest = place_entity(Prototype.WoodenChest, position = left_top)\nprint(f"placed collection chest at {chest.position}")\nchest_inserter = place_entity_next_to(Prototype.BurnerInserter,chest.position,direction=Direction.RIGHT, spacing = 0)\nchest_inserter = rotate_entity(chest_inserter, Direction.LEFT)\nmain_belt_extended = connect_entities(belt_end_position,chest_inserter.pickup_position,Prototype.TransportBelt)\nprint(f"Extended the resource belt: {main_belt_extended}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")
        

def test_achievements_16():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'water_position = nearest(Resource.Water)\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(offshore_pump)\nboiler = place_entity_next_to(Prototype.Boiler,reference_position=offshore_pump.position,spacing=3)\nboiler = insert_item(Prototype.Coal, boiler, 10)\nsteam_engine = place_entity_next_to(Prototype.SteamEngine,reference_position=boiler.position, spacing=3)\nprint(f"Placed steam_engine at {steam_engine.position}") # Position(x=4, y = -21)\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\nsleep(5)\nprint(steam_engine)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")

def test_achievements_17():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'move_to(Position(x=-11.5, y=21.5))\nplace_entity(Prototype.BurnerInserter, position = Position(x=-11.5, y=21.5))\npickup_entity(Prototype.BurnerInserter, Position(x=-11.5, y=21.5))'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_18():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'for i in range(10):\n    if i < 5:\n        j = 0\n        while j < 3:\n            j +=1\n            if j == 2:\n                try:\n                    int("asd")\n                except:\n                    print("fucked")\n                    continue\n            print(j)\n        print(f"first lower loop for {i}")\n    else:        print(f"second lower loop for {i}")\n    print(f"Placed inserter {i}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)



def test_achievements_19():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'belts = connect_entities(Position(x = 10, y = -9), Position(x = 0, y = 0), Prototype.TransportBelt)\nprint(belts)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

def test_achievements_20():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'belts = connect_entities(Position(x = 10, y = -9), Position(x = 0, y = 0), Prototype.TransportBelt)\nprint(belts)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_20():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 


        test_string_1 = 'water_position = nearest(Resource.Water)\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(offshore_pump)\nboiler = place_entity_next_to(Prototype.Boiler,reference_position=offshore_pump.position,spacing=3)\nboiler = insert_item(Prototype.Coal, boiler, 10)\nsteam_engine = place_entity_next_to(Prototype.SteamEngine,reference_position=boiler.position, spacing=3)\nprint(f"Placed steam_engine at {steam_engine.position}") # Position(x=4, y = -21)\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\nsleep(5)\nprint(steam_engine)\noutp = connect_entities(steam_engine.position, Position(x = 4, y = -20), Prototype.SmallElectricPole)\nprint(get_entities())'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_21():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'move_to(Position(x = 0, y = 0))\nprint(can_place_entity(Prototype.Boiler, position=Position(x = 0, y = 0)))'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Power system pattern\nwater_position = nearest(Resource.Water)\nmove_to(water_position)\n# first place offshore pump on the water system\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump at {offshore_pump.position}")\n# Then place the boiler close to the offshore pump\n# IMPORTANT: We need to be careful as there is water nearby which is unplaceable,\n# We do not know where the water is so we will use can_place_entity for safety\n# We will also need to be atleast 6 tiles away as the entities are large and otherwise wont have room for connections\n# construct 6 potential positions for the boiler, each 6 tiles away from offshore pump\npotential_positions = [Position(x = offshore_pump.position.x+6, y = offshore_pump.position.y),Position(x = offshore_pump.position.x-6, y = offshore_pump.position.y),Position(x = offshore_pump.position.x, y = offshore_pump.position.y+6),Position(x = offshore_pump.position.x, y = offshore_pump.position.y-6)]\nboiler_placed = False # variable to check if boiler was placed\nfor boiler_position in potential_positions:\n    if can_place_entity(Prototype.Boiler, position=boiler_position):\n        # place the boiler\n        boiler = place_entity(Prototype.Boiler, position=boiler_position)\n        boiler_placed = True\n        print(f"Placed boiler at {boiler_position}")\n        break\nassert boiler_placed, f"Could not find a safe tile to place boiler close to offshore pump 6 spaces away. Consider enlargening the grid"\n# add coal to boiler to start the power generation\nboiler = insert_item(Prototype.Coal, boiler, 10)\n# Finally we need to place the steam engine close to the boiler\n# IMPORTANT: We again need to be safe and use can_place_entity with a tile size of 6\npotential_positions = [Position(x = boiler.position.x+6, y = boiler.position.y),Position(x = boiler.position.x-6, y = boiler.position.y),Position(x = boiler.position.x, y = boiler.position.y+6), Position(x = boiler.position.x, y = boiler.position.y-6)]\nsteam_engine_placed = False # variable to check if boiler was placed\nfor steam_engine_position in potential_positions:\n    move_to(steam_engine_position)\n    if can_place_entity(Prototype.SteamEngine, position=steam_engine_position):\n        # place the steam engine\n        steam_engine = place_entity(Prototype.SteamEngine,position=steam_engine_position)\n        # update the variable\n        steam_engine_placed = True\n        print(f"Placed steam_engine at {steam_engine.position}")\n        break\nassert steam_engine_placed, f"Could not find a safe tile to place steam_engine 6 spaces away from boiler. Consider enlargening the grid"'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")



def test_achievements_22():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Locate the nearest copper ore patch\ncopper_ore_position = nearest(Resource.CopperOre)\nprint(f"Located copper ore patch at {copper_ore_position}")\n\n# Define the BuildingBox for the drills. ElectricMiningDrill has 3x3 dimensions.\nbuilding_box = BuildingBox(width=3, height=3)\n\n# Get the nearest buildable area around the copper_ore_position\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, copper_ore_position)\n\n# Place two electric mining drills on the copper ore patch\n# Start from the leftmost position of the buildable area\nleft_top = buildable_coordinates["left_top"]\n\n# Move to the position to place the first drill\nmove_to(left_top)\ndrill_1 = place_entity(Prototype.ElectricMiningDrill, position=left_top)\nprint(f"Placed first ElectricMiningDrill at {drill_1.position} to mine copper ore")\n\n# Place the second drill next to the first one\ndrill_2_position = left_top + Position(x=3, y=0)  # Move 3 tiles to the right\nmove_to(drill_2_position)\ndrill_2 = place_entity(Prototype.ElectricMiningDrill, position=drill_2_position)\nprint(f"Placed second ElectricMiningDrill at {drill_2.position} to mine copper ore")\n\n# Set up a power source for the drills\n# Locate the nearest water source for the offshore pump\nwater_position = nearest(Resource.Water)\nprint(f"Located water source at {water_position}")\n\n# Move to the water position and place the offshore pump\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed OffshorePump at {offshore_pump.position} to get water")\n\n# Place a boiler close to the offshore pump\n# Ensure there is enough space for connections\nboiler_position = Position(x=offshore_pump.position.x + 4, y=offshore_pump.position.y)\nmove_to(boiler_position)\nboiler = place_entity(Prototype.Boiler, position=boiler_position)\nprint(f"Placed Boiler at {boiler.position} to generate steam")\n\n# Insert coal into the boiler to start generating steam\nboiler = insert_item(Prototype.Coal, boiler, quantity=20)\n\n# Place a steam engine close to the boiler\nsteam_engine_position = Position(x=boiler.position.x + 4, y=boiler.position.y)\nmove_to(steam_engine_position)\nsteam_engine = place_entity(Prototype.SteamEngine, position=steam_engine_position)\nprint(f"Placed SteamEngine at {steam_engine.position} to generate electricity")\n\n# Connect the offshore pump to the boiler with pipes\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nprint(f"Connected OffshorePump at {offshore_pump.position} to Boiler at {boiler.position} with pipes {water_pipes}")\n\n# Connect the boiler to the steam engine with pipes\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_24():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        PLACEMENT_STARTING_INVENTORY = {"iron-plate": 19}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'craft_item(Prototype.BurnerMiningDrill, quantity=1)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


def test_achievements_24():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Place storage chest at end of main belt\nstorage_pos = Position(x=-8.5, y=30.5)\nmove_to(storage_pos)\nstorage_chest = place_entity(Prototype.WoodenChest, position=storage_pos)\nprint(f"Placed storage chest at {storage_pos}")\n\n# Connect main belt to storage chest\nbelt_end = Position(x=-10.5, y=30.5)\nconnect_entities(belt_end, storage_pos, Prototype.TransportBelt)\nprint(f"Connected main belt at {belt_end} to storage chest at {storage_pos}")\n\n# Verify ore flow to storage chest\nsleep(10)\nstorage_chest = get_entity(Prototype.WoodenChest, storage_pos)\nstorage_inv = inspect_inventory(storage_chest)'
        #test_string_1 = '# Place storage chest at end of main belt\nstorage_pos = Position(x=-8.5, y=30.5)\nmove_to(storage_pos)\nstorage_chest = place_entity(Prototype.WoodenChest, position=storage_pos)\nprint(f"Placed storage chest at {storage_pos}")\nstorage_chest = get_entity(Prototype.WoodenChest, storage_pos)\nstorage_inv = inspect_inventory(storage_chest)\nassert storage_inv[Prototype.IronOre] > 0, "Ore not reaching storage chest"\nprint(f"Storage chest now has {storage_inv[Prototype.IronOre]} iron ore")\n\n# Final system verification\nprint(f"Current throughput: {production_stats()}")\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")

def test_achievements_25():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'nearest(Resource.Water)'
        #test_string_1 = '# Place storage chest at end of main belt\nstorage_pos = Position(x=-8.5, y=30.5)\nmove_to(storage_pos)\nstorage_chest = place_entity(Prototype.WoodenChest, position=storage_pos)\nprint(f"Placed storage chest at {storage_pos}")\nstorage_chest = get_entity(Prototype.WoodenChest, storage_pos)\nstorage_inv = inspect_inventory(storage_chest)\nassert storage_inv[Prototype.IronOre] > 0, "Ore not reaching storage chest"\nprint(f"Storage chest now has {storage_inv[Prototype.IronOre]} iron ore")\n\n# Final system verification\nprint(f"Current throughput: {production_stats()}")\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")



def test_achievements_26():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Move to the nearest copper ore position\ncopper_ore_position = nearest(Resource.CopperOre)\nmove_to(copper_ore_position)\nprint(f"Moved to copper ore position at {copper_ore_position}")\n\n# Define the building box for the drill line\nbuilding_box = BuildingBox(width=2*5, height=4) # 5 drills, 2 width per drill, 4 height to account for inserter and belt\n# Get the nearest buildable area around the copper ore position\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, copper_ore_position)\n\n# Place the drill line\nleft_top = buildable_coordinates["left_top"]\nmove_to(left_top)\nfor i in range(5):\n    drill_position = Position(x=left_top.x + 2*i, y=left_top.y)\n    move_to(drill_position)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_position, direction=Direction.DOWN)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine copper ore")\n\n# Place the furnace line\nfurnace_positions = []\nfor i in range(5):\n    furnace_position = Position(x=left_top.x + 2*i, y=left_top.y + 2)\n    move_to(furnace_position)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_position)\n    furnace_positions.append(furnace_position)\n    print(f"Placed StoneFurnace {i} at {furnace_position} to smelt copper plates")\n\n# Connect the drill line to the furnace line with inserters and belts\nfor i in range(5):\n    drill = get_entity(Prototype.ElectricMiningDrill, position=Position(x=left_top.x + 2*i, y=left_top.y))\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace_positions[i])\n    inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=drill.position, direction=Direction.DOWN, spacing=0)\n    print(f"Placed BurnerInserter {i} at {inserter.position} to input copper ore to furnace")\n    inserter = rotate_entity(inserter, Direction.DOWN) # Face inserter towards furnace\n    belts = connect_entities(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)\n    print(f"Connected ElectricMiningDrill {i} to BurnerInserter {i} with {belts}")\n\n# Connect the furnace line to a chest with inserters and belts\nchest_position = Position(x=left_top.x + 5, y=left_top.y + 1)\nmove_to(chest_position)\nchest = place_entity(Prototype.WoodenChest, position=chest_position)\nprint(f"Placed WoodenChest at {chest_position} to collect copper plates")\nfor i in range(5):\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace_positions[i])\n    inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=furnace.position, direction=Direction.RIGHT, spacing=0)\n    print(f"Placed BurnerInserter {i} at {inserter.position} to output copper plates to chest")\n    inserter = rotate_entity(inserter, Direction.LEFT) # Face inserter towards chest\n    belts = connect_entities(furnace.position, inserter.pickup_position, Prototype.TransportBelt)\n    print(f"Connected StoneFurnace {i} to BurnerInserter {i} with {belts}")\n    belts = connect_entities(inserter.drop_position, chest.position, Prototype.TransportBelt)\n    print(f"Connected BurnerInserter {i} to WoodenChest with {belts}")'
        test_string_1 = '# Move to the nearest copper ore position\ncopper_ore_position = nearest(Resource.CopperOre)\nmove_to(copper_ore_position)\nprint(f"Moved to copper ore position at {copper_ore_position}")\n\n# Define the building box for the drill line\nbuilding_box = BuildingBox(width=2*5, height=4) # 5 drills, 2 width per drill, 4 height to account for inserter and belt\n# Get the nearest buildable area around the copper ore position\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, copper_ore_position)\n\n# Place the drill line\nleft_top = buildable_coordinates["left_top"]\nmove_to(left_top)\nfor i in range(5):\n    drill_position = Position(x=left_top.x + 2*i, y=left_top.y)\n    move_to(drill_position)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_position, direction=Direction.DOWN)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine copper ore")\n\n# Place the furnace line\nfurnace_positions = []\nfor i in range(5):\n    furnace_position = Position(x=left_top.x + 2*i, y=left_top.y + 2)\n    move_to(furnace_position)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_position)\n    furnace_positions.append(furnace_position)\n    print(f"Placed StoneFurnace {i} at {furnace_position} to smelt copper plates")\n\n# Connect the drill line to the furnace line with inserters and belts\nfor i in range(5):\n    drill = get_entity(Prototype.ElectricMiningDrill, position=Position(x=left_top.x + 2*i, y=left_top.y))'
        test_string_1 = '# Move to the nearest copper ore position\ncopper_ore_position = nearest(Resource.CopperOre)\nmove_to(copper_ore_position)\nprint(f"Moved to copper ore position at {copper_ore_position}")\n\n# Define the building box for the drill line\nbuilding_box = BuildingBox(width=2*5, height=4) # 5 drills, 2 width per drill, 4 height to account for inserter and belt\n# Get the nearest buildable area around the copper ore position\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, copper_ore_position)\n\n# Place the drill line\nleft_top = buildable_coordinates["left_top"]\nmove_to(left_top)\nfor i in range(5):\n    drill_position = Position(x=left_top.x + 2*i, y=left_top.y)\n    move_to(drill_position)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_position, direction=Direction.DOWN)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine copper ore")'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_27():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Locate the nearest copper ore patch\ncopper_ore_position = nearest(Resource.CopperOre)\nprint(f"Found copper ore at {copper_ore_position}")\n\n# Define the BuildingBox for the drill line\n# ElectricMiningDrill has dimensions 3x3\n# We need 2 drills so width is 3*2, height is 4 (3 for drill, 1 for furnace)\nbuilding_box = BuildingBox(width=3*2, height=4)\n\n# Get the nearest buildable area around the copper_ore_position\nbuildable_coordinates = nearest_buildable(Prototype.ElectricMiningDrill, building_box, copper_ore_position)\n\n# Place the first electric mining drill\ndrill_1_position = buildable_coordinates["left_top"]\nmove_to(drill_1_position)\ndrill_1 = place_entity(Prototype.ElectricMiningDrill, position=drill_1_position, direction=Direction.DOWN)\nprint(f"Placed ElectricMiningDrill at {drill_1.position} to mine copper ore")\n\n# Place the second electric mining drill next to the first one\ndrill_2_position = drill_1_position.right()\nmove_to(drill_2_position)\ndrill_2 = place_entity(Prototype.ElectricMiningDrill, position=drill_2_position, direction=Direction.DOWN)'
         
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_28():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'water_position = nearest(Resource.Water)\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(offshore_pump)\nbbox = BuildingBox(height = 6, width = 6)\ncoords = nearest_buildable(Prototype.Boiler,bbox,offshore_pump.position)\ntop_left_coord = coords["left_top"]\ncenter = Position(top_left_coord.x +3, top_left_coord.y +3)\nboiler = place_entity(Prototype.Boiler, position = center)\nbbox = BuildingBox(height = 7, width = 7)\ncoords = nearest_buildable(Prototype.SteamEngine,bbox,boiler.position)\ntop_left_coord = coords["left_top"]\ncenter = Position(top_left_coord.x +3, top_left_coord.y +3)\nmove_to(center)\nsteam_engine = place_entity(Prototype.SteamEngine, position = center)\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")

def test_achievements_29():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'belts = connect_entities(Position(x = 10, y = -9), Position(x = -19, y = 22), Prototype.TransportBelt)\nprint(belts)\nprint(belts[0].belts)\npickup_entity(Prototype.TransportBelt, Position(x=-14.5, y=17.5))'

        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nprint(belts)\nprint(belts[0].belts)\npickup_entity(Prototype.TransportBelt, Position(x=1.5, y=0.5))'

        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nprint(belts)\nprint(belts[0].belts)\nfor belt in belts[0].belts:\n    pickup_entity(Prototype.TransportBelt, belt.position)\n    print(f"Pickup belt at {belt.position}")'
        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nprint(len(belts[0].belts))\nprint(belts[0].belts)\nfor belt in belts[0].belts:\n    pickup_entity(Prototype.TransportBelt, belt.position)\n    print(f"Pickup belt at {belt.position}")'

        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nbelts_in_beltgroup = [x.position for x in belts[0].belts]\nprint(len(belts_in_beltgroup))\nprint(belts_in_beltgroup)\nfor i, specific_belt in enumerate(belts_in_beltgroup):\n    pickup_entity(Prototype.TransportBelt, specific_belt)\n    print(i)\nprint(f"done")'

        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nbelts_in_beltgroup = [x.position for x in belts[0].belts]\nprint(len(belts_in_beltgroup))\nprint(belts_in_beltgroup)\nfor i, specific_belt in enumerate(belts_in_beltgroup):\n    pickup_entity(Prototype.TransportBelt, specific_belt)\n    print(i)\nprint(f"done")'
        
        test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.TransportBelt)\nbelts_in_beltgroup = [x.position for x in belts[0].belts]\nprint(len(belts_in_beltgroup))\nprint(belts_in_beltgroup)\npickup_entity(Prototype.BeltGroup, belts[0].position)'
        
        #test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.Pipe)\nprint(belts)\nprint(belts[0].pipes)\nfor belt in belts[0].pipes:\n    pickup_entity(Prototype.Pipe, belt.position)\n    print(f"Pickup belt at {belt.position}")'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_30():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'steam_engine_pos = Position(x=-8.5, y=10.5)\nboiler_pos = Position(x=-8.5, y=5.5)\nwater_pos = nearest(Resource.Water)\nmove_to(water_pos)\noffshore_pump = place_entity(Prototype.OffshorePump,position = water_pos)\nprint(offshore_pump)\nmove_to(boiler_pos)\nboiler =  place_entity(Prototype.Boiler, position = boiler_pos)\ninsert_item(Prototype.Coal, boiler, 20)\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nassert len(water_pipes) == 1\nmove_to(steam_engine_pos)\nengine = place_entity(Prototype.SteamEngine, position = steam_engine_pos)\nsteam_pipes = connect_entities(boiler, engine, Prototype.Pipe)\nassert len(steam_pipes) ==1\nengine=get_entity(Prototype.SteamEngine, engine.position)\nassert engine.energy > 0'
        #test_string_1 = 'belts = connect_entities(Position(x = 1, y = -1), Position(x = -2, y = 0), Prototype.Pipe)\nprint(belts)\nprint(belts[0].pipes)\nfor belt in belts[0].pipes:\n    pickup_entity(Prototype.Pipe, belt.position)\n    print(f"Pickup belt at {belt.position}")'

        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print("asda")


def test_achievements_31():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Step 1: Locate the nearest iron ore patch\niron_ore_position = nearest(Resource.IronOre)\nprint(f"Nearest iron ore patch located at {iron_ore_position}")\n\n# Step 2: Set up 3 electric mining drills on the iron ore patch\n# Define the BuildingBox for the drills. ElectricMiningDrill has 3x3 dimensions.\nbuilding_box = BuildingBox(width=3*3, height=3)\ndrill_positions = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_position)\n\n# Place the electric mining drills\ndrills = []\nfor i in range(3):\n    drill_pos = Position(x=drill_positions.left_top.x + i * 3, y=drill_positions.left_top.y)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)\n    drills.append(drill)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine iron ore")\n\n# Step 3: Place 4 stone furnaces to smelt the iron ore into copper plates\n# Define the BuildingBox for the furnaces. StoneFurnace has 2x2 dimensions.\nfurnace_box = BuildingBox(width=4*2, height=2)\nfurnace_positions = nearest_buildable(Prototype.StoneFurnace, furnace_box, Position(x=drill_positions.left_top.x, y=drill_positions.left_top.y + 5))\n\nfurnaces = []\nfor i in range(4):\n    furnace_pos = Position(x=furnace_positions.left_top.x + i * 2, y=furnace_positions.left_top.y)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    furnaces.append(furnace)\n    print(f"Placed StoneFurnace {i} at {furnace.position} to smelt iron ore into copper plates")\n\n# Step 4: Connect the mining drills to the furnaces using transport belts\nfor drill, furnace in zip(drills, furnaces):\n    belts = connect_entities(drill.drop_position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {drill} to {furnace} with belts: {belts}")\n\n# Step 5: Fuel the furnaces with coal\nfor furnace in furnaces:\n    furnace = insert_item(Prototype.Coal, furnace, quantity=20)\n    print(f"Fueled {furnace} with coal")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Step 1: Set up a power generation system\n# Move to the nearest water source to place an offshore pump\nwater_position = nearest(Resource.Water)\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed OffshorePump at {offshore_pump.position}")\n\n# Place a boiler near the offshore pump\nboiler_position = Position(x=water_position.x + 4, y=water_position.y)\nmove_to(boiler_position)\nboiler = place_entity(Prototype.Boiler, position=boiler_position)\nprint(f"Placed Boiler at {boiler.position}")\n\n# Place a steam engine near the boiler\nsteam_engine_position = Position(x=boiler_position.x + 5, y=boiler_position.y)\nmove_to(steam_engine_position)\nsteam_engine = place_entity(Prototype.SteamEngine, position=steam_engine_position)\nprint(f"Placed SteamEngine at {steam_engine.position}")\n\n# Connect the offshore pump to the boiler and the boiler to the steam engine with pipes\nconnect_entities(offshore_pump, boiler, Prototype.Pipe)\nconnect_entities(boiler, steam_engine, Prototype.Pipe)\n\n# Fuel the boiler with coal\nboiler = insert_item(Prototype.Coal, boiler, quantity=20)\nprint(f"Fueled Boiler at {boiler.position} with coal")\n\n# Step 2: Connect the electric mining drills to the power network\nfor drill in drills:\n    connect_entities(drill, steam_engine, Prototype.SmallElectricPole)\n    print(f"Connected ElectricMiningDrill at {drill.position} to the power network")\n\n# Step 3: Fuel the stone furnaces with coal\nfor furnace in furnaces:\n    furnace = insert_item(Prototype.Coal, furnace, quantity=20)\n    print(f"Fueled StoneFurnace at {furnace.position} with coal")\n\n# Step 4: Retry connecting the mining drills to the furnaces using transport belts\nfor drill, furnace in zip(drills, furnaces):\n    belts = connect_entities(drill.drop_position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {drill} to {furnace} with belts: {belts}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        test_string_1 = '# Step 1: Place chests at the drop positions of the mining drills\nfor drill in drills:\n    drop_position = drill.drop_position\n    move_to(drop_position)\n    chest = place_entity(Prototype.WoodenChest, position=drop_position)\n    print(f"Placed WoodenChest at {chest.position} to collect iron ore from {drill}")\n\n# Step 2: Connect the chests to the furnaces using transport belts\nfor drill, furnace in zip(drills, furnaces):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    belts = connect_entities(chest.position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {chest} to {furnace} with belts: {belts}")\n\n# Step 3: Verify connections and ensure that iron ore reaches the furnaces\n# Wait a few seconds to ensure the system is working\nsleep(10)\n# Check the status of furnaces\nfor furnace in furnaces:\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace.position)\n    assert furnace.status != EntityStatus.NO_INGREDIENTS, f"Furnace at {furnace.position} is not receiving iron ore"\n    print(f"Furnace at {furnace.position} is operational and receiving iron ore")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        
        test_string_1 = '# Step 1: Reconnect the electric mining drills to the power network\n# Identify the nearest electric pole to the mining drills\nnearest_pole_position = nearest(Prototype.SmallElectricPole)\nfor drill in drills:\n    connect_entities(drill, nearest_pole_position, Prototype.SmallElectricPole)\n    print(f"Reconnected ElectricMiningDrill at {drill.position} to the power network")\n\n# Step 2: Verify and adjust the transport belt connections from chests to furnaces\nfor drill, furnace in zip(drills, furnaces):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    # Ensure belts are correctly connecting the chest to the furnace\n    belts = connect_entities(chest.position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {chest} to {furnace} with belts: {belts}")\n\n# Step 3: Verify furnaces are receiving iron ore and are operational\n# Wait a few seconds to ensure the system is working\nsleep(10)\n# Check the status of furnaces\nfor furnace in furnaces:\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace.position)\n    assert furnace.status != EntityStatus.NO_INGREDIENTS, f"Furnace at {furnace.position} is not receiving iron ore"\n    print(f"Furnace at {furnace.position} is operational and receiving iron ore")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Step 1: Verify and ensure the fluid connections from the offshore pump to the boiler and from the boiler to the steam engine\n# Reconnect the offshore pump to the boiler\nconnect_entities(offshore_pump, boiler, Prototype.Pipe)\nprint(f"Reconnected OffshorePump at {offshore_pump.position} to Boiler at {boiler.position}")\n\n# Reconnect the boiler to the steam engine\nconnect_entities(boiler, steam_engine, Prototype.Pipe)\nprint(f"Reconnected Boiler at {boiler.position} to SteamEngine at {steam_engine.position}")\n\n# Step 2: Ensure the boiler is fueled with coal\nboiler = insert_item(Prototype.Coal, boiler, quantity=20)\nprint(f"Fueled Boiler at {boiler.position} with coal")\n\n# Step 3: Verify the power network is active and electric mining drills are operational\n# Wait a few seconds to ensure the power network is active\nsleep(10)\n# Check the status of electric mining drills\nfor drill in drills:\n    drill = get_entity(Prototype.ElectricMiningDrill, position=drill.position)\n    assert drill.status != EntityStatus.NO_POWER, f"ElectricMiningDrill at {drill.position} is not receiving power"\n    print(f"ElectricMiningDrill at {drill.position} is operational and receiving power")\n\n# Step 4: Verify transport belt connections from chests to furnaces\nfor drill, furnace in zip(drills, furnaces):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    belts = connect_entities(chest.position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {chest} to {furnace} with belts: {belts}")\n\n# Wait a few seconds to ensure the system is working\nsleep(10)\n# Check the status of furnaces\nfor furnace in furnaces:\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace.position)\n    assert furnace.status != EntityStatus.NO_INGREDIENTS, f"Furnace at {furnace.position} is not receiving iron ore"\n    print(f"Furnace at {furnace.position} is operational and receiving iron ore")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Step 1: Remove the existing boiler\nmove_to(boiler.position)\npickup_entity(Prototype.Boiler, position=boiler.position)\nprint(f"Removed Boiler from {boiler.position}")\n\n# Step 2: Find a suitable position for the boiler\n# Define a new position for the boiler with clear connection points\nnew_boiler_position = Position(x=offshore_pump.position.x + 3, y=offshore_pump.position.y)\nmove_to(new_boiler_position)\nboiler = place_entity(Prototype.Boiler, position=new_boiler_position)\nprint(f"Placed Boiler at {boiler.position} with clear connection points")\n\n# Step 3: Reconnect the offshore pump to the newly positioned boiler\nconnect_entities(offshore_pump, boiler, Prototype.Pipe)\nprint(f"Connected OffshorePump at {offshore_pump.position} to Boiler at {boiler.position}")\n\n# Step 4: Reconnect the boiler to the steam engine\nconnect_entities(boiler, steam_engine, Prototype.Pipe)\nprint(f"Connected Boiler at {boiler.position} to SteamEngine at {steam_engine.position}")\n\n# Step 5: Ensure the boiler is fueled with coal\nboiler = insert_item(Prototype.Coal, boiler, quantity=20)\nprint(f"Fueled Boiler at {boiler.position} with coal")\n\n# Step 6: Verify the power network is active and electric mining drills are operational\n# Wait a few seconds to ensure the power network is active\nsleep(10)\n# Check the status of electric mining drills\nfor drill in drills:\n    drill = get_entity(Prototype.ElectricMiningDrill, position=drill.position)\n    assert drill.status != EntityStatus.NO_POWER, f"ElectricMiningDrill at {drill.position} is not receiving power"\n    print(f"ElectricMiningDrill at {drill.position} is operational and receiving power")\n\n# Step 7: Verify transport belt connections from chests to furnaces\nfor drill, furnace in zip(drills, furnaces):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    belts = connect_entities(chest.position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {chest} to {furnace} with belts: {belts}")\n\n# Wait a few seconds to ensure the system is working\nsleep(10)\n# Check the status of furnaces\nfor furnace in furnaces:\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace.position)\n    assert furnace.status != EntityStatus.NO_INGREDIENTS, f"Furnace at {furnace.position} is not receiving iron ore"\n    print(f"Furnace at {furnace.position} is operational and receiving iron ore")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print("asda")


def test_achievements_32():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find water source for power system\nwater_pos = Position(x=-1.0 ,y=28.0)\nprint(f"Found water source at {water_pos}")\n\n# Place offshore pump\nmove_to(water_pos)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed offshore pump at {offshore_pump.position}")\n\n# Place boiler next to pump\nbuilding_box = BuildingBox(width=3, height=3)\nbuildable_coords = nearest_buildable(Prototype.Boiler, building_box, offshore_pump.position)\nboiler_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\nmove_to(boiler_pos)\nboiler = place_entity(Prototype.Boiler, position=boiler_pos)\nprint(f"Placed boiler at {boiler.position}")\n\n# Place steam engine next to boiler\nbuilding_box = BuildingBox(width=3, height=3)\nbuildable_coords = nearest_buildable(Prototype.SteamEngine, building_box, boiler.position)\nengine_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\nmove_to(engine_pos)\nsteam_engine = place_entity(Prototype.SteamEngine, position=engine_pos)\nprint(f"Placed steam engine at {steam_engine.position}")\n# Connect offshore pump to boiler with pipes\npump_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pump_to_boiler}")\n\n# Connect boiler to steam engine with pipes\nboiler_to_engine = connect_entities(boiler.position, steam_engine.position, Prototype.Pipe)\nprint(f"Connected boiler to steam engine with pipes: {boiler_to_engine}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print("asda")


def test_achievements_33():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore patch at {iron_ore_pos}")\n\n# Place 3 electric mining drills with smaller building boxes\ndrill_positions = []\nfor i in range(3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n    drill_positions.append(drill.position)\n    # Update iron_ore_pos to be near last placed drill for next iteration\n    iron_ore_pos = drill.position\n\n# Place 4 stone furnaces with their own building boxes\nfurnace_positions = []\nfor i in range(4):\n    # Use 2x2 building box for each furnace\n    building_box = BuildingBox(width=2, height=2)\n    # Place furnaces 4 tiles below the drills\n    furnace_center = Position(x=drill_positions[0].x + i*2, y=drill_positions[0].y + 4)\n    buildable_coords = nearest_buildable(Prototype.StoneFurnace, building_box, furnace_center)\n    \n    # Place furnace at center of buildable area\n    furnace_pos = Position(x=buildable_coords.left_top.x + 1, y=buildable_coords.left_top.y + 1)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    print(f"Placed stone furnace {i+1} at {furnace.position}")\n    furnace_positions.append(furnace.position)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        #test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore patch at {iron_ore_pos}")\n\n# Place 3 electric mining drills with smaller building boxes\ndrill_positions = []\nfor i in range(3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n    drill_positions.append(drill.position)\n    # Update iron_ore_pos to be near last placed drill for next iteration\n    iron_ore_pos = drill.position\n\n# Place 4 stone furnaces with their own building boxes\nfurnace_positions = []\nfor i in range(4):\n    # Use 2x2 building box for each furnace\n    building_box = BuildingBox(width=2, height=2)\n    # Place furnaces 4 tiles below the drills\n    furnace_center = Position(x=drill_positions[0].x + i*2, y=drill_positions[0].y + 4)\n    buildable_coords = nearest_buildable(Prototype.StoneFurnace, building_box, furnace_center)\n    \n    # Place furnace at center of buildable area\n    furnace_pos = Position(x=buildable_coords.left_top.x + 1, y=buildable_coords.left_top.y + 1)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    print(f"Placed stone furnace {i+1} at {furnace.position}")\n    furnace_positions.append(furnace.position)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore patch at {iron_ore_pos}")\n\n# Place 3 electric mining drills with smaller building boxes\ndrill_positions = []\nfor i in range(3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n    drill_positions.append(drill.position)\n    # Update iron_ore_pos to be near last placed drill for next iteration\n    iron_ore_pos = drill.position'
        
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Place remaining 2 electric mining drills\nfor i in range(1, 3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, Position(x=-12.5 + i*3, y=24.5))\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n\n# Place remaining 3 stone furnaces\nfor i in range(1, 4):\n    # Use 2x2 building box for each furnace\n    building_box = BuildingBox(width=2, height=2)\n    # Place furnaces 4 tiles below the first drill\n    furnace_center = Position(x=-11.0 + i*2, y=30.0)\n    buildable_coords = nearest_buildable(Prototype.StoneFurnace, building_box, furnace_center)\n    \n    # Place furnace at center of buildable area\n    furnace_pos = Position(x=buildable_coords.left_top.x + 1, y=buildable_coords.left_top.y + 1)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    print(f"Placed stone furnace {i+1} at {furnace.position}")\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print("asda")

def test_achievements_34():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore patch at {iron_ore_pos}")\n\n# Place 3 electric mining drills with smaller building boxes\ndrill_positions = []\nfor i in range(3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n    drill_positions.append(drill.position)\n    # Update iron_ore_pos to be near last placed drill for next iteration\n    iron_ore_pos = drill.position\n\n# Place 4 stone furnaces with their own building boxes\nfurnace_positions = []\nfor i in range(4):\n    # Use 2x2 building box for each furnace\n    building_box = BuildingBox(width=2, height=2)\n    # Place furnaces 4 tiles below the drills\n    furnace_center = Position(x=drill_positions[0].x + i*2, y=drill_positions[0].y + 4)\n    buildable_coords = nearest_buildable(Prototype.StoneFurnace, building_box, furnace_center)\n    \n    # Place furnace at center of buildable area\n    furnace_pos = Position(x=buildable_coords.left_top.x + 1, y=buildable_coords.left_top.y + 1)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    print(f"Placed stone furnace {i+1} at {furnace.position}")\n    furnace_positions.append(furnace.position)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        #test_string_1 = '# Find iron ore patch\niron_ore_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore patch at {iron_ore_pos}")\n\n# Place 3 electric mining drills with smaller building boxes\ndrill_positions = []\nfor i in range(3):\n    # Use 3x3 building box for each drill\n    building_box = BuildingBox(width=3, height=3)\n    buildable_coords = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_pos)\n    \n    # Place drill at center of buildable area\n    drill_pos = Position(x=buildable_coords.left_top.x + 1.5, y=buildable_coords.left_top.y + 1.5)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos, direction=Direction.DOWN)\n    print(f"Placed electric mining drill {i+1} at {drill.position}")\n    drill_positions.append(drill.position)\n    # Update iron_ore_pos to be near last placed drill for next iteration\n    iron_ore_pos = drill.position\n\n# Place 4 stone furnaces with their own building boxes\nfurnace_positions = []\nfor i in range(4):\n    # Use 2x2 building box for each furnace\n    building_box = BuildingBox(width=2, height=2)\n    # Place furnaces 4 tiles below the drills\n    furnace_center = Position(x=drill_positions[0].x + i*2, y=drill_positions[0].y + 4)\n    buildable_coords = nearest_buildable(Prototype.StoneFurnace, building_box, furnace_center)\n    \n    # Place furnace at center of buildable area\n    furnace_pos = Position(x=buildable_coords.left_top.x + 1, y=buildable_coords.left_top.y + 1)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    print(f"Placed stone furnace {i+1} at {furnace.position}")\n    furnace_positions.append(furnace.position)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        test_string_1 = 'for i in range(3):\n    print(i)'
        score, goal, result = instance.eval_with_error(test_string_1, 300)
        
        print("asda")



def test_achievements_35():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'move_to(Position(x = 4, y = -12))\nengine = place_entity(Prototype.ElectricMiningDrill, position = Position(x = 4, y = -12))\npickup_entity(Prototype.ElectricMiningDrill, engine.position)'
        score, goal, result = instance.eval_with_error(test_string_1, 300)
        
        print("asda")



def test_achievements_35():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'water_pos = Position(x=-13.5, y=-1.5)\nprint(f"Found water source at {water_pos}")\n\n# Place offshore pump\nmove_to(water_pos)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed offshore pump at {offshore_pump.position}")\nboiler_pos = Position(x=-28.5, y=1.0)\nmove_to(boiler_pos)\nboiler = place_entity(Prototype.Boiler, position=boiler_pos)\nprint(f"Placed boiler at {boiler.position}")\nengine_pos = Position(x=-4.5, y=0.5)\nmove_to(engine_pos)\nsteam_engine = place_entity(Prototype.SteamEngine, position=engine_pos)\nprint(f"Placed steam engine at {steam_engine.position}")\n# Connect offshore pump to boiler with pipes\npump_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pump_to_boiler}")\n\n# Connect boiler to steam engine with pipes\nboiler_to_engine = connect_entities(boiler.position, steam_engine.position, Prototype.Pipe)\nprint(f"Connected boiler to steam engine with pipes: {boiler_to_engine}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print("asda")

def test_achievements_36():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Locate the nearest copper ore patch\ncopper_ore_position = nearest(Resource.CopperOre)\n\n# Define the number of drills needed and place them\nnum_drills = 3\ndrills = []\n\n# Place electric mining drills on the copper ore patch\nfor i in range(num_drills):\n    # Calculate positions with proper spacing\n    drill_position = Position(\n        x=copper_ore_position.x + i * 3,  # Assuming each drill occupies 3 tiles\n        y=copper_ore_position.y\n    )\n    move_to(drill_position)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_position)\n    drills.append(drill)\n    print(f"Placed ElectricMiningDrill {i+1} at {drill.position} to mine copper ore")\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        
        test_string_1 = '# Locate the nearest water source for the offshore pump\nwater_position = nearest(Resource.Water)\n\n# Move to the water position and place the offshore pump\nmove_to(water_position)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump at {offshore_pump.position}")\n\n# Place the boiler close to the offshore pump\nboiler_position = Position(x=offshore_pump.position.x + 2, y=offshore_pump.position.y)\nmove_to(boiler_position)\nboiler = place_entity(Prototype.Boiler, position=boiler_position)\nprint(f"Placed boiler at {boiler.position}")\n\n# Place the steam engine close to the boiler\nsteam_engine_position = Position(x=boiler.position.x + 2, y=boiler.position.y)\nmove_to(steam_engine_position)\nsteam_engine = place_entity(Prototype.SteamEngine, position=steam_engine_position)\nprint(f"Placed steam engine at {steam_engine.position}")\n\n# Connect the offshore pump to the boiler\nwater_pipes = connect_entities(offshore_pump, boiler, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {water_pipes}")\n\n# Connect the boiler to the steam engine\nsteam_pipes = connect_entities(boiler, steam_engine, Prototype.Pipe)\nprint(f"Connected boiler to steam engine with pipes: {steam_pipes}")\n\n# Add fuel to the boiler\nboiler = insert_item(Prototype.Coal, boiler, quantity=20)\nprint(f"Added fuel to boiler at {boiler.position}")\n\n# Connect the electric mining drills to the power network using small electric poles\nfor drill in drills:\n    connect_entities(drill, steam_engine, Prototype.SmallElectricPole)\n    print(f"Connected electric mining drill at {drill.position} to power network")\n\nprint(f"Updated entities on the map: {get_entities()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = 'steam_engine_position = nearest(Prototype.SteamEngine)\nprint(f"Found steam engine at {steam_engine_position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


        print("asda")

## BUG 1
def test_achievements_36():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'furnace = place_entity(Prototype.StoneFurnace, position = Position(x = 2, y = 0))\nblets = connect_entities(Position(x = 0, y = 0), furnace.position, Prototype.TransportBelt)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print("asda")


## BUG 2
def test_achievements_37():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'boiler_position = Position(x=3.5, y=28.0)\nmove_to(boiler_position)\nboiler = place_entity(Prototype.Boiler, position=boiler_position)'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print("asda")



## BUG 2
def test_achievements_38():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Step 1: Locate the nearest iron ore patch\niron_ore_position = nearest(Resource.IronOre)\nprint(f"Nearest iron ore patch located at {iron_ore_position}")\n\n# Step 2: Set up 3 electric mining drills on the iron ore patch\n# Define the BuildingBox for the drills. ElectricMiningDrill has 3x3 dimensions.\nbuilding_box = BuildingBox(width=3*3, height=3)\ndrill_positions = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_position)\n\n# Place the electric mining drills\ndrills = []\nfor i in range(3):\n    drill_pos = Position(x=drill_positions.left_top.x + i * 3, y=drill_positions.left_top.y)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)\n    drills.append(drill)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine iron ore")\n\n# Step 3: Place 4 stone furnaces to smelt the iron ore into copper plates\n# Define the BuildingBox for the furnaces. StoneFurnace has 2x2 dimensions.\nfurnace_box = BuildingBox(width=4*2, height=2)\nfurnace_positions = nearest_buildable(Prototype.StoneFurnace, furnace_box, Position(x=drill_positions.left_top.x, y=drill_positions.left_top.y + 5))\n\nfurnaces = []\nfor i in range(4):\n    furnace_pos = Position(x=furnace_positions.left_top.x + i * 2, y=furnace_positions.left_top.y)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    furnaces.append(furnace)\n    print(f"Placed StoneFurnace {i} at {furnace.position} to smelt iron ore into copper plates")\n\n# Step 4: Connect the mining drills to the furnaces using transport belts\nfor drill, furnace in zip(drills, furnaces):\n    belts = connect_entities(drill.drop_position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {drill} to {furnace} with belts: {belts}")\n\n# Step 5: Fuel the furnaces with coal\nfor furnace in furnaces:\n    furnace = insert_item(Prototype.Coal, furnace, quantity=20)\n    print(f"Fueled {furnace} with coal")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Step 1: Place chests at the drop positions of the mining drills\nfor drill in drills:\n    drop_position = drill.drop_position\n    move_to(drop_position)\n    chest = place_entity(Prototype.WoodenChest, position=drop_position)\n    print(f"Placed WoodenChest at {chest.position} to collect iron ore from {drill}")\n\n# Step 2: Connect the chests to the furnaces using transport belts\nfor drill, furnace in zip(drills, furnaces):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    belts = connect_entities(chest.position, furnace.position, Prototype.TransportBelt)\n    print(f"Connected {chest} to {furnace} with belts: {belts}")\n\n# Step 3: Verify connections and ensure that iron ore reaches the furnaces\n# Wait a few seconds to ensure the system is working\nsleep(10)\n# Check the status of furnaces\nfor furnace in furnaces:\n    furnace = get_entity(Prototype.StoneFurnace, position=furnace.position)\n    assert furnace.status != EntityStatus.NO_INGREDIENTS, f"Furnace at {furnace.position} is not receiving iron ore"\n    print(f"Furnace at {furnace.position} is operational and receiving iron ore")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)


        print("asda")



## BUG 2
def test_achievements_39():
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Step 1: Locate the nearest iron ore patch\niron_ore_position = nearest(Resource.IronOre)\nprint(f"Nearest iron ore patch located at {iron_ore_position}")\n\n# Step 2: Set up 3 electric mining drills on the iron ore patch\n# Define the BuildingBox for the drills. ElectricMiningDrill has 3x3 dimensions.\nbuilding_box = BuildingBox(width=3*3, height=3)\ndrill_positions = nearest_buildable(Prototype.ElectricMiningDrill, building_box, iron_ore_position)\n\n# Place the electric mining drills\ndrills = []\nfor i in range(3):\n    drill_pos = Position(x=drill_positions.left_top.x + i * 3, y=drill_positions.left_top.y)\n    move_to(drill_pos)\n    drill = place_entity(Prototype.ElectricMiningDrill, position=drill_pos)\n    drills.append(drill)\n    print(f"Placed ElectricMiningDrill {i} at {drill.position} to mine iron ore")\n    chest = place_entity(Prototype.WoodenChest, position=drill.drop_position)\n\n# Step 3: Place 4 stone furnaces to smelt the iron ore into copper plates\n# Define the BuildingBox for the furnaces. StoneFurnace has 2x2 dimensions.\nfurnace_box = BuildingBox(width=4*2, height=2)\nfurnace_positions = nearest_buildable(Prototype.StoneFurnace, furnace_box, Position(x=drill_positions.left_top.x, y=drill_positions.left_top.y + 5))\n\ninserters = []\nfor i in range(4):\n    furnace_pos = Position(x=furnace_positions.left_top.x + i * 2, y=furnace_positions.left_top.y+2)\n    move_to(furnace_pos)\n    furnace = place_entity(Prototype.StoneFurnace, position=furnace_pos)\n    inserter = place_entity_next_to(Prototype.BurnerInserter, reference_position=furnace_pos, direction = Direction.UP, spacing = 0)\n    inserter = rotate_entity(inserter, Direction.DOWN)\n    inserters.append(inserter)\n# Step 2: Connect the chests to the furnaces using transport belts\nfor drill, inserter in zip(drills, inserters):\n    chest = get_entity(Prototype.WoodenChest, position=drill.drop_position)\n    belts = connect_entities(chest.position, inserter.pickup_position, Prototype.TransportBelt)\n    print(f"Connected chest to furnace with belts: {len(belts)}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print("asda")


def test_achievements_40(): # For appendix
        PLACEMENT_STARTING_INVENTORY = {"coal": 200, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = 'water_pos = nearest(Resource.Water)\nprint(f"Found water source at {water_pos}")\n\n# Place offshore pump\nmove_to(water_pos)\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed offshore pump at {offshore_pump.position}")\n\nboiler = place_entity_next_to(Prototype.Boiler, reference_position=offshore_pump.position, spacing = 4, direction = Direction.RIGHT)\nprint(f"Placed boiler at {boiler.position}")\nsteam_engine = place_entity_next_to(Prototype.SteamEngine, reference_position=boiler.position, spacing = 5, direction = Direction.RIGHT)\nprint(f"Placed steam engine at {steam_engine.position}")\n# Connect offshore pump to boiler with pipes\npump_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pump_to_boiler}")\n\n# Connect boiler to steam engine with pipes\nboiler_to_engine = connect_entities(boiler.position, steam_engine.position, Prototype.Pipe)\nprint(f"Connected boiler to steam engine with pipes: {boiler_to_engine}")\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = 'iron_pos = nearest(Resource.IronOre)\nmove_to(iron_pos)\ndrill = place_entity(Prototype.ElectricMiningDrill, position = iron_pos)\nprint(f"Put a drill to mine iron at {drill.position}")\nsteam_engine = get_entity(Prototype.SteamEngine, position = Position(x = 3.5, y=-0.5))\npoles = connect_entities(steam_engine,drill,Prototype.SmallElectricPole)\nprint(f"Used poles {poles} to power drill at {drill.position}")\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print(f"asd")


def test_achievements_41(): # DEMO
        PLACEMENT_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '# Find iron ore patch and get position\niron_pos = nearest(Resource.IronOre)\nprint(f"Found iron ore at {iron_pos}")\n\n# Define building box for drill (2x2) plus furnace (2x2)\nbuilding_box = BuildingBox(width=2, height=4)\n\n# Get buildable area\nbuildable_coords = nearest_buildable(Prototype.BurnerMiningDrill, building_box, iron_pos)\ndrill_pos = buildable_coords.left_top\n\n# Place drill\nmove_to(drill_pos)\ndrill = place_entity(Prototype.BurnerMiningDrill, position=drill_pos, direction=Direction.DOWN)\nprint(f"Placed drill at {drill.position}")\n\n# Place furnace at drop position\nfurnace = place_entity(Prototype.StoneFurnace, position=drill.drop_position)\nprint(f"Placed furnace at {furnace.position}")\n\n# Add coal to drill\ndrill = insert_item(Prototype.Coal, drill, quantity=50)\nprint(f"Added coal to drill")\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Get current entities\ndrill = get_entity(Prototype.BurnerMiningDrill, Position(x=-13.0, y=22.0))\nfurnace = get_entity(Prototype.StoneFurnace, Position(x=-12.0, y=24.0))\n\n# Add coal to furnace\nfurnace = insert_item(Prototype.Coal, furnace, quantity=50)\nprint(f"Added coal to furnace")\n\n# Place inserter between drill and furnace\ninserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nprint(f"Placed inserter at {inserter.position}")\n\n# Add coal to inserter\ninserter = insert_item(Prototype.Coal, inserter, quantity=50)\nprint(f"Added coal to inserter")\n\n# Log current state\nprint(f"Current inventory: {inspect_inventory()}")\nprint(f"Updated entities: {get_entities()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print(f"asd")

        test_string_1 = '# Find water and setup power\nwater_pos = nearest(Resource.Water)\nprint(f"Found water at {water_pos}")\n\n# Place offshore pump\nmove_to(water_pos)\npump = place_entity(Prototype.OffshorePump, position=water_pos)\nprint(f"Placed pump at {pump.position}")\n\n# Place boiler with spacing of 3 to ensure room for pipes\nboiler = place_entity_next_to(\n    Prototype.Boiler,\n    reference_position=pump.position,\n    direction=Direction.LEFT,\n    spacing=3\n)\nprint(f"Placed boiler at {boiler.position}")\n\n# Add coal to boiler\nboiler = insert_item(Prototype.Coal, boiler, quantity=50)\n\n# Place steam engine with spacing of 3\nengine = place_entity_next_to(\n    Prototype.SteamEngine,\n    reference_position=boiler.position,\n    direction=Direction.DOWN,\n    spacing=3\n)\nprint(f"Placed steam engine at {engine.position}")\n\n# Connect pump to boiler to steam engine with pipes\nconnect_entities(pump, boiler, Prototype.Pipe)\nconnect_entities(boiler, engine, Prototype.Pipe)\n\n# Place assembling machine 10 spaces away from furnace\nfurnace = get_entity(Prototype.StoneFurnace, Position(x=-12.0, y=24.0))\ntarget_pos = Position(x=furnace.position.x + 10, y=furnace.position.y)\n\n# Define building box for assembling machine (3x3) plus inserter (1x1)\nbuilding_box = BuildingBox(width=4, height=3)\nbuildable_coords = nearest_buildable(Prototype.AssemblingMachine1, building_box, target_pos)\n\n# Place assembling machine\nmove_to(buildable_coords.left_top)\nassembler = place_entity(Prototype.AssemblingMachine1, position=buildable_coords.left_top)\nprint(f"Placed assembling machine at {assembler.position}")\n\n# Connect power with electric poles\nconnect_entities(engine.position, assembler.position, Prototype.SmallElectricPole)\n\n# Set recipe for iron gear wheels\nset_entity_recipe(assembler, Prototype.IronGearWheel)\n\nprint(f"Current entities: {get_entities()}")\nprint(f"Current inventory: {inspect_inventory()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Get current entities\nfurnace = get_entity(Prototype.StoneFurnace, Position(x=-12.0, y=24.0))\nassembler = get_entity(Prototype.AssemblingMachine1, Position(x=3.5, y=29.5))\n\n# Place inserter next to furnace to take out plates\nfurnace_output_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=furnace.position,\n    direction=Direction.RIGHT,\n    spacing=0\n)\nprint(f"Placed furnace output inserter at {furnace_output_inserter.position}")\n\n# Add coal to inserter\nfurnace_output_inserter = insert_item(Prototype.Coal, furnace_output_inserter, quantity=50)\n\n# Place inserter next to assembling machine to input plates\nassembler_input_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=assembler.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nprint(f"Placed assembler input inserter at {assembler_input_inserter.position}")\n\n# Rotate assembler input inserter to face assembler\nassembler_input_inserter = rotate_entity(assembler_input_inserter, Direction.UP)\n\n# Add coal to inserter\nassembler_input_inserter = insert_item(Prototype.Coal, assembler_input_inserter, quantity=50)\n\n# Connect the two inserters with transport belt\nbelts = connect_entities(\n    furnace_output_inserter.drop_position,\n    assembler_input_inserter.pickup_position,\n    Prototype.TransportBelt\n)\nprint(f"Connected inserters with transport belts")\n\n# Add output inserter for iron gear wheels\noutput_inserter = place_entity_next_to(\n    Prototype.BurnerInserter,\n    reference_position=assembler.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nprint(f"Placed output inserter at {output_inserter.position}")\n\n# Add coal to output inserter\noutput_inserter = insert_item(Prototype.Coal, output_inserter, quantity=50)\n\n# Place chest to collect gear wheels\nchest = place_entity_next_to(\n    Prototype.WoodenChest,\n    reference_position=output_inserter.position,\n    direction=Direction.DOWN,\n    spacing=0\n)\nprint(f"Placed collection chest at {chest.position}")\n\nprint(f"Current entities: {get_entities()}")\nprint(f"Current inventory: {inspect_inventory()}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        print(f"asd")


def test_achievements_42(): # DEMO
        from search.model.game_state import GameState
        PLACEMENT_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        test_string_1 = '\niron_ore_loc = nearest(Resource.IronOre)\nprint(f"found iron ore at {iron_ore_loc}")\nmove_to(iron_ore_loc)\nprint(f"Moved to iron ore location")\ndrill = place_entity(Prototype.BurnerMiningDrill, position = iron_ore_loc)\ndrill = insert_item(Prototype.Coal, drill, 30)\nprint(f"Placed drill at iron ore location ({drill.position}) and inserted coal")\nfurnace_pos = Position(x = drill.position.x - 9, y =  drill.position.y)\nbelts = connect_entities(drill.drop_position, furnace_pos, Prototype.TransportBelt)\nprint(f"Connected drill at {drill.position} to {furnace_pos} with belts {belts}")\n# wait for 10 seconds and check if furnace is smelting plates\nsleep(30)\nprint(get_entities())'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        game_state = GameState.from_instance(instance)
        instance.reset(game_state)
        test_string_1 = 'print(get_entities())'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)
        
        print(f"asd")


def test_achievements_43(): # DEMO
        from search.model.game_state import GameState
        PLACEMENT_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = '\n# log your general idea what you will do next\nprint(f"I will create a power generation setup with a steam engine")\n# get the water position\nwater_position = nearest(Resource.Water)\n# moveto water positon\nmove_to(water_position)\n# first place offshore pump on the water system\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump to get water at {offshore_pump.position}")\n# place the boiler next to offshore pump\nboiler = place_entity_next_to(Prototype.Boiler, reference_position = offshore_pump.position, spacing = 1, direction = Direction.DOWN)'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Use nearest_buildable to find a valid position for the boiler\n# The boiler has a dimension of 2x3, so we need to ensure there is enough space\nboiler_building_box = BuildingBox(width=3, height=2)\noffshore_pump_position = Position(x=-10.5, y=1.5)\noffshore_pump = get_entity(Prototype.OffshorePump, position = offshore_pump_position)\n\n# Find the nearest buildable position for the boiler\nboiler_bounding_box = nearest_buildable(\n    Prototype.Boiler,\n    building_box=boiler_building_box,\n    center_position=offshore_pump_position\n)\n\n# Log the found position for the boiler\nprint(f"Found buildable position for boiler: {boiler_bounding_box.center()}")\n\n# Move to the center of the bounding box and place the boiler\nmove_to(boiler_bounding_box.center())\nboiler = place_entity(Prototype.Boiler, position=boiler_bounding_box.center())\nprint(f"Placed boiler at {boiler.position}")\n\n# Connect the offshore pump to the boiler with pipes\npipes_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pipes_to_boiler}")\nsleep(2)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = 'water_position = nearest(Resource.Water)\n# moveto water positon\nmove_to(water_position)\n# first place offshore pump on the water system\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump to get water at {offshore_pump.position}")\n# Use nearest_buildable to find a valid position for the boiler\n# The boiler has a dimension of 2x3, so we need to ensure there is enough space\nboiler_building_box = BuildingBox(width=3, height=2)\nboiler_bounding_box = nearest_buildable(\n    Prototype.Boiler,\n    building_box=boiler_building_box,\n    center_position=offshore_pump.position\n)\n\n# Log the found position for the boiler\nprint(f"Found buildable position for boiler: {boiler_bounding_box.center()}")\n\n# Move to the center of the bounding box and place the boiler\nmove_to(boiler_bounding_box.center())\nboiler = place_entity(Prototype.Boiler, position=boiler_bounding_box.center())\nprint(f"Placed boiler at {boiler.position}")\n\n# Connect the offshore pump to the boiler with pipes\npipes_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pipes_to_boiler}")\nsleep(2)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = 'water_position = nearest(Resource.Water)\n# moveto water positon\nmove_to(water_position)\n# first place offshore pump on the water system\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump to get water at {offshore_pump.position}")\n# Use nearest_buildable to find a valid position for the boiler\n# The boiler has a dimension of 2x3, so we need to ensure there is enough space\nboiler_building_box = BuildingBox(width=3, height=2)\nboiler_bounding_box = nearest_buildable(\n    Prototype.Boiler,\n    building_box=boiler_building_box,\n    center_position=offshore_pump.position\n)\n\n# Log the found position for the boiler\nprint(f"Found buildable position for boiler: {boiler_bounding_box.center()}")\n\n# Move to the center of the bounding box and place the boiler\nmove_to(boiler_bounding_box.center())\nboiler = place_entity(Prototype.Boiler, position=boiler_bounding_box.center())\nprint(f"Placed boiler at {boiler.position}")\n\n# Connect the offshore pump to the boiler with pipes\npipes_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pipes_to_boiler}")\nsleep(2)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        
        print(f"asd")


def test_achievements_44(): # DEMO
        from search.model.game_state import GameState
        PLACEMENT_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 200,
                                "stone-furnace": 5, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 200, "pipe": 100,
                                "assembling-machine-1": 5}
        instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=PLACEMENT_STARTING_INVENTORY) 

        #test_string_1 = '\n# log your general idea what you will do next\nprint(f"I will create a power generation setup with a steam engine")\n# get the water position\nwater_position = nearest(Resource.Water)\n# moveto water positon\nmove_to(water_position)\n# first place offshore pump on the water system\noffshore_pump = place_entity(Prototype.OffshorePump, position=water_position)\nprint(f"Placed offshore pump to get water at {offshore_pump.position}")\n# place the boiler next to offshore pump\nboiler = place_entity_next_to(Prototype.Boiler, reference_position = offshore_pump.position, spacing = 1, direction = Direction.DOWN)'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        #test_string_1 = '# Use nearest_buildable to find a valid position for the boiler\n# The boiler has a dimension of 2x3, so we need to ensure there is enough space\nboiler_building_box = BuildingBox(width=3, height=2)\noffshore_pump_position = Position(x=-10.5, y=1.5)\noffshore_pump = get_entity(Prototype.OffshorePump, position = offshore_pump_position)\n\n# Find the nearest buildable position for the boiler\nboiler_bounding_box = nearest_buildable(\n    Prototype.Boiler,\n    building_box=boiler_building_box,\n    center_position=offshore_pump_position\n)\n\n# Log the found position for the boiler\nprint(f"Found buildable position for boiler: {boiler_bounding_box.center()}")\n\n# Move to the center of the bounding box and place the boiler\nmove_to(boiler_bounding_box.center())\nboiler = place_entity(Prototype.Boiler, position=boiler_bounding_box.center())\nprint(f"Placed boiler at {boiler.position}")\n\n# Connect the offshore pump to the boiler with pipes\npipes_to_boiler = connect_entities(offshore_pump.position, boiler.position, Prototype.Pipe)\nprint(f"Connected offshore pump to boiler with pipes: {pipes_to_boiler}")\nsleep(2)\nprint(f"Current inventory {inspect_inventory()}")\nprint(f"Updated entities on the map: {get_entities()}")\n'
        #output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        test_string_1 = '# Step 1: Locate the nearest water source for power generation\nwater_pos = nearest(Resource.Water)\nprint(f"Found water source at {water_pos}")\n\n# Define a safe area for boiler and steam engine placement\nboiler_steam_box = BuildingBox(width=5, height=5)\nboiler_area = nearest_buildable(Prototype.Boiler, boiler_steam_box, water_pos)\n\n# Place boiler\nboiler_pos = boiler_area.left_top\nmove_to(boiler_pos)\nboiler = place_entity(Prototype.Boiler, position=boiler_pos)\nprint(f"Placed Boiler at {boiler.position}")'
        output_list, result, error, achievements = eval_program_with_achievements(instance, test_string_1)

        print(f"asd")
if __name__ == '__main__':
        
    #unittest.main()
    test_achievements_44()
    #test_achievements_38()