from controllers._action import Action
from typing import Tuple

from factorio_instance import PLAYER


class SetEntityRecipe(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self, position: Tuple[int, int], recipe: str, relative=False) -> bool:
        x, y = position

        if not relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER, recipe, x, y)

        if response != 1:
            raise Exception(f"Could not set recipe to {recipe}", response)
        return True
