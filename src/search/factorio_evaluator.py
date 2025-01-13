import asyncio
import pickle
from typing import List, Tuple, Union, Dict

from search.db_client import DBClient
from search.model.game_state import GameState
from search.mcts.logger import FactorioLogger
from search.model.program import Program
from factorio_entities import Entity, EntityGroup
from factorio_instance import FactorioInstance
from utils import get_achievements, get_profits
import copy

class FactorioEvaluator:
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
    def __init__(self, db_client: DBClient, instances: List[FactorioInstance], value_accrual_time=10, logger=None, include_holdout = True):
        self.db = db_client
        self.include_holdout = include_holdout
        if self.include_holdout:
            self.instances = instances[:-1]  # Main instances
            self.holdout = instances[-1]  # Holdout instance
        else:
            self.instances = instances
            self.holdout = None

=======
    def __init__(self,
                 db_client: DBClient,
                 instances: List[FactorioInstance],
                 value_accrual_time=10,
                 error_penalty=10,
                 logger=None):
        self.db = db_client
        self.instances = instances  # Main instances
        #self.holdout = instances[-1]  # Holdout instance
>>>>>>> feature/advantage:src/search/factorio_evaluator.py
        self.value_accrual_time = value_accrual_time  # Time to accrue value before evaluating
        self.error_penalty = error_penalty  # Penalty for errors during evaluation


        # Initialize logger if not provided
        if not logger:
            self.logger = FactorioLogger(len(instances))
            self.logger.start()
        else:
            self.logger = logger

        # Create instance ID to TCP port mapping
        self.instance_to_port = {
            i: instance.tcp_port
            for i, instance in enumerate(self.instances)
        }
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
        if self.holdout:
            self.instance_to_port[len(self.instances)] = self.holdout.tcp_port  # Add holdout mapping
=======
        #self.instance_to_port[len(self.instances)] = self.holdout.tcp_port  # Add holdout mapping
>>>>>>> feature/advantage:src/search/factorio_evaluator.py


        if logger:
            self.port_to_group = logger.port_to_group
            # Find the group ID for the holdout instance
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
            self.holdout_group_id = self.port_to_group[self.holdout.tcp_port] if self.holdout else None
=======
            #self.holdout_group_id = self.port_to_group[self.holdout.tcp_port]
>>>>>>> feature/advantage:src/search/factorio_evaluator.py

    def set_status(self, status):
        for instance in self.instances:
            self.logger.update_instance(instance.tcp_port, status=status)

    def set_sampling_status(self):
        """Update status for all instances in this evaluator's group"""
        if self.logger:
            for instance in self.instances:
                self.logger.update_instance(instance.tcp_port, status="sampling")
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
            if self.holdout:
                # Also update holdout status
                self.logger.update_instance(self.holdout.tcp_port, status="sampling")

    async def evaluate_batch(self, programs: List[Program], start_state: GameState) -> List[Program]:
        try:
            if self.holdout:
                # Reset holdout and start its baseline run
                self.holdout.reset(start_state)
                if self.logger:
                    self.logger.update_instance(self.holdout.tcp_port, status="running", program_id=None)
                holdout_future = asyncio.create_task(self._run_holdout())
=======
            # Also update holdout status
            #self.logger.update_instance(self.holdout.tcp_port, status="sampling")

    def set_iteration(self, iteration, n_iterations):
        """Update iteration number for all instances in this evaluator's group"""
        if self.logger:
            for instance in self.instances:
                self.logger.update_instance(instance.tcp_port, iteration=iteration, n_iterations=n_iterations)
            # Also update holdout status
            # self.logger.update_instance(self.holdout.tcp_port, iteration=iteration, n_iterations=n_iterations)

    async def evaluate_batch(self, programs: List[Program], start_state: GameState) -> List[Program]:
        try:
            # Reset holdout and start its baseline run
            #self.holdout.reset(start_state)
            #if self.logger:
            #    self.logger.update_instance(self.holdout.tcp_port, status="running", program_id=None)
            #holdout_future = asyncio.create_task(self._run_holdout())
>>>>>>> feature/advantage:src/search/factorio_evaluator.py

            # Evaluate programs in parallel
            eval_futures = []
            for i, (prog, inst) in enumerate(zip(programs, self.instances)):
                inst.reset(start_state)
                if self.logger:
                    self.logger.update_instance(inst.tcp_port, program_id=prog.id, status="resetting")
                eval_futures.append(self._evaluate_single(inst.tcp_port, prog, inst))

            # Wait for all evaluations and holdout
            eval_results = await asyncio.gather(*eval_futures)
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
            if self.holdout:
                holdout_value = await holdout_future

            # Update metrics for this group's holdout
            if self.logger and self.holdout:
                self.logger.update_instance(
                    self.holdout.tcp_port,
                    status="completed",
                    current_reward=holdout_value
                )

            # Update program results
            for i, (program, (raw_reward, state, response, entities, achievements)) in enumerate(zip(programs, eval_results)):
                relative_reward = raw_reward - holdout_value if self.holdout else raw_reward
=======
            #holdout_value = await holdout_future

            # Update metrics for this group's holdout
            # if self.logger:
            #     self.logger.update_instance(
            #         self.holdout.tcp_port,
            #         status="completed",
            #         current_reward=holdout_value
            #     )

            # Update program results
            for i, (program, (raw_reward, state, response, entities, achievements)) in enumerate(zip(programs, eval_results)):
                relative_reward = raw_reward# - holdout_value
>>>>>>> feature/advantage:src/search/factorio_evaluator.py

                if self.logger:
                    self.logger.update_instance(
                        self.instances[i].tcp_port,
                        status="completed",
                        raw_reward=raw_reward,
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
                        holdout_value=holdout_value if self.holdout else -1,
=======
                        holdout_value=raw_reward,
>>>>>>> feature/advantage:src/search/factorio_evaluator.py
                        relative_reward=relative_reward,
                        total_programs=self.logger.groups[
                                           self.port_to_group[self.instances[i].tcp_port]
                                       ].instances[self.instances[i].tcp_port].total_programs + 1
                    )

                program.value = relative_reward
                program.state = state
                program.raw_reward = raw_reward
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
                program.holdout_value = holdout_value if self.holdout else -1
                program.conversation.add_result(program.code, response, score=raw_reward, advantage=relative_reward)
=======
                #program.holdout_value = holdout_value
                program.conversation.add_result(program.code, response, score=raw_reward, advantage=relative_reward, objectives=program.meta['objectives'] if 'objectives' in program.meta else [])
>>>>>>> feature/advantage:src/search/factorio_evaluator.py
                program.response = response
                program.achievements = achievements

            return programs

        except Exception as e:
            if self.logger:
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
                instances = self.instances + [self.holdout] if self.holdout else self.instances
                for instance in instances:
=======
                for instance in self.instances:
>>>>>>> feature/advantage:src/search/factorio_evaluator.py
                    self.logger.update_instance(
                        instance.tcp_port,
                        status="error",
                        error_count=self.logger.groups[
                                        self.port_to_group[instance.tcp_port]
                                    ].instances[instance.tcp_port].error_count + 1
                    )
            raise e

    def _evaluate_for_achievements(self, code: str, instance: FactorioInstance) \
            -> Tuple[float, GameState, str, List[Union[Entity, EntityGroup]], Dict[str, Dict[str, int]]]:
        # Get initial state information
        start_production_flows = instance.get_production_stats()
        # Executing code
        reward, time, result = instance.eval(code, timeout=120)
        post_production_flows = instance.get_production_stats()
        achievements = get_achievements(start_production_flows, copy.deepcopy(post_production_flows))
        
        return result, achievements, post_production_flows


    async def _evaluate_single(self, instance_id: int, program: Program, instance: FactorioInstance) \
            -> Tuple[float, GameState, str, List[Union[Entity, EntityGroup]], Dict[str, Dict[str, int]]]:
        try:
            # Convert instance_id to TCP port
            tcp_port = self.instance_to_port[instance_id]
        except:
            tcp_port = instance_id

        try:
            # Get initial state information
            self.logger.update_instance(tcp_port, status="starting value")
            start_entities = instance.get_entities()
            start_inventory = instance.inspect_inventory()
            start_production_flows = instance.get_production_stats()
            initial_value, start_time = instance.score()
            code = program.code
            # Executing code
            self.logger.update_instance(tcp_port, status="executing")
            reward, time, result = instance.eval(program.code, timeout=600)

            # Capturing immediate resulting state
            self.logger.update_instance(tcp_port, status="capturing state")
            state = GameState.from_instance(instance)

            # Get the namespace variables in a human readable format for debugging purposes
            vars = pickle.loads(state.namespace)

            entities = instance.get_entities()
            final_inventory = instance.inspect_inventory()

            # Check to see if the inventories are different
            # If so, we put a hint in the code and result
<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
            #get_inventory_code = 'print(f"Inventory changed to {inspect_inventory()}")'
            #if start_inventory.__dict__ != final_inventory.__dict__ and 'error' not in result.lower() and get_inventory_code not in program.code:
            #    program.code += f'\n{get_inventory_code}'
            #    result += f'\n'+str(len(program.code.split('\n')))+f': (\'Inventory changed to {final_inventory}\',)'

            # Check to see if the entities are different
            # If so, we put a hint in the code and result
            #get_entities_code = 'print(f"Entities on the map: {get_entities()}")'
            #if start_entities != entities and 'error' not in result.lower() and get_entities_code not in program.code:
            #    program.code += f'\n{get_entities_code}\n'
            #    result += "\n"+str(len(program.code.split('\n')))+f': (\'Entities on the map: {entities}\',)'
=======
            get_inventory_code = 'print(f"Inventory changed to {inspect_inventory()}")'
            if (start_inventory.__dict__ != final_inventory.__dict__
                    and 'error' not in result.lower()
                    and get_inventory_code not in program.code
                    and 'inspect_inventory()' not in program.code):
                program.code += f'\n{get_inventory_code}'
                result += f'\n'+str(len(program.code.split('\n')))+f': (\'Inventory changed to {final_inventory}\',)'

            # Check to see if the entities are different
            # If so, we put a hint in the code and result
            get_entities_code = 'print(f"Entities on the map: {get_entities()}")'
            if (start_entities != entities and 'error' not in result.lower()
                    and get_entities_code not in program.code
                    and 'get_entities()' not in program.code):
                program.code += f'\n{get_entities_code}\n'
                result += "\n"+str(len(program.code.split('\n')))+f': (\'Entities on the map: {entities}\',)'
>>>>>>> feature/advantage:src/search/factorio_evaluator.py

            self.logger.update_instance(tcp_port, status=f"accruing value ({self.value_accrual_time}s)")
            await asyncio.sleep(self.value_accrual_time)

            score, _ = instance.score()
            final_reward = score - initial_value

            post_production_flows = instance.get_production_stats()
            achievements = get_achievements(start_production_flows, post_production_flows)
            profits = get_profits(start_production_flows, post_production_flows)

            group_id = self.port_to_group[tcp_port]
            group = self.logger.groups[group_id]
            instance_metrics = group.instances[tcp_port]

            self.logger.update_instance(
                tcp_port,
                status="accrued value",
                current_reward=final_reward,
                raw_reward=final_reward,
                final_entities=len(entities),
                start_entities=len(start_entities),
                total_programs=instance_metrics.total_programs + 1,
                start_inventory_count=sum([v for k, v in start_inventory.__dict__.items() if v > 0]),
                final_inventory_count=sum([v for k, v in final_inventory.__dict__.items() if v > 0])
            )

            error = False
            if "error" in result.lower() and self.logger:
                group_id = self.port_to_group[tcp_port]
                group = self.logger.groups[group_id]
                instance_metrics = group.instances[tcp_port]
                self.logger.update_instance(
                    tcp_port,
                    status="error",
                    error_count=instance_metrics.error_count + 1
                )
                error = True

            return final_reward, state, result, entities, achievements, profits, error

        except Exception as e:
            print(f"Error in _evaluate_single:")
            print(f"Instance ID: {instance_id}")
            print(f"TCP Port: {self.instance_to_port.get(instance_id, 'Unknown')}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

            if self.logger:
                tcp_port = self.instance_to_port[instance_id]
                group_id = self.port_to_group[tcp_port]
                group = self.logger.groups[group_id]
                instance_metrics = group.instances[tcp_port]
                self.logger.update_instance(
                    tcp_port,
                    status="error",
                    error_count=instance_metrics.error_count + 1
                )
            raise e

<<<<<<< HEAD:src/datasetgen/mcts/factorio_evaluator.py
    async def _run_holdout(self) -> float:
        """Run holdout instance for same duration as programs"""
        try:
            initial_production_flows = self.holdout.get_production_stats()
            initial_entities = self.holdout.get_entities()
            start_inventory = self.holdout.inspect_inventory()

            initial_value, _ = self.holdout.score()
            if self.logger:
                self.logger.update_instance(self.holdout.tcp_port, status=f"accruing value ({self.value_accrual_time}s)")
            await asyncio.sleep(self.value_accrual_time)
            entities = self.holdout.get_entities()
            reward, _ = self.holdout.score()
            final_inventory = self.holdout.inspect_inventory()

            if self.logger:
                # Get the metrics for this holdout instance from the correct group
                group = self.logger.groups[self.holdout_group_id]
                holdout_metrics = group.instances[self.holdout.tcp_port]

                self.logger.update_instance(
                    self.holdout.tcp_port,
                    status="accrued value",
                    final_entities=len(entities),
                    start_entities=len(initial_entities),
                    total_programs=holdout_metrics.total_programs + 1,
                    start_inventory_count=sum([v for k, v in start_inventory.__dict__.items() if v > 0]),
                    final_inventory_count=sum([v for k, v in final_inventory.__dict__.items() if v > 0])
                )
            
            end_production_flows = self.holdout.get_production_stats()
            profits = get_profits(initial_production_flows, end_production_flows)
            return reward - initial_value, profits
        except Exception as e:
            if self.logger:
                # Update error count using the grouped structure
                group = self.logger.groups[self.holdout_group_id]
                holdout_metrics = group.instances[self.holdout.tcp_port]
                self.logger.update_instance(
                    self.holdout.tcp_port,
                    status="error",
                    error_count=holdout_metrics.error_count + 1
                )
            raise e
=======
    # async def _run_holdout(self) -> float:
    #     """Run holdout instance for same duration as programs"""
    #     try:
    #         initial_entities = self.holdout.get_entities()
    #         start_inventory = self.holdout.inspect_inventory()
    #
    #         initial_value, _ = self.holdout.score()
    #         if self.logger:
    #             self.logger.update_instance(self.holdout.tcp_port, status=f"accruing value ({self.value_accrual_time}s)")
    #         await asyncio.sleep(self.value_accrual_time)
    #         entities = self.holdout.get_entities()
    #         reward, _ = self.holdout.score()
    #         final_inventory = self.holdout.inspect_inventory()
    #
    #         if self.logger:
    #             # Get the metrics for this holdout instance from the correct group
    #             group = self.logger.groups[self.holdout_group_id]
    #             holdout_metrics = group.instances[self.holdout.tcp_port]
    #
    #             self.logger.update_instance(
    #                 self.holdout.tcp_port,
    #                 status="accrued value",
    #                 final_entities=len(entities),
    #                 start_entities=len(initial_entities),
    #                 total_programs=holdout_metrics.total_programs + 1,
    #                 start_inventory_count=sum([v for k, v in start_inventory.__dict__.items() if v > 0]),
    #                 final_inventory_count=sum([v for k, v in final_inventory.__dict__.items() if v > 0])
    #             )
    #
    #         return reward - initial_value
    #     except Exception as e:
    #         if self.logger:
    #             # Update error count using the grouped structure
    #             group = self.logger.groups[self.holdout_group_id]
    #             holdout_metrics = group.instances[self.holdout.tcp_port]
    #             self.logger.update_instance(
    #                 self.holdout.tcp_port,
    #                 status="error",
    #                 error_count=holdout_metrics.error_count + 1
    #             )
    #         raise e
>>>>>>> feature/advantage:src/search/factorio_evaluator.py

    def __del__(self):
        """Clean up logger on deletion"""
        self.logger.stop()