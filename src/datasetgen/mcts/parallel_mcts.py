import time
from dataclasses import dataclass
from typing import List, Tuple
import asyncio
from math import floor

from datasetgen.mcts.chunked_mcts import ChunkedMCTS
from datasetgen.mcts.factorio_evaluator import FactorioEvaluator
from datasetgen.mcts.grouped_logger import GroupedFactorioLogger
from datasetgen.mcts.mcts import MCTS
from datasetgen.mcts.mcts_debugger import MCTSDebugger
from factorio_instance import FactorioInstance


@dataclass
class InstanceGroup:
    """Represents a group of Factorio instances for parallel MCTS"""
    group_id: int
    active_instances: List[FactorioInstance]
    holdout_instance: FactorioInstance
    evaluator: FactorioEvaluator
    mcts: MCTS


class ParallelMCTS:
    def __init__(self,
                 instances: List[FactorioInstance],
                 n_parallel: int,
                 db_client: 'DBClient',
                 llm_factory: 'LLMFactory',
                 system_prompt: str,
                 initial_state: 'GameState',
                 mcts_class=ChunkedMCTS,
                 **mcts_kwargs):

        self.debugger = MCTSDebugger()

        self.n_parallel = n_parallel
        instances_per_group = floor(len(instances) / n_parallel)

        # Create shared logger for all groups
        self.logger = GroupedFactorioLogger(
            n_groups=n_parallel,
            instances_per_group=instances_per_group
        )
        self.logger.start()

        self.instance_groups = self._create_instance_groups(
            instances, n_parallel, db_client, llm_factory,
            system_prompt, initial_state, mcts_class, **mcts_kwargs
        )

    def _create_instance_groups(self,
                                instances: List[FactorioInstance],
                                n_parallel: int,
                                db_client: 'DBClient',
                                llm_factory: 'LLMFactory',
                                system_prompt: str,
                                initial_state: 'GameState',
                                mcts_class: type,
                                **mcts_kwargs) -> List[InstanceGroup]:

        if len(instances) < n_parallel * 2:
            raise ValueError(
                f"Need at least {n_parallel * 2} instances for {n_parallel} parallel searches "
                f"(got {len(instances)})")

        total_instances = len(instances)
        instances_per_group = floor(total_instances / n_parallel)

        if instances_per_group < 2:
            raise ValueError(
                f"Not enough instances to allocate at least one active and one holdout "
                f"instance per group (need {n_parallel * 2}, got {total_instances})")

        groups = []
        current_idx = 0

        for group_id in range(n_parallel):
            group_instances = instances[current_idx:current_idx + instances_per_group]
            active_instances = group_instances[:-1]
            holdout_instance = group_instances[-1]

            # Create evaluator with shared logger
            evaluator = FactorioEvaluator(
                db_client=db_client,
                instances=group_instances,
                value_accrual_time=3,
                logger=self.logger  # Pass the shared logger
            )

            # Create MCTS instance
            mcts = mcts_class(
                llm_factory=llm_factory,
                db_client=db_client,
                evaluator=evaluator,
                system_prompt=system_prompt,
                initial_state=initial_state,
                **mcts_kwargs
            )

            groups.append(InstanceGroup(
                group_id=group_id,
                active_instances=active_instances,
                holdout_instance=holdout_instance,
                evaluator=evaluator,
                mcts=mcts
            ))

            current_idx += instances_per_group

        return groups


    async def search(self, n_iterations: int, skip_failures: bool = False):
        """Run parallel MCTS searches across all groups"""

        # Create progress task if not exists
        # if not self.logger.progress_task:
        #     total_steps = n_iterations * len(self.instance_groups)
        #     self.logger.progress_task = self.logger.progress.add_task(
        #         "Running MCTS iterations...",
        #         total=total_steps
        #     )

        async def run_group_search(group: InstanceGroup):
            """Run iterations for a single group"""
            try:
                group_id = group.group_id
                timing_data = {}

               # self.debugger.console.print(f"[bold blue]Initializing search for Group {group_id}[/bold blue]")

                for iteration in range(n_iterations):
                    iteration_start = time.time()

                    # # Debug header for iteration
                    # self.debugger.console.print(
                    #     f"\n[yellow]Group {group_id} - Iteration {iteration + 1}/{n_iterations}[/yellow]"
                    # )

                    await group.mcts.run_iteration(
                        len(group.active_instances),
                        skip_failures
                    )
                    self.logger.update_progress()
            except Exception as e:
                print(f"Error in group {group.group_id}: {str(e)}")
                raise e

        # Create tasks for concurrent execution
        search_tasks = [
            run_group_search(group)
            for group in self.instance_groups
        ]

        # Run all groups concurrently and wait for completion
        await asyncio.gather(*search_tasks)

    def cleanup(self):
        """Clean up resources for all instance groups"""
        self.logger.stop()
        for group in self.instance_groups:
            if hasattr(group.evaluator, 'logger'):
                group.evaluator.logger.stop()