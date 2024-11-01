from time import sleep
from typing import List

import pytest

from factorio_entities import Entity, Position, ResourcePatch, Recipe, BurnerMiningDrill
from factorio_instance import Direction, FactorioInstance
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.initial_inventory = {'stone-furnace': 1, 'boiler': 1, 'steam-engine': 1, 'offshore-pump': 1, 'pipe': 100, 'iron-plate': 50, 'copper-plate': 20, 'coal': 50}
    #instance.rcon_client.send_command('game.reset_game_state()')
    #instance.rcon_client.send_command('game.reload_script()')
    instance.reset()
    yield instance

def test_create_offshore_pump_to_steam_engine(game):
    """
    Place a boiler and a steam engine next to each other in 3 cardinal directions.
    :param game:
    :return:
    """
    boilers_in_inventory = game.inspect_inventory()[Prototype.Boiler]
    steam_engines_in_inventory = game.inspect_inventory()[Prototype.SteamEngine]
    pipes_in_inventory = game.inspect_inventory()[Prototype.Pipe]

    DIR = Direction.UP
    # move to the nearest water source
    water_location = game.nearest(Resource.Water)
    game.move_to(water_location)

    offshore_pump = game.place_entity(Prototype.OffshorePump,
                                      position=water_location,
                                      direction=DIR)
    assert offshore_pump.direction.value == DIR.value
    # Get offshore pump direction
    direction = offshore_pump.direction

    # pump connection point
    pump_connection_point = offshore_pump.connection_points[0]

    # place the boiler next to the offshore pump
    boiler = game.place_entity_next_to(Prototype.Boiler,
                                       reference_position=offshore_pump.position,
                                       direction=direction,
                                       spacing=2)
    assert boiler.direction.value == direction.value

    # rotate the boiler to face the offshore pump
    boiler = game.rotate_entity(boiler, Direction.next_clockwise(direction))

    # insert coal into the boiler
    game.insert_item(Prototype.Coal, boiler, quantity=5)

    # connect the boiler and offshore pump with a pipe
    offshore_pump_to_boiler_pipes = game.connect_entities(offshore_pump, boiler, connection_type=Prototype.Pipe)

    game.move_to(Position(x=0, y=10))
    steam_engine: Entity = game.place_entity_next_to(Prototype.SteamEngine,
                                                     reference_position=boiler.position,
                                                     direction=DIR,
                                                     spacing=2)

    # connect the boiler and steam engine with a pipe
    boiler_to_steam_engine_pipes = game.connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)

    inspected_steam_engine = game.inspect_entities(position=steam_engine.position, radius=1).get_entity(Prototype.SteamEngine)
    assert inspected_steam_engine.warning == 'not connected to power network'

    assert steam_engine.direction.value == DIR.value


def test_build_iron_gear_factory(game):
    """
    Build a factory that produces iron gears from iron plates.
    :param game:
    :return:
    """
    # move to the iron ore
    iron_ore_patch = game.get_resource_patch(Resource.IronOre, game.nearest(Resource.IronOre))
    game.move_to(iron_ore_patch.bounding_box.left_top + Position(x=1, y=1))

    # harvest 80 iron ore
    while game.inspect_inventory()[Prototype.IronOre] < 80:
        game.harvest_resource(iron_ore_patch.bounding_box.left_top, quantity=10)

    # move to the stone patch
    stone_patch = game.get_resource_patch(Resource.Stone, game.nearest(Resource.Stone))

    # harvest 10 stone
    game.move_to(stone_patch.bounding_box.left_top + Position(x=1, y=1))
    game.harvest_resource(stone_patch.bounding_box.left_top, quantity=10)

    # move to the coal patch
    coal_patch: ResourcePatch = game.get_resource_patch(Resource.Coal, game.nearest(Resource.Coal))
    game.move_to(coal_patch.bounding_box.left_top + Position(x=1, y=1))

    # harvest 30 coal
    while game.inspect_inventory()[Prototype.Coal] < 30:
        game.harvest_resource(coal_patch.bounding_box.left_top, quantity=10)

    # move to the copper patch
    copper_patch: ResourcePatch = game.get_resource_patch(Resource.CopperOre, game.nearest(Resource.CopperOre))
    game.move_to(copper_patch.bounding_box.left_top + Position(x=1, y=1))

    # harvest 10 copper ore
    while game.inspect_inventory()[Prototype.CopperOre] < 30:
        game.harvest_resource(copper_patch.bounding_box.left_top, quantity=10)

    # move to the origin
    game.move_to(Position(x=0, y=0))

    # place a stone furnace
    stone_furnace = game.place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))

    # insert 20 coal into the stone furnace
    game.insert_item(Prototype.Coal, stone_furnace, quantity=20)

    # insert 80 iron ore into the stone furnace
    game.insert_item(Prototype.IronOre, stone_furnace, quantity=50)

    # check if the stone furnace has produced iron plates
    while game.inspect_inventory(stone_furnace)[Prototype.IronPlate] < 50:
        sleep(1)

    # extract the iron plates from the stone furnace
    game.extract_item(Prototype.IronPlate, stone_furnace, quantity=50)

    # insert 80 iron ore into the stone furnace
    game.insert_item(Prototype.IronOre, stone_furnace, quantity=30)

    # check if the stone furnace has produced iron plates
    while game.inspect_inventory(stone_furnace)[Prototype.IronPlate] < 30:
        sleep(1)

    # extract the iron plates from the stone furnace
    game.extract_item(Prototype.IronPlate, stone_furnace, quantity=30)

    # insert 20 copper ore into the stone furnace
    game.insert_item(Prototype.CopperOre, stone_furnace, quantity=20)

    # check if the stone furnace has produced copper plates
    while game.inspect_inventory(stone_furnace)[Prototype.CopperPlate] < 20:
        sleep(5)

    # extract the copper plates from the stone furnace
    game.extract_item(Prototype.CopperPlate, stone_furnace, quantity=20)

    # pick up the stone furnace
    game.pickup_entity(stone_furnace)

    # get recipe for burner mining drill
    recipe: Recipe = game.get_prototype_recipe(Prototype.BurnerMiningDrill)

    # craft any ingredient that is missing
    for ingredient in recipe.ingredients:
        if game.inspect_inventory()[ingredient.name] < ingredient.count:
            game.craft_item(ingredient.name, quantity=ingredient.count)

    # craft a burner mining drill
    game.craft_item(Prototype.BurnerMiningDrill)

    # move to the iron ore patch
    game.move_to(iron_ore_patch.bounding_box.left_top + Position(x=1, y=1))

    # place a burner mining drill
    burner_mining_drill: BurnerMiningDrill = game.place_entity(Prototype.BurnerMiningDrill,
                                                               position=iron_ore_patch.bounding_box.left_top)

    # fuel the burner mining drill
    game.insert_item(Prototype.Coal, burner_mining_drill, quantity=5)

    # place the stone furnace
    stone_furnace = game.place_entity_next_to(Prototype.StoneFurnace,
                                              reference_position=burner_mining_drill.drop_position,
                                              direction=Direction.UP,
                                              spacing=0)

    # place a burner inserter
    burner_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                reference_position=stone_furnace.position,
                                                direction=Direction.UP,
                                                spacing=0)

    def ensure_ingredients(game, recipe, quantity=1):
        for ingredient in recipe.ingredients:
            required = ingredient.count * quantity
            available = game.inspect_inventory()[ingredient.name]
            if available < required:
                craft_recursive(game, ingredient.name, required - available)

    def craft_recursive(game, item_name, quantity):
        recipe = game.get_prototype_recipe(item_name)
        ensure_ingredients(game, recipe, quantity)
        game.craft_item(item_name, quantity=quantity)

    recipe = game.get_prototype_recipe(Prototype.AssemblingMachine1)
    ensure_ingredients(game, recipe)

    # craft an assembly machine
    game.craft_item(Prototype.AssemblingMachine1)

    # place the assembly machine
    assembly_machine = game.place_entity_next_to(Prototype.AssemblingMachine1,
                                                 reference_position=burner_inserter.position,
                                                 direction=Direction.UP,
                                                 spacing=0)
    # set the recipe for the assembly machine to produce iron gears
    game.set_entity_recipe(assembly_machine, Prototype.IronGearWheel)

    # craft an offshore pump
    recipe = game.get_prototype_recipe(Prototype.OffshorePump)
    ensure_ingredients(game, recipe)
    game.craft_item(Prototype.OffshorePump)

    # place the offshore pump at nearest water source
    game.move_to(game.nearest(Resource.Water))
    offshore_pump = game.place_entity(Prototype.OffshorePump,
                                      position=game.nearest(Resource.Water),
                                      direction=Direction.LEFT)

    # craft a boiler
    recipe = game.get_prototype_recipe(Prototype.Boiler)
    ensure_ingredients(game, recipe)
    game.craft_item(Prototype.Boiler)

    # place the boiler next to the offshore pump
    boiler = game.place_entity_next_to(Prototype.Boiler,
                                       reference_position=offshore_pump.position,
                                       direction=Direction.LEFT,
                                       spacing=2)


    # craft a steam engine
    recipe = game.get_prototype_recipe(Prototype.SteamEngine)
    ensure_ingredients(game, recipe)
    game.craft_item(Prototype.SteamEngine)

    # place the steam engine next to the boiler
    steam_engine = game.place_entity_next_to(Prototype.SteamEngine,
                                             reference_position=boiler.position,
                                             direction=Direction.LEFT,
                                             spacing=2)

    # connect the steam engine and assembly machine with power poles

    # harvest nearby trees for wood
    tree_patch = game.get_resource_patch(Resource.Wood, game.nearest(Resource.Wood))
    game.move_to(tree_patch.bounding_box.left_top + Position(x=1, y=1))
    game.harvest_resource(tree_patch.bounding_box.left_top, quantity=40)

    # craft 5 small electric poles
    recipe = game.get_prototype_recipe(Prototype.SmallElectricPole)
    ensure_ingredients(game, recipe, quantity=10)
    game.craft_item(Prototype.SmallElectricPole, quantity=10)

    # place connect the steam engine and assembly machine with power poles
    game.connect_entities(steam_engine, assembly_machine, connection_type=Prototype.SmallElectricPole)

    # place connective pipes between the boiler and steam engine
    game.connect_entities(boiler, steam_engine, connection_type=Prototype.Pipe)

    # place connective pipes between the boiler and offshore pump
    game.connect_entities(boiler, offshore_pump, connection_type=Prototype.Pipe)

    game.move_to(boiler.position)
    game.insert_item(Prototype.Coal, boiler, quantity=10)
    game.insert_item(Prototype.Coal, burner_inserter, quantity=10)
    game.insert_item(Prototype.Coal, stone_furnace, quantity=10)

    game.move_to(burner_mining_drill.position)
    game.insert_item(Prototype.Coal, burner_mining_drill, quantity=10)

    game.sleep(15)

    # extract the iron gears from the assembly machine
    game.extract_item(Prototype.IronGearWheel, assembly_machine, quantity=5)

    inventory = game.inspect_inventory(entity=assembly_machine)

    assert inventory.get(Prototype.IronGearWheel) >= 0