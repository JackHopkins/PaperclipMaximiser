import ast
import asyncio
import json
from dataclasses import dataclass
from typing import List, Tuple, Optional

from datasetgen.mcts.conversation import Conversation, Message
from datasetgen.mcts.conversation_formatter import PLANNING_ADDITION_PROMPT
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.mcts import MCTS
from datasetgen.mcts.program import Program


class ChunkedMCTS(MCTS):
    def _split_into_chunks(self, program_code: str) -> List[Program]:
        chunks = []
        current_docstring = ""
        current_code = []
        module = ast.parse(program_code)

        for node in module.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if current_code and current_docstring:
                    chunks.append(Program(
                        code=f'"""{current_docstring}"""\n'+"\n".join(current_code),
                        conversation=Conversation(messages=[]) # We need this to conform to the Program class structure
                    ))
                    current_code = []
                current_docstring = node.value.s
            else:
                # Get the source lines for this node
                start = node.lineno
                end = node.end_lineno if hasattr(node, 'end_lineno') else start
                code_lines = program_code.splitlines()[start - 1:end]
                current_code.extend(code_lines)

        if current_code and current_docstring:
            chunks.append(Program(
                code=f'"""{current_docstring}"""\n'+"\n".join(current_code),
                conversation=Conversation(messages=[]) # We need this to conform to the Program class structure
            ))
        return chunks

    async def _evaluate_chunks(self, chunks: List[Program], start_state: GameState, instance_id: int) -> Tuple[
        List[Program], float]:
        current_state = start_state
        holdout_start = GameState.from_instance(self.evaluator.holdout)
        self.evaluator.holdout.reset(holdout_start)
        holdout_future = asyncio.create_task(self.evaluator._run_holdout())
        entity_list = []
        try:
            for chunk in chunks:
                instance = self.evaluator.instances[instance_id]
                instance.reset(current_state)
                self.evaluator.logger.update_instance(instance_id, status="executing")

                reward, state, response, entities = await self.evaluator._evaluate_single(
                    instance_id,
                    chunk,
                    instance
                )
                entity_list.append(entities)
                chunk.state = state
                chunk.value = reward
                chunk.response = response

                current_state = state
        except Exception as e:
            print(f"Error during evaluation: {e}")
            raise e  # Propagate the exception to handle it elsewhere if needed.

        holdout_value = await holdout_future
        return chunks, holdout_value, entity_list

    async def search(self, n_iterations: int, samples_per_iteration: int, skip_failures: bool = False):
        for iteration in range(n_iterations):
            parent = await self.db.sample_parent(version=self.version)
            start_state = parent.state if parent else self.initial_state
            conversation = parent.conversation if parent else Conversation(messages=[
                Message(role="system", content=self.system_prompt),
                Message(role="user",
                        content=f"Inventory: {json.dumps(start_state.inventory.__dict__)}\n\n{PLANNING_ADDITION_PROMPT}")
            ])

            self.evaluator.set_sampling_status()
            raw_programs = await self._generate_programs_batch(conversation, samples_per_iteration)

            for i, (program, chunks) in enumerate(raw_programs):
                instance_id = i % (len(self.evaluator.instances) - 1)

                try:
                    evaluated_chunks, holdout, entity_list = await self._evaluate_chunks(chunks, start_state, instance_id)
                    last_chunk_id = parent.id if parent else None
                    last_conversation_stage = program.conversation
                    for chunk, entities in zip(evaluated_chunks, entity_list):
                        chunk_program = Program(
                            code=chunk.code,
                            conversation=program.conversation,
                            value=chunk.value - (holdout / len(evaluated_chunks)),  # Distribute holdout value
                            state=chunk.state,
                            response=chunk.response,
                            version=self.version,
                            version_description=self.version_description,
                            parent_id=last_chunk_id,
                            token_usage=program.token_usage // len(evaluated_chunks),
                            completion_token_usage=program.completion_token_usage // len(evaluated_chunks),
                            prompt_token_usage=program.prompt_token_usage // len(evaluated_chunks)
                        )
                        last_conversation_stage.add_result(chunk.code, chunk.value - (holdout / len(evaluated_chunks)), chunk.response, chunk.state, entities)
                        chunk_program.id = hash((chunk.code, json.dumps(chunk_program.conversation.model_dump()['messages'])))
                        chunk_program.conversation = last_conversation_stage

                        last_chunk_id = chunk_program.id
                        if not skip_failures or chunk_program.value is not None:
                            await self.db.create_program(chunk_program)

                except Exception as e:
                    print(f"Failed to evaluate program: {str(e)}")
                    continue

                self.evaluator.logger.update_progress()

    async def _generate_programs_batch(self, conversation: Conversation, n_samples: int) -> List[Tuple[Program, List[Program]]]:
        programs = await super()._generate_programs_batch(conversation, n_samples)
        chunked_programs = []

        for i, program in enumerate(programs):
            try:
                chunks = self._split_into_chunks(program.code)
                if not chunks:
                    continue

                chunked_programs.append((program, chunks))

            except Exception as e:
                print(f"Failed to process chunks for program: {str(e)}")
                continue

        return chunked_programs