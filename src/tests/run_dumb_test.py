import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")
from factorio_instance import FactorioInstance
from factorio_entities import Position
from factorio_instance import Direction
from factorio_types import Prototype, Resource, ResourceName
import time


def get_recursive_ingredients(game, prototype):
    resources = ResourceName.get_list_of_names()
    recipe = game.get_prototype_recipe(prototype)
    ingredients = recipe.ingredients
    for ingredient in ingredients:
        name = ingredient.name
        if name not in resources:
            prototype_recursive = Prototype.from_string(name)
            ingredient.ingredients = get_recursive_ingredients(game, prototype_recursive)
    return ingredients

def get_missing_ingredients(game, prototype, inventory):
    resources = ResourceName.get_list_of_names()
    recipe = game.get_prototype_recipe(prototype)
    ingredients = recipe.ingredients
    for ing_idx, ingredient in enumerate(ingredients):
        name = ingredient.name
        prototype_recursive = Prototype.from_string(name)
        need_crafting = True
        if name in inventory:
            if ingredient.count > inventory[name]:
                ingredient.count -= inventory[name]
                inventory.pop(name)
            else:
                inventory[name] -= ingredient.count
                need_crafting = False
        if name not in resources and need_crafting:
                required_ingredients, inventory = get_missing_ingredients(game, prototype_recursive, inventory)
                if required_ingredients is not None:
                    ingredient.ingredients = required_ingredients
        else:
            ingredients[ing_idx] = None
    return ingredients, inventory

def check_for_missing_ingredients(ingredient, count, inventory):
    name = ingredient.name
    if name in inventory:
        if count > inventory[name]:
            count -= inventory[name]
            ingredient.count = count
            inventory.pop(name)
        else:
            inventory[name] -= count
            return None, inventory
    if ingredient.ingredients is not None:
        for sub_ingredient in ingredient.ingredients:
            sub_ingredient.count *= count
            sub_ingredient, inventory = check_for_missing_ingredients(sub_ingredient, sub_ingredient.count, inventory)
    return ingredient, inventory

def get_missing_ingredients_v2(game, prototype, inventory):
    full_recipe = get_recursive_ingredients(game, prototype)
    for ing_idx, ingredient in enumerate(full_recipe):
        missing_ingredients, inventory = check_for_missing_ingredients(ingredient, ingredient.count, inventory)
        full_recipe[ing_idx] = missing_ingredients
    return full_recipe

def test():
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                inventory={
                                    #'coal': 50,
                                    #'copper-plate': 50,
                                    #'iron-plate': 50,
                                    #'iron-chest': 2,
                                    #'burner-mining-drill': 3,
                                    #'electric-mining-drill': 1,
                                    #'assembling-machine-1': 1,
                                    #'stone-furnace': 9,
                                    #'transport-belt': 50,
                                    #'boiler': 1,
                                    #'burner-inserter': 32,
                                    #'pipe': 15,
                                    #'steam-engine': 1,
                                    #'small-electric-pole': 10
                            })
    #instance.initial_inventory = {'stone-furnace': 1,
    #                                  'iron-chest': 3,
    #                                  'burner-inserter': 6,
    #                                  'coal': 50,
    #                                  'transport-belt': 50,
    #                                  'burner-mining-drill': 3}
    #drill = instance.place_object()
    inventory = {'iron-plate': 4,
                 "stone": 5,
                 "stone-furnace": 2}
    instance.reset()
    #drill = instance.place_entity()
    num_drills = 3
    game  = instance
    orig_recipe = get_recursive_ingredients(game, Prototype.BurnerMiningDrill)
    missing_ingredients = get_missing_ingredients_v2(game, Prototype.BurnerMiningDrill, inventory)
    #recipe = game.get_prototype_recipe(Prototype.CopperPlate)
    # Start at the origin
    game.move_to(Position(x=0, y=0))
    
    # 1) mine 5 stone
    # Find nearest stone resource
    nearest_stone = game.nearest(Resource.Stone)
    # Move to the stone resource
    game.move_to(nearest_stone)
    # Harvest stone
    game.harvest_resource(nearest_stone, quantity=5) 
    
    #2) Craft stone furnace
    game.craft_item(Prototype.StoneFurnace, quantity=1)
    #3) Mine coal for stone furnace
    nearest_coal = game.nearest(Resource.Coal)
    game.move_to(nearest_coal)
    game.harvest_resource(nearest_coal, quantity=5)

    #4) Move to copper ore
    nearest_copper = game.nearest(Resource.CopperOre)
    game.move_to(nearest_copper)
    #5) Place down stone furnace
    stone_furnace = game.place_entity_next_to(Prototype.StoneFurnace,
                                                reference_position=nearest_copper,
                                                direction=game.UP,
                                                spacing=1)
    #6) Mine copper ore
    game.harvest_resource(nearest_copper, quantity=5)
    #7) Place coal and copper ore to stone furnace
    game.insert_item(Prototype.Coal, stone_furnace, 5)
    game.insert_item(Prototype.CopperOre, stone_furnace, 5)
    #8) Smelt copper ore for copper plates
    # wait for smelting
    game.sleep(20)
    game.extract_item(Prototype.CopperPlate, stone_furnace, 5)
    # Find the nearest coal patch
    #coal_patch = game.get_resource_patch(Resource.Coal, game.nearest(Resource.Coal))
    #
    ## Move to the center of the coal patch
    #game.move_to(coal_patch.bounding_box.left_top)
    
    # Place the first drill
    # getting '{ ["a"] = false,["b"] = attempt to call a nil value,}' at line 90 in _action.py
    
    
test()