import asyncio
from typing import List, Tuple, Union

from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.logger import FactorioLogger
from datasetgen.mcts.program import Program
from factorio_entities import Entity, EntityGroup
from factorio_instance import FactorioInstance


class FactorioEvaluator:
    def __init__(self, db_client: DBClient, instances: List[FactorioInstance], value_accrual_time=10, logger=None):
        self.db = db_client
        self.instances = instances[:-1]  # Main instances
        self.holdout = instances[-1]  # Holdout instance
        self.value_accrual_time = value_accrual_time  # Time to accrue value before evaluating
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
        self.instance_to_port[len(self.instances)] = self.holdout.tcp_port  # Add holdout mapping


        if logger:
            self.port_to_group = logger.port_to_group
            # Find the group ID for the holdout instance
            self.holdout_group_id = self.port_to_group[self.holdout.tcp_port]

    def set_sampling_status(self):
        """Update status for all instances in this evaluator's group"""
        if self.logger:
            for instance in self.instances:
                self.logger.update_instance(instance.tcp_port, status="sampling")
            # Also update holdout status
            self.logger.update_instance(self.holdout.tcp_port, status="sampling")

    async def evaluate_batch(self, programs: List[Program], start_state: GameState) -> List[Program]:
        try:
            # Reset holdout and start its baseline run
            self.holdout.reset(start_state)
            if self.logger:
                self.logger.update_instance(self.holdout.tcp_port, status="running", program_id=None)
            holdout_future = asyncio.create_task(self._run_holdout())

            # Evaluate programs in parallel
            eval_futures = []
            for i, (prog, inst) in enumerate(zip(programs, self.instances)):
                inst.reset(start_state)
                if self.logger:
                    self.logger.update_instance(inst.tcp_port, program_id=prog.id, status="resetting")
                eval_futures.append(self._evaluate_single(inst.tcp_port, prog, inst))

            # Wait for all evaluations and holdout
            eval_results = await asyncio.gather(*eval_futures)
            holdout_value = await holdout_future

            # Update metrics for this group's holdout
            if self.logger:
                self.logger.update_instance(
                    self.holdout.tcp_port,
                    status="completed",
                    current_reward=holdout_value
                )

            # Update program results
            for i, (program, (raw_reward, state, response, entities)) in enumerate(zip(programs, eval_results)):
                relative_reward = raw_reward - holdout_value

                if self.logger:
                    self.logger.update_instance(
                        self.instances[i].tcp_port,
                        status="completed",
                        raw_reward=raw_reward,
                        holdout_value=holdout_value,
                        relative_reward=relative_reward,
                        total_programs=self.logger.groups[
                                           self.port_to_group[self.instances[i].tcp_port]
                                       ].instances[self.instances[i].tcp_port].total_programs + 1
                    )

                program.value = relative_reward
                program.state = state
                program.raw_reward = raw_reward
                program.holdout_value = holdout_value
                program.conversation.add_result(program.code, relative_reward, response, state, entities)
                program.response = response

            return programs

        except Exception as e:
            if self.logger:
                for instance in self.instances + [self.holdout]:
                    self.logger.update_instance(
                        instance.tcp_port,
                        status="error",
                        error_count=self.logger.groups[
                                        self.port_to_group[instance.tcp_port]
                                    ].instances[instance.tcp_port].error_count + 1
                    )
            raise e

    async def _evaluate_single(self, instance_id: int, program: Program, instance: FactorioInstance) -> Tuple[
        float, GameState, str, List[Union[Entity, EntityGroup]]]:
        try:
            # Convert instance_id to TCP port
            tcp_port = self.instance_to_port[instance_id]

            start_entities = instance.get_entities()
            start_inventory = instance.inspect_inventory()
            self.logger.update_instance(tcp_port, status="starting value")
            initial_value, _ = instance.score()

            self.logger.update_instance(tcp_port, status="executing")
            reward, _, result = instance.eval(program.code, timeout=60)

            self.logger.update_instance(tcp_port, status="capturing state")
            state = GameState.from_instance(instance)
            entities = instance.get_entities()
            final_inventory = instance.inspect_inventory()

            # Check to see if the inventories are different
            # If so, we put a hint in the code and result
            if start_inventory.__dict__ != final_inventory.__dict__ and 'error' not in result.lower():
                program.code += '\nprint(f"Inventory changed to {inspect_inventory()}")'
                result += f'\n'+str(len(program.code.split('\n')))+f': (\'Inventory changed to {final_inventory}\',)'

            # Check to see if the entities are different
            # If so, we put a hint in the code and result
            if start_entities != entities and 'error' not in result.lower():
                program.code += '\nprint(f"Entities on the map: {get_entities()}")\n'
                result += "\n"+str(len(program.code.split('\n')))+f': (\'Entities on the map: {entities}\',)'

            self.logger.update_instance(tcp_port, status="accruing value")
            await asyncio.sleep(self.value_accrual_time)

            score, _ = instance.score()
            final_reward = score - initial_value

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

            if "error" in result.lower() and self.logger:
                group_id = self.port_to_group[tcp_port]
                group = self.logger.groups[group_id]
                instance_metrics = group.instances[tcp_port]
                self.logger.update_instance(
                    tcp_port,
                    status="error",
                    error_count=instance_metrics.error_count + 1
                )

            return final_reward, state, result, entities

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

    async def _run_holdout(self) -> float:
        """Run holdout instance for same duration as programs"""
        try:
            initial_entities = self.holdout.get_entities()
            start_inventory = self.holdout.inspect_inventory()

            initial_value, _ = self.holdout.score()
            if self.logger:
                self.logger.update_instance(self.holdout.tcp_port, status="accruing value")
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

            return reward - initial_value
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

    def __del__(self):
        """Clean up logger on deletion"""
        self.logger.stop()