from datetime import datetime
from typing import Dict
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

from datasetgen.mcts.conversation import Conversation
from datasetgen.mcts.program import Program
from datasetgen.mcts.game_state import GameState


class LanguageOutput(BaseModel):
    id: Optional[int] = None
    response: str
    conversation: Conversation
    parent_id: Optional[int] = None
    state: Optional[GameState] = None
    meta: Optional[dict] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    prompt_token_usage: Optional[int] = None
    completion_token_usage: Optional[int] = None
    token_usage: Optional[int] = None
    version: int = 1
    version_description: str = ""

class TaskOutput(BaseModel):
    task: str
    language_output: Optional[LanguageOutput]

class InitialPlanOutput(BaseModel):
    initial_plan: str
    language_output: LanguageOutput

class Step(BaseModel):
    candidate_language_outputs: list[LanguageOutput] = []
    judge_step_str: str = ""
    chosen_step: str = ""
    judge_language_output_step: LanguageOutput = None
    sampled_programs: list[Program] = []
    program: Program = None
    start_state: GameState = None
    end_state: GameState = None
    reward: float = None
    meta: dict = {}


class PlanOutput(BaseModel):
    task: TaskOutput
    initial_plan: Optional[InitialPlanOutput]
    final_output: str = ""
    steps : list[Step] = []
    logs: Optional[list] = []
    success: bool = False
    meta: Optional[Dict] = {}