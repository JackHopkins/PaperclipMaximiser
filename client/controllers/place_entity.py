from controllers._action import Action
from typing import Optional, Tuple

from factorio_instance import PLAYER

class PlaceEntity(Action):

    def __init__(self, connection, game_state):
        super().__init__(self, connection, game_state)

    def __call__(self, entity: str, direction=0, position: Tuple[int, int] = (0, 0), relative=False) -> Optional[Tuple]:
        x, y = position

        if direction > 3 or direction < 0:
            raise Exception("Directions are between 0-3")

        if relative:
            x -= self.game_state.last_observed_player_location[0]
            y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self._send('place',
                                       PLAYER,
                                       entity.replace("_", "-"),
                                       direction + 1,
                                       x,
                                       y
                                       )
        if not isinstance(response, dict):
            raise Exception(f"Could not place {entity}", response.replace("___", ", ").replace("_", " "))

        return (response['x'], response['y'])
