import os
import json
import hashlib
import re
from typing import List, Dict, Optional, Tuple

from llm_factory import LLMFactory
from search.mcts.formatters.conversation_formatter import ConversationFormatter
from search.model.conversation import Message, Conversation

DEFAULT_INSTRUCTIONS = \
    """
You are a report generating model for the game factorio. You are given a number of steps and logs an agent has executed in the game. You are also given the previous historical report. Using the previous historical report and the latest step execution logs you must generate a new report. The report must have 2 sections: EXISTING STRUCTURES and ERROR TIPS. Below are instructions for both of them

EXISTING STRUCTURES
In this section you must summarise what stucutres the agent has created on the map and what are the use-cases of those structures. You must also bring out the entities and positions of entities of each of those structures.

Focus on the structures themselves. Do not bring out entities separately, create sections like 
###Electricity generator at position(x)
Consists of steam engine(position x), boiler(position y) and offshore pump (position z)

###Copper plate mine at position(x)
Consists of following entities
-  Burner mining drill (position x1) and a furnace at position(y1)
-  Burner mining drill (position x2) and a furnace at position(y2)
-  Burner mining drill (position x3) and a furnace at position(y3)

###Copper cable factory
Consists of following entities
-  Burner mining drill (position x1) and a furnace at position(y1)
-  Assembling machine at position(z1) and inserter at position(a) that puts into assembling machine
-  Beltgroup (position ) that connects the furnace at position y1 to assembling machine at position(z1)

- If multiple sections are connected, summarise them as one structure
- Do not include any mention of harvesting or crafting activities. That is not the aim of this report and is self-evident as the agent can see its own inventory
- All structures from the previous report that did not have any updates, include them in the new report unchanged

ERROR TIPS
In this section you must analyse the errors that the agent has made and bring out tips how to mitigate these errors. 
Usually error messages tell you what the agent did wrong. The errors can be incorrect use of API, misplaced objects etc. 
Make this a succinct detailed list, group common similar error patterns and solutions how to avoid these errors. 
Group similar mistakes, if the agent made the same mistake multiple times but at many places, bring it out as one section/bulletpoint. 
Include new mistakes and all mistake tips from the previous report

Make the sections accurate and thorough. Do not mention things like "The error message suggests" etc, this is self evident.
Some examples

### Errors when using extracting but being too far
 -  Make sure to move to the target entity where you want to extract from before extracting items
### Errors when placing into a tile which is occupied by another entity
- Ensure you can place a entity to a tile before attempting placing
    """


class RecursiveReportFormatter(ConversationFormatter):
    """
    Formatter that maintains a fixed context window through hierarchical summarization.
    Recursively summarizes from left to right, incorporating newer messages into the summary.
    """

    def __init__(self,
                 chunk_size: int = 16,
                 llm_factory: Optional[LLMFactory] = None,
                 cache_dir: str = ".conversation_cache",
                 truncate_entity_data: bool = True,
                 summarize_history: bool = True):
        """

        @param chunk_size:
        @param llm_factory:
        @param cache_dir:
        @param summary_instructions:
        @param truncate_entity_data: Whether we should truncate historical (stale) entity observations when summarizing.
        """
        self.chunk_size = chunk_size
        self.llm_factory = llm_factory
        self.cache_dir = cache_dir
        self.summary_instructions = DEFAULT_INSTRUCTIONS
        self.truncate_entity_data = truncate_entity_data
        self.entity_data_pattern = re.compile(r': \[((.|[\n])+)]",\)')
        self.summarize_history = summarize_history
        self.historical_report = ""
        self.last_summary_step = 0
        # Ensure cache directory exists.
        os.makedirs(cache_dir, exist_ok=True)

    def _get_chunk_hash(self, messages: List[Message]) -> str:
        """Generate a deterministic hash for a chunk of messages."""
        chunk_content = json.dumps([{
            'role': msg.role,
            'content': msg.content,
            'metadata': msg.metadata
        } for msg in messages], sort_keys=True)
        return hashlib.sha256(chunk_content.encode()).hexdigest()

    def _get_cache_path(self, chunk_hash: str) -> str:
        """Get the file path for a cached summary."""
        return os.path.join(self.cache_dir, f"{chunk_hash}.json")

    def _load_cached_summary(self, chunk_hash: str) -> Optional[Message]:
        """Load a cached summary if it exists."""
        cache_path = self._get_cache_path(chunk_hash)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                return Message(
                    role="assistant",
                    content=data['content'],
                    metadata={"summarized": True, "summary_range": data['summary_range']}
                )
            except Exception as e:
                print(f"Error loading cached summary: {e}")
                return None
        return None

    def _save_summary_cache(self, chunk_hash: str, summary: Message):
        """Save a generated summary to the cache."""
        cache_path = self._get_cache_path(chunk_hash)
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'content': summary.content,
                    'summary_range': summary.metadata['summary_range']
                }, f)
        except Exception as e:
            print(f"Error saving summary cache: {e}")

    def _truncate_entity_data(self, message: Message, is_recent: bool = False, message_index = 0) -> Message:
        """
        Truncate entity data in message content if enabled and message is not recent.
        Returns a new Message instance with modified content if truncation occurred.
        """
        if not self.truncate_entity_data or is_recent or message.role in ('assistant', 'system'):
            return message

        if isinstance(message.content, str):
            new_content = self.entity_data_pattern.sub(': <STALE_ENTITY_DATA_OMITTED/>', message.content)
            if new_content != message.content:
                new_content = f"Step {message_index} execution log\n{new_content}"
                return Message(
                    role=message.role,
                    content=new_content,
                    metadata=message.metadata
                )

        return message

    async def _generate_summary(self, messages: List[Message], start_idx: int, end_idx: int) -> Message:
        """Generate a summary of messages using the LLM."""
        if not self.llm_factory:
            raise ValueError("LLM factory required for summary generation")
        messages = [self._truncate_entity_data(msg, is_recent=(i >= len(messages) - 1), message_index = int((i - 1)/2))
                    for i, msg in enumerate(messages)]
        
        summary_prompt = [
            {
                "role": "system",
                "content": self.summary_instructions
            }
        ]
        if self.last_summary_step == 0:
            steps = f"These are the first steps so there is no historical report to summarize.\n\n"
            steps += f"Here are the first {int(self.chunk_size/2)} execution steps of the agent:\n\n"
        else:
            steps = f"Here is the report from step 0 until step {self.last_summary_step}\n\n{self.historical_report}\n\n"
            steps += f"Here are the next {int(self.chunk_size/2)} execution steps of the agent:\n\n"
        for msg in messages:
            if msg.role in ["system", "assistant"]:
                continue
            steps += msg.content + "\n\n"
        summary_prompt.append({
            "role": "user",
            "content": steps
        })
        response = await self.llm_factory.acall(
            messages=summary_prompt,
            max_tokens=1024,
            temperature=0.3
        )

        if hasattr(response, 'choices'):
            content = response.choices[0].message.content
        else:
            content = response.content[0].text

        return Message(
            role="user",
            content=content,
            metadata={
                "summarized": True,
                "summary_range": f"[{start_idx}-{end_idx}]"
            }
        )
    async def format_conversation(self, conversation: Conversation) -> List[Message]:
        """
        Format conversation by recursively summarizing historical messages from left to right.
        Returns [system_message (if present), historical_summary, recent_messages].
        """
        messages = conversation.messages
        # Handle base cases
        if len(messages) <= self.chunk_size + 1: # account for system message
            return [self._truncate_entity_data(msg, is_recent=(i >= len(messages) - 1), message_index = int((i - 1)/2))
                    for i, msg in enumerate(messages)]

        # Keep system message separate if present
        system_message = None
        if messages[0].role == "system":
            system_message = messages[0]
            messages = messages[1:]
        
        # Keep the most recent chunk as-is
        recent_messages = messages[-self.chunk_size:]
        history = messages[:-self.chunk_size]
        history_size = int(len(history)/2)
        
        formatted = [
                self._truncate_entity_data(msg, is_recent=(i >= len(recent_messages) - 1), message_index = history_size + int((i - 1)/2))
                for i, msg in enumerate(recent_messages)
            ]

        # We turn this off
        if self.summarize_history:
            if len(messages) % self.chunk_size == 0:
                self.historical_report = await self._generate_summary(recent_messages, system_message)
                self.last_summary_step = int(len(messages)/2)
            formatted = [Message(
                    role="user",
                    content=self.historical_report)] + formatted

        if system_message:
            formatted = [system_message] + formatted
        

        return formatted

    def format_message(self, message: Message) -> Message:
        """Format a single message - apply entity data truncation if enabled."""
        return self._truncate_entity_data(message, is_recent=True)