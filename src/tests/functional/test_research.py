import pytest

from factorio_entities import Position
from factorio_instance import Direction, FactorioInstance
from factorio_types import Resource, Prototype, PrototypeName, Technology
from search.model.game_state import GameState


@pytest.fixture()
def game(instance):
    initial_inventory = {
        'coal': 50,
        'copper-plate': 50,
        'iron-plate': 50,
        'iron-chest': 2,
        'burner-mining-drill': 3,
        'assembling-machine-1': 1,
        'boiler': 1,
        'steam-engine': 1,
        'stone-furnace': 10,
        'burner-inserter': 32,
        'offshore-pump': 4,
        'pipe': 100,
        'small-electric-pole': 50,
        'transport-belt': 100,
        'lab': 1,
        'automation-science-pack': 10,
    }
    instance = FactorioInstance(address='localhost',
                                         bounding_box=200,
                                         tcp_port=27015,
                                         fast=True,
                                         all_technologies_researched=False,
                                         inventory=initial_inventory)
    instance.reset()
    yield instance.namespace


def test_craft_automation_packs_and_research(game):
    inventory = game.inspect_inventory()
    # place the offshore pump at nearest water source
    game.move_to(game.nearest(Resource.Water))
    offshore_pump = game.place_entity(Prototype.OffshorePump,
                                      position=game.nearest(Resource.Water),
                                      direction=Direction.LEFT)
    # place the boiler next to the offshore pump
    boiler = game.place_entity_next_to(Prototype.Boiler,
                                       reference_position=offshore_pump.position,
                                       direction=offshore_pump.direction,
                                       spacing=3)
    game.insert_item(Prototype.Coal, boiler, quantity=10)

    # place the steam engine next to the boiler
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine,
                                             reference_position=boiler.position,
                                             direction=boiler.direction,
                                             spacing=2)

    # Place a Lab
    lab = game.place_entity_next_to(Prototype.Lab,
                                    reference_position=steam_engine.position,
                                    direction=steam_engine.direction,
                                    spacing=2)
    assert lab, "Failed to place Lab"

    # place connect the steam engine and assembly machine with power poles
    game.connect_entities(steam_engine, lab, connection_type=Prototype.SmallElectricPole)

    # place connective pipes between the boiler and steam engine
    game.connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)

    # place connective pipes between the boiler and offshore pump
    game.connect_entities(boiler, offshore_pump, connection_type=Prototype.Pipe)


    # Insert science packs into the Lab
    game.insert_item(Prototype.AutomationSciencePack, lab, quantity=10)

    # Verify science packs were inserted
    lab_inventory = game.inspect_inventory(lab)
    assert lab_inventory.get(
        Prototype.AutomationSciencePack) == 10, f"Failed to insert science packs into Lab. Current count: {lab_inventory.get(Prototype.AutomationSciencePack)}"

    # Start researching (assuming a function to start research exists)
    #initial_research = game.get_research_progress(Technology.Automation)  # Get initial research progress
    ingredients1 = game.set_research(Technology.Automation)  # Start researching automation technology

    # Wait for some time to allow research to progress
    game.sleep(30)

    # Check if research has progressed
    ingredients2 = game.get_research_progress(Technology.Automation)
    assert ingredients1[0].count > ingredients2[0].count, f"Research did not progress. Initial: {ingredients1[0].count}, Current: {ingredients2[0].count}"

    # Save gamestate with research progress
    # Verify that there are no technologies here
    n_game_state = GameState.from_instance(game.instance)

    game.instance.reset(n_game_state)

    pass