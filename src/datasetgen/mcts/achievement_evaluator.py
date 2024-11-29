import asyncio
import json
from typing import Optional, List, Dict
import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")
import psycopg2
import tenacity
from tenacity import wait_exponential, retry, retry_if_exception_type

from datasetgen.mcts.conversation import Conversation, Message
from datasetgen.mcts.conversation_formatter import ConversationFormatter, DefaultFormatter, PLANNING_ADDITION_PROMPT
from datasetgen.mcts.db_client import DBClient
from datasetgen.mcts.factorio_evaluator import FactorioEvaluator
from datasetgen.mcts.game_state import GameState
from datasetgen.mcts.program import Program
from factorio_instance import FactorioInstance
from utils import eval_program_with_achievements
class AchievementEvaluator:
    def __init__(self,
                 instances: List[FactorioInstance],
                 ):

        self.instances = instances
        self.achievements = []
        

    def _extract_code_from_choice(self, choice) -> Optional[str]:
        """Extract code from a single completion choice"""
        code = ""
        try:
            content = choice.message.content
            code = self._verify_response_is_python(content)
            return code
        except Exception as e:
            try:
                content = choice.message.content
                code = content.split('```python')[1].split('```')[0].strip()
                code = self._verify_response_is_python(code)
                return code
            except Exception as e1:
                # Sometimes it samples a leading line, before writing unblocked python code.
                content = "\n".join(choice.message.content.split("\n")[1:])
                try:
                    code = self._verify_response_is_python(content)
                    return code
                except Exception as e2:
                    try:
                        code = content.split('from factorio_instance import *')[1].strip()
                        code = self._verify_response_is_python(code)
                        return code
                    except Exception as e2:
                        #print(f"Failed to extract code from choice after removing leading line and factorio_instance import: {str(e2)} \n\n`{content}`")
                        chain_of_thoughts = '"""\n'+content.strip().strip("\"")+'\n"""'
                        return chain_of_thoughts
                    #print(f"Failed to extract code from choice after removing leading line: {str(e2)}")
                print(f"Failed to extract code from choice: {str(e1)}")

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_programs_batch(self, conversation: Conversation, n_samples: int, logit_bias: Optional[Dict[str, float]] = None) -> List[Program]:
        """Generate multiple programs in a single API call using 'n' parameter"""
        formatted_messages = self.formatter.to_llm_messages(
            self.formatter.format_conversation(conversation)
        )
        if "claude" in self.llm.model:
            assert n_samples == 1, "Number of samples must be 1 for Claude"

        try:
            # Single API call to generate n_samples completions
            response = await self.llm.acall(
                messages=formatted_messages,
                max_tokens=2048,
                n=n_samples,
                temperature=1,
                logit_bias=logit_bias,
                presency_penalty=0.7
            )

            programs = []
            messages = conversation.model_dump()['messages']

            # Process all choices from the response
            if "claude" in self.llm.model:

                # Handle Claude response format
                code = self._extract_code_from_choice(response)
                if code:
                    programs.append(Program(
                        id=hash((code, json.dumps(messages))),
                        code=code,
                        conversation=conversation,
                        token_usage=response.usage.total_tokens if hasattr(response, 'usage') else None,
                        completion_token_usage=response.usage.completion_tokens if hasattr(response, 'usage') else None,
                        prompt_token_usage=response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                        version=self.version,
                        version_description=self.version_description
                    ))
            else:
                # Handle OpenAI response format with multiple choices
                for choice in response.choices:
                    code = self._extract_code_from_choice(choice)
                    if code:
                        programs.append(Program(
                            id=hash((code, json.dumps(messages))),
                            code=code,
                            conversation=conversation,
                            token_usage=response.usage.total_tokens // n_samples if hasattr(response,
                                                                                            'usage') else None,
                            completion_token_usage=response.usage.completion_tokens // n_samples if hasattr(response,
                                                                                                            'usage') else None,
                            prompt_token_usage=response.usage.prompt_tokens // n_samples if hasattr(response,
                                                                                                    'usage') else None,
                            version=self.version,
                            version_description=self.version_description
                        ))

            return programs

        except Exception as e:
            print(f"Batch program generation failed: {str(e)}")
            return []

    async def search(self,
                     n_iterations: int,
                     samples_per_iteration: int,
                     skip_failures: bool = False):
        """
        Search for the best program using Monte Carlo Tree Search (MCTS).
        :param n_iterations: Number of iterations to perform.
        :param samples_per_iteration: Number of programs to sample per iteration.
        :param skip_failures: Whether to skip saving failed program generations.
        """

        for iteration in range(n_iterations):
            print(f"Starting iteration {iteration}")
            await self.run_iteration(samples_per_iteration, skip_failures)
            self.evaluator.logger.update_progress()

    @tenacity.retry(
        retry=retry_if_exception_type(psycopg2.Error),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=tenacity.stop_after_attempt(3)
    )
    async def run_iteration(self, samples_per_iteration, skip_failures):
        """Run a single MCTS iteration with retries for concurrent operations"""
        try:
            parent = await self.db.sample_parent(version=self.version)
            if parent:
                start_state = parent.state
                conversation = parent.conversation
            else:
                start_state = self.initial_state
                conversation = Conversation(messages=[
                    Message(role="system", content=self.system_prompt),
                    Message(role="user",
                            content=f"Inventory: {json.dumps(start_state.inventory.__dict__)}\n\n{PLANNING_ADDITION_PROMPT}")
                ])

            self.evaluator.set_sampling_status()
            
            programs = await self._generate_programs_batch(conversation, samples_per_iteration)

            if not programs:
                return

            programs = [p for p in programs if p is not None]
            for program in programs:
                program.parent_id = parent.id if parent else None

            evaluated_programs = await self.evaluator.evaluate_batch(programs, start_state)

            # Use a connection pool or new connections for parallel saves
            save_tasks = []
            for program in evaluated_programs:
                if program.state is not None:
                    if not skip_failures or program.value is not None:
                        save_tasks.append(self.db.create_program(program))

            if save_tasks:
                await asyncio.gather(*save_tasks)

        except Exception as e:
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                print(f"Max retries ({self.max_retries}) reached. Error: {str(e)}")
                self.retry_count = 0
                raise e
            raise e


def get_new_crafted_entities(starting_stats, ending_stats):
    previous_crafts = starting_stats['output'].keys()
    new_crafts = ending_stats['output'].keys()
    new_crafts = [craft for craft in new_crafts if craft not in previous_crafts]
    return new_crafts

if __name__ == "__main__":
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory={})

    test_string = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.IronOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.IronOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(5)\nextract_item(Prototype.IronPlate, furnace.position, 10)"
    output_list, result, error, achievements = eval_program_with_achievements(instance, test_string)
    print(achievements)
    test_string = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.CopperOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.CopperOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(5)"
    output_list, result, error, achievements = eval_program_with_achievements(instance, test_string)
    print(achievements)
    test_string = "pos = nearest(Resource.Stone)\nmove_to(pos)\nharvest_resource(pos, 10)\ncraft_item(Prototype.StoneFurnace, 1)\npos = nearest(Resource.Coal)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = nearest(Resource.CopperOre)\nmove_to(pos)\nharvest_resource(pos, 10)\npos = Position(x = 0, y = 0)\nmove_to(pos)\nfurnace = place_entity(Prototype.StoneFurnace, position = pos)\ninsert_item(Prototype.CopperOre, furnace, 5)\ninsert_item(Prototype.Coal, furnace, 5)\nsleep(5)"
    output_list, result, error, achievements = eval_program_with_achievements(instance, test_string)
    print(achievements)
    