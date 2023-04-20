from controllers._action import Action
from typing import Tuple

from factorio_instance import PLAYER


class SetEntityRecipe(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, position: Tuple[int, int], recipe: str, relative=False) -> bool:
        x, y = position

        if not relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self._send('recipe', PLAYER, recipe, x, y)

        if response != 1:
            raise Exception(f"Could not set recipe to {recipe}", response)
        return True
