from typing import Any, Dict, Type

from search.model.game_state import GameState
from search.mcts.mcts import MCTS
from search.mcts.samplers.db_sampler import DBSampler


class ParallelMCTSConfig:
    """Configuration for ParallelMCTS"""
    def __init__(self,
                 n_parallel: int,
                 system_prompt: str,
                 initial_state: GameState,
                 mcts_class: Type[MCTS],
                 sampler: DBSampler,
                 mcts_kwargs: Dict[str, Any] = None,
                 **kwargs):
        self.n_parallel = n_parallel
        self.system_prompt = system_prompt
        self.initial_state = initial_state
        self.mcts_class = mcts_class
        self.sampler = sampler
        self.mcts_kwargs = mcts_kwargs or {}

        for key, value in kwargs.items():
            setattr(self, key, value)
