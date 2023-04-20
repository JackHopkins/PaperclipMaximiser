from controllers._action import Action
from typing import Tuple

from factorio_instance import PLAYER


class PlaceEntityNextTo(Action):

    def __init__(self, connection, game_state):
        super().__init__(self, connection, game_state)

    def __call__(self, entity: str, reference_position: Tuple = (0,0), direction: int = 1, gap: int =0, relative=False):
        x, y = reference_position

        if relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self._send('place_entity_next_to', PLAYER, entity, x, y, direction, gap)
        if not isinstance(response, dict):
            raise Exception(f"Could not place {entity} at {reference_position}.", response)
        return response['x'], response['y']
