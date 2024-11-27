import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")


import json
import os
import statistics

from datasetgen.auto_curriculum.plan_sampler import PlanSampler
from datasetgen.mcts.chunked_mcts import ChunkedMCTS
from datasetgen.mcts.planning_mcts import PlanningMCTS
from datasetgen.mcts.conversation import Conversation, Message
from datasetgen.mcts.program import Program

os.environ["FORCE_COLOR"] = "1"
os.environ["TERM"] = "xterm-256color"

import concurrent
import os
from typing import Tuple, List

from dotenv import load_dotenv
from rich import print
from rich.console import Console
from cluster.local.cluster_ips import get_local_container_ips
from datasetgen.mcts.conversation_formatter import StructurePreservingFormatter, PLANNING_ADDITION_PROMPT
from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.factorio_evaluator import FactorioEvaluator
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.mcts import MCTS
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



def create_parallel_instances(nr_of_instances) -> List[FactorioInstance]:
    """Create Factorio instances in parallel using ThreadPoolExecutor from local servers"""
    ips, udp_ports, tcp_ports = get_local_container_ips()
    params = list(zip(ips, udp_ports, tcp_ports))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        instances = list(executor.map(create_instance, params))

    return instances[:nr_of_instances]


async def get_seed_programs(
        mcts: PlanningMCTS,
        plan_sampler: 'PlanSampler',
        n_seeds: int = 100,
) -> List[Program]:
    existing_rewards = await mcts.db.get_all_program_rewards(version=mcts.version)
    # filter out rewards < 0
    existing_rewards = list(filter(lambda x: x >= 0, existing_rewards))
    default_reward = (max(existing_rewards)-min(existing_rewards))/2 if existing_rewards else 10.0
    seeded_programs: List[Program] = []
    instance = mcts.evaluator.instances[0]

    # Get all available scenarios
    scenarios = [f for f in os.listdir(plan_sampler.starting_scenarios_folder)
                 if os.path.isdir(os.path.join(plan_sampler.starting_scenarios_folder, f))]

    seeds_per_scenario = n_seeds // len(scenarios)
    remaining_seeds = n_seeds % len(scenarios)

    for scenario in scenarios:
        num_samples = seeds_per_scenario + (1 if remaining_seeds > 0 else 0)
        remaining_seeds -= 1

        for _ in range(num_samples):
            game_state = plan_sampler.get_game_state(instance, scenario)
            if not game_state:
                continue

            objective, response = plan_sampler(instance, game_state)

            if len(objective) < 100:
                continue



            conversation = Conversation(messages=[
                Message(role="system", content=mcts.system_prompt),
                Message(role="user",
                        content=f"Inventory: {json.dumps(game_state.inventory.__dict__)}\n\n{PLANNING_ADDITION_PROMPT}"),
                Message(role="assistant", content=objective)
            ])
            try:
                messages = conversation.model_dump()['messages']
            except:
                messages = conversation.dict()['messages']
            if not objective.strip().startswith('"""'):
                objective = '"""\n'+objective

            program = Program(
                id=hash((objective, json.dumps(messages))),
                code=objective,
                conversation=conversation,
                value=default_reward,
                state=game_state,
                version=mcts.version,
                version_description=mcts.version_description,
                token_usage=response.usage.total_tokens if hasattr(response, 'usage') else None,
                completion_token_usage=response.usage.completion_tokens if hasattr(response, 'usage') else None,
                prompt_token_usage=response.usage.prompt_tokens if hasattr(response, 'usage') else None,
            )
            seeded_programs.append(program)

    return seeded_programs

async def main():
    step_executor_model_path = "ft:gpt-4o-2024-08-06:paperplane-ai:fact-instruct-1:ATSVGf4d:ckpt-step-214"
    planner_model = "claude-3-5-sonnet-20241022"
    objective_model = "ft:gpt-4o-2024-08-06:paperplane-ai:fact-self-gen-planning:AQzcPI91"
    step_executor_prompt_path = r"src\prompts\bottoms_up_prompts\finetuning_prompts\step_supervised"
    step_generator_prompt_path = r"src\prompts\bottoms_up_prompts\finetuning_prompts\step_generator"
    executor_plan_prompt_path = r"src\prompts\bottoms_up_prompts\finetuning_prompts\executor_plan"
    step_judge_prompt_path = r"src\prompts\bottoms_up_prompts\finetuning_prompts\step_judge"
    starting_scenario_folder = r"src\skills\data_scenarios\starting_scenarios"
    objective_model_prompt_path = r"src\prompts\bottoms_up_prompts\finetuning_prompts\system_message_policy_self_gen.md"
    nr_of_seeded_programs = 4
    version = 101
    version = 8
    parent_version = 4
    version_description = "Seeded / No planning prompt in user messages / Step-wise evaluation / Errors not saved"

    # Initialize components
    llm = LLMFactory(step_executor_model_path)
    db_client = DBClient(host=os.getenv("SKILLS_DB_HOST"),
                         port=os.getenv("SKILLS_DB_PORT"),
                         dbname=os.getenv("SKILLS_DB_NAME"),
                         user=os.getenv("SKILLS_DB_USER"),
                         password=os.getenv("SKILLS_DB_PASSWORD"))

    instances = create_parallel_instances(2)

    for instance in instances:
        instance.speed(10) # Set the game speed to 10x normal speed for faster testing

    # Initialize FactorioEvaluator with the list of instances
    evaluator = FactorioEvaluator(db_client, instances, value_accrual_time=3)
    initial_state = GameState.from_instance(instances[0])

    # load from prompts/bottoms_up_prompts/system_message_policy_self_gen into string
    with open(objective_model_prompt_path, "r") as f:
        system_prompt = f.read().format(schema=instances[0].get_system_prompt())

    print("Initializing MCTS...")

    mcts = PlanningMCTS(llm,
                db_client,
                evaluator,
                system_prompt, # Not used
                initial_state,
                version=version,
                version_description=version_description,
                planning_model = planner_model,
                executor_model = step_executor_model_path, 
                objective_model = objective_model, 
                step_executor_prompt_path = step_executor_prompt_path, 
                step_generator_prompt_path = step_generator_prompt_path, 
                step_judge_prompt_path = step_judge_prompt_path, 
                example_plan_prompt_path = executor_plan_prompt_path, 
                )

    sampler = PlanSampler(objective_model, objective_model_prompt_path, starting_scenario_folder)

    #print("Sampling seed scenarios...")
    #seeded_programs = await get_seed_programs(mcts, sampler, n_seeds=nr_of_seeded_programs)
    #for program in seeded_programs:
    #    await db_client.create_program(program)

    print("Starting MCTS search...")
    best_programs = await mcts.search(
        n_iterations=500,
        samples_per_iteration=len(instances)-1, # One for each instance, minus a holdout.
        skip_failures=False,
    )

    print("\nBest programs found:")
    for i, prog in enumerate(best_programs, 1):
        print(f"\nProgram {i} (reward: {prog.value:.2f}):")
        print(f"```python\n{prog.code}\n```")
        print("\nConversation history:")
        for msg in prog.conversation.messages:
            print(f"\n{msg['role'].upper()}:")
            print(msg['content'])
            

if __name__ == '__main__':
    # run asynchronously
    import asyncio
    asyncio.run(main())
