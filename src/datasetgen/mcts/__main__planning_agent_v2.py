import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")
import json
import os

from datasetgen.auto_curriculum.plan_sampler import PlanSampler
from datasetgen.mcts.conversation import Conversation, Message
from datasetgen.mcts.parallel_mcts_config import ParallelMCTSConfig
from datasetgen.mcts.parallel_planning_v2_mcts import ParallelPlanningV2MCTS, TaskConfig
from datasetgen.mcts.planning_mcts import PlanningMCTS
from datasetgen.mcts.program import Program
from datasetgen.mcts.samplers.kld_achievement_sampler import KLDiversityAchievementSampler

os.environ["FORCE_COLOR"] = "1"
os.environ["TERM"] = "xterm-256color"

import concurrent
import os
from typing import Tuple, List

from dotenv import load_dotenv
from rich import print
from cluster.local.cluster_ips import get_local_container_ips
from datasetgen.mcts.conversation_formatter import PLANNING_ADDITION_PROMPT
from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.game_state import GameState
from factorio_instance import FactorioInstance
from llm_factory import LLMFactory

load_dotenv()



def create_instance(params: Tuple[str, int, int]) -> FactorioInstance:
    """Create a single Factorio instance with the given parameters"""
    ip, udp_port, tcp_port = params
    return FactorioInstance(
        address=ip,
        tcp_port=tcp_port,
        bounding_box=200,
        fast=True,
        cache_scripts=False,
        inventory={}
    )


def create_factorio_instances() -> List[FactorioInstance]:
    """Create Factorio instances in parallel from local servers"""
    def init_instance(params: Tuple[str, int, int]) -> FactorioInstance:
        ip, udp_port, tcp_port = params
        return FactorioInstance(
            address=ip,
            tcp_port=tcp_port,
            bounding_box=200,
            fast=True,
            cache_scripts=False,
            inventory={}
        )

    ips, udp_ports, tcp_ports = get_local_container_ips()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(init_instance, zip(ips, udp_ports, tcp_ports)))


async def main():
    model_to_evaluate = "claude-3-5-sonnet-20241022"
    #model_to_evaluate = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
    step_executor_prompt_path = r"src\prompts\agentic_eval_prompts\planning_v2\step_program_supervised"
    step_generator_prompt_path = r"src\prompts\agentic_eval_prompts\planning_v2\step_generator"
    step_judge_prompt_path = r"src\prompts\agentic_eval_prompts\planning_v2\step_judge"
    beam_judge = r"src\prompts\agentic_eval_prompts\planning_v2\path_judge"
    version = 301 # 120 and 121 was the last version before this change
    version_description = "eval_agentic_v3_demo"


    # Initialize components
    llm = LLMFactory(model_to_evaluate)
    db_client = DBClient(host=os.getenv("SKILLS_DB_HOST"),
                         port=os.getenv("SKILLS_DB_PORT"),
                         dbname=os.getenv("SKILLS_DB_NAME"),
                         user=os.getenv("SKILLS_DB_USER"),
                         password=os.getenv("SKILLS_DB_PASSWORD"))

    instances = create_factorio_instances()
    for instance in instances:
        instance.speed(10) # Set the game speed to 10x normal speed for faster testing

    # Initialize FactorioEvaluator with the list of instances

    initial_state = GameState.from_instance(instances[0])

    print("Initializing MCTS...")
    # Sampler
    sampler = KLDiversityAchievementSampler(db_client, temperature=0.5)

    config = ParallelMCTSConfig(
        n_parallel=1,
        mcts_class=PlanningMCTS,
        sampler=sampler,
        system_prompt="",
        initial_state=initial_state,
        max_steps_per_objective=25,
        programs_sampled_per_step = 3,
        number_of_steps_for_judge=3,
        beam_unification_steps = 5,
        mcts_kwargs={
            "model_to_evaluate":model_to_evaluate,
            "step_executor_prompt_path":step_executor_prompt_path,
            "step_generator_prompt_path":step_generator_prompt_path,
            "step_judge_prompt_path":step_judge_prompt_path,
            "initial_state": initial_state,
            "beam_unification_prompt_path": beam_judge
        }
    )
    general_task = "create an automatic coal mine into a chest placed 10 spaces away from the drill"
    general_task = "create an automatic coal mine consisting of 3 burner mining drills"
    #general_task = "Mine 5 iron ore"
    task = TaskConfig(
        task_str=general_task,
        check_for_completion=True,
        check_dicts=[{"task_type": "craft", "item":"iron-ore", "quantity": 5}]
    )
    #general_task = "Craft 2 burner mining drills"
    mcts = ParallelPlanningV2MCTS(instances,
                db_client,
                llm,
                config,
                version=version,
                version_description=version_description)

    print("Starting MCTS search...")
    best_programs = await mcts.search(
        n_iterations=3,
        skip_failures=False,
        task=task
    )
            

if __name__ == '__main__':
    # run asynchronously
    import asyncio
    asyncio.run(main())
