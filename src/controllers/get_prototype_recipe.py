from controllers.__action import Action
from typing import Tuple, OrderedDict, Union

from factorio_entities import Recipe, Entity, Inventory, Ingredient
from factorio_instance import PLAYER
from factorio_types import Prototype, ResourceName
from utilities.parse_lua_dict import parse_lua_dict


class GetPrototypeRecipe(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)

    def __call__(self, prototype: Union[Prototype, str]) -> Recipe:
        """
        Get the recipe of the given entity prototype.
        :param prototype: Prototype to get recipe from
        :return: Recipe of the given prototype
        """

        if isinstance(prototype, Prototype):
            name, _ = prototype.value
        else:
            name = prototype

        response, elapsed = self.execute(PLAYER, name)

        if not isinstance(response, dict):
            raise Exception(f"Could not get recipe of {name}", response)

        parsed_response = parse_lua_dict(response)
        
        def _get_prototype_from_name(name: str) -> Prototype:
            for prototype in Prototype:
                if prototype.value[0] == name:
                    return prototype

        ingredients = [Ingredient(name=ingredient['name'], count=ingredient['amount'], type=ingredient['type'] if 'type' in ingredient else None) for ingredient in parsed_response['ingredients']]
        ingredient_queue = [ing for ing in ingredients if ing.type == 'item']
        final_recipe = Recipe(name=name, ingredients=ingredients, sub_recipes=[])
        processed_ingredients = [name]
        while ingredient_queue:
            ingredient_to_process = ingredient_queue.pop(0)
            ingredient_name = ingredient_to_process.name
            if ingredient_name in processed_ingredients:
                continue
            processed_ingredients.append(ingredient_name)
            response, elapsed = self.execute(PLAYER, ingredient_name)
            if not isinstance(response, dict):
                raise Exception(f"Could not get recipe of {ingredient_name}", response)
            parsed_response = parse_lua_dict(response)
            ingredients = [Ingredient(name=ingredient['name'], count=ingredient['amount'], type=ingredient['type'] if 'type' in ingredient else None) for ingredient in parsed_response['ingredients']]
            ingredient_queue += [ing for ing in ingredients if ing.type == 'item' and ing.name not in processed_ingredients]
            final_recipe.sub_recipes.append(Recipe(name=ingredient_name, ingredients=ingredients))

        return final_recipe
