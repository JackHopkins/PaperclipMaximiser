import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")
import json
import os

from datasetgen.auto_curriculum.plan_sampler import PlanSampler
from datasetgen.mcts.conversation import Conversation, Message
from datasetgen.mcts.parallel_supervised_config import SupervisedExecutorConfig
from datasetgen.mcts.parallel_planning_v2_mcts import ParallelPlanningV2MCTS, TaskConfig
from datasetgen.mcts.planning_mcts import PlanningMCTS
from datasetgen.mcts.program import Program
from datasetgen.mcts.best_of_n_open_ended import BestOfNOpenExecutor
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
from results.supervised_results.tasks import TASKS
load_dotenv()
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def plot_throughput_timeseries_mean(input_data, file_path, task):
        throughput_entity = task.throughput_entity
        input_data = input_data["results"][0]
        data = {}
        for key, value in input_data.items():
            values = [x["holdout_achievements"]["dynamic"].get(f"{throughput_entity}", 0) for x in value]
            data[key] = values
        

        # Convert the data into a numpy array for easier calculation
        values = np.array(list(data.values()))

        # Calculate mean and standard deviation across series
        mean = np.mean(values, axis=0)
        std = np.std(values, axis=0)

        # Create time points (x-axis)
        time_points = np.arange(len(mean))

        # Create the plot
        plt.figure(figsize=(10, 6))

        # Plot individual series
        #for series_name, series_data in data.items():
        #    plt.plot(time_points, series_data, 'o-', alpha=0.3, label=series_name)

        # Plot mean
        plt.plot(time_points, mean, 'k-', linewidth=2, label='Mean')

        # Plot confidence bands (mean ± 2*std)
        plt.fill_between(time_points, 
                         mean - 2*std,
                         mean + 2*std,
                         color='gray',
                         alpha=0.2,
                         label='±2 STD')

        # Customize the plot
        plt.title(f'{throughput_entity} throughput ')
        plt.xlabel('Steps')
        plt.ylabel(f'{throughput_entity}/20s')
        plt.grid(True, alpha=0.3)

        # Set y-axis to start at 0
        plt.ylim(bottom=0)

        # Show the plot
        plt.tight_layout()
        plt.savefig(file_path)



def plot_throughput_timeseries(data, file_path, task):
        throughput_entity = task.throughput_entity
        data = data["results"][0]
        data_to_plot = {}
        for key, value in data.items():
            values = [x["holdout_achievements"]["dynamic"].get(throughput_entity, 0) for x in value]
            data_to_plot[key] = values

        # Create a figure and axis
        plt.figure(figsize=(10, 6))

        # Plot each series
        for series_name, values in data_to_plot.items():
            plt.plot(values, label=series_name, marker='o')

        # Customize the plot
        plt.title(f'{throughput_entity} throughput ')
        plt.xlabel('Steps')
        plt.ylabel(f'{throughput_entity}/20s')
        plt.legend()
        plt.grid(True)

        # save the plot to the file path
        plt.savefig(file_path)

def initiate_executor(config, instances, version, db_client, version_description, llm_factory):
    executor = config["executor"](
        instances=instances,
        version=version,
        db_client=db_client,
        version_description=version_description,
        llm_factory=llm_factory,
        config = config["config"]
    )
    return executor

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
    #model_to_evaluate = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    #model_to_evaluate = "Qwen/Qwen2.5-72B-Instruct-Turbo"
    #model_to_evaluate = "gpt-4o"
    result_path = r"src\results\supervised_results"
    task_types = ["open_ended"]
    tasks_to_exclude = []
    search_type = "open_ended"
    search_iterations = 1
    version = 330 # 120 and 121 was the last version before this change
    version_description = "eval_agentic_supervised"


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


    # random test of smthing stupid
    #sampler = KLDiversityAchievementSampler(db_client, temperature=0.5)
    #id = 81484
    #initial_program = await sampler.sample_specific_parent(id)
    #initial_state = initial_program.state
    # end of random test of smthing stupid
    # Initialize FactorioEvaluator with the list of instances

    print("Initializing supervised executor...")
    initial_state = GameState.from_instance(instances[0])
    configs = {"open_ended": {"config": SupervisedExecutorConfig(
        n_parallel=1,
        model_to_evaluate=model_to_evaluate,
        initial_state=initial_state,
        supervised_kwargs = {"prompt_path": r"src\prompts\supervised_task_prompts\open_ended\action_generator",
                             "max_steps_per_objective": 10,
                             "beam_unification_steps": 3}),
        "executor": BestOfNOpenExecutor}
        }
    
    # get the current date and time
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    
    save_path = os.path.join(result_path, search_type, model_to_evaluate, dt_string)
    # check if the path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    task_types = task_types if task_types else TASKS.keys()
    executor = initiate_executor(configs[search_type], instances, version, db_client, version_description, llm)
    
    for task_type in task_types:
        tasks_for_this_category = TASKS[task_type]
        config_dict = {"iterations": search_iterations,
                   "executor_kwargs": executor.config._to_dict()}
        # save the config dict
        with open(os.path.join(save_path, f"{task_type}_config.json"), "w") as f:
            json.dump(config_dict, f)
        for task_key, task in tasks_for_this_category.items():
            if task_key in tasks_to_exclude:
                continue
            print(f"Starting MCTS search for task {task.task}")
            results = await executor.search_supervised(
            n_iterations=search_iterations,
            skip_failures=False,
            task=task,
            run_id = f"{task_key}_{dt_string}"
            )
            print(f"Task: {task.task} has been completed")
            result_dict = {"results" :results,
                           "starting_inventory": task.starting_inventory,
                           "target_entity": task.throughput_entity,}
            with open(os.path.join(save_path, f"{task_key}.json"), "w") as f:
                json.dump(result_dict, f)
            plot_throughput_timeseries(result_dict, os.path.join(save_path, f"{task_key}_individual.png"), task)
            plot_throughput_timeseries_mean(result_dict, os.path.join(save_path, f"{task_key}_mean.png"), task)
    print("All tasks completed")
            

if __name__ == '__main__':
    # run asynchronously
    import asyncio
    asyncio.run(main())
