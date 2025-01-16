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
                                tcp_port=27015,
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

if __name__ == '__main__':
    #unittest.main()
    test_achievements_1()    