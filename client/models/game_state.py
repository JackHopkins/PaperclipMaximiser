from typing import Tuple

import numpy as np
from pydantic import BaseModel, Field

from vocabulary import Vocabulary


class GameState(BaseModel):
    bounding_box: int = 100
    last_observed_player_location: Tuple[int, int] = (0,0)
    player_location: Tuple[int, int] = (0,0)
    collision_mask: np.ndarray = Field(default_factory=lambda: np.full((100, 100), 1, dtype=object))
    grid_world: np.ndarray = Field(default_factory=lambda: np.full((100, 100), 1, dtype=object))
    minimap_bounding_box: int = 100 * 4
    initial_score: int = 0
    vocabulary: Vocabulary = None

    @classmethod
    def with_default(cls, vocabulary, *args, **kwargs):
        default_collision_mask = np.full((100, 100), 1, dtype=object)
        default_grid_world = np.full((100, 100), 1, dtype=object)
        return cls(*args,
                   collision_mask=default_collision_mask,
                   grid_world=default_grid_world,
                   vocabulary=vocabulary,
                   **kwargs)

    class Config:
        arbitrary_types_allowed = True