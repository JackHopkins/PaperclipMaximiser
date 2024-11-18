import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional

from datasetgen.mcts.conversation import Message, Conversation

PLANNING_ADDITION_PROMPT = \
"""
First bring out a thorough step-by-step plan how you can achieve this task and then create the python script to achieve the task.
For your plan, follow this structure:
1) What entities are needed for the task
2) What entities do we have on the map, in different entity inventories or in our inventory
3) What entities are we missing for the task
4) Execution -- Taking into account 1,2 and 3, what steps do we need to take to successfully carry out the task
"""


class CodeProcessor:
    """Handles code block processing and summarization"""

    @staticmethod
    def extract_code_blocks(content: str) -> List[Tuple[str, int, int]]:
        """
        Extract code blocks that are between comments.
        Returns list of (code, start_line, end_line) tuples.
        """
        lines = content.splitlines()
        blocks = []
        current_block = []
        block_start = None

        for i, line in enumerate(lines, 1):  # Start line counting from 1
            stripped = line.strip()

            if stripped.startswith('#'):
                # If we have an active block, end it
                if current_block:
                    blocks.append((
                        '\n'.join(current_block),
                        block_start,
                        i - 1
                    ))
                    current_block = []
                    block_start = None
            else:
                # If this is first code line after comment
                if stripped and block_start is None:
                    block_start = i
                # Add non-empty lines to current block
                if stripped:
                    current_block.append(line)

        # Handle any remaining block
        if current_block:
            blocks.append((
                '\n'.join(current_block),
                block_start,
                len(lines)
            ))

        # If no blocks found, treat entire content as one block
        if not blocks:
            return [(content, 1, len(lines))]

        return blocks

    @staticmethod
    def summarize_code_block(code: str, start_line: int = None, end_line: int = None,
                             preserve_comments: bool = True) -> str:
        """
        Summarize a code block by replacing code sections with line count indicators.
        Uses plural form when omitting multiple lines.
        """
        lines = code.splitlines()

        # If there are no lines, return empty string
        if not lines:
            return ""

        # Check if this is a pure code block (no comments)
        has_comments = any(line.strip().startswith('#') for line in lines)

        if not has_comments:
            # For pure code blocks, treat the entire content as one section
            return f"<LINES 1-{len(lines)} OMITTED>"

        # Regular processing for blocks with comments
        result = []
        code_start = None
        code_lines = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith('#'):
                # If we were collecting code lines
                if code_start is not None:
                    # Determine whether to use singular or plural form
                    if code_lines == 1:
                        result.append(f"<LINE {code_start} OMITTED>")
                    else:
                        result.append(f"<LINES {code_start}-{code_start + code_lines - 1} OMITTED>")
                    code_start = None
                    code_lines = 0
                result.append(line)
            else:
                if stripped:
                    if code_start is None:
                        code_start = i
                    code_lines += 1

        # Handle any remaining code section
        if code_start is not None:
            if code_lines == 1:
                result.append(f"<LINE {code_start} OMITTED>")
            else:
                result.append(f"<LINES {code_start}-{code_start + code_lines - 1} OMITTED>")

        return '\n'.join(result)

class ConversationFormatter(ABC):
    """Abstract base class for conversation formatting strategies"""

    @abstractmethod
    def format_conversation(self, conversation: Conversation) -> List[Message]:
        """
        Format a conversation according to the specific strategy.
        Returns a list of formatted messages ready for LLM consumption.
        """
        pass

    @abstractmethod
    def format_message(self, message: Message) -> Message:
        """Format a single message according to the strategy"""
        pass

    def to_llm_messages(self, formatted_msgs: List[Message]) -> List[Dict[str, str]]:
        """Convert formatted messages to LLM-compatible format"""
        return [{"role": msg.role, "content": msg.content} for msg in formatted_msgs]

class DefaultFormatter(ConversationFormatter):
    def format_conversation(self, conversation: Conversation) -> List[Message]:
        return conversation.messages

    def format_message(self, message: Message) -> Message:
        return message


class StructurePreservingFormatter(ConversationFormatter):
    """
    Formatter that preserves program structure through comments while reducing token usage.
    """

    def __init__(self):
        self.code_processor = CodeProcessor()

    def format_message(self, message: Message, is_last: bool = False) -> Optional[Message]:
        if message.role == "system":
            return Message(role="system", content=message.content)

        elif message.role == "assistant":
            if not is_last:  # Summarize all but the last program
                content = self.code_processor.summarize_code_block(message.content)
                return Message(
                    role="assistant",
                    content=content,
                    metadata={"summarized": True}
                )
            else:
                return Message(
                    role="assistant",
                    content=message.content,
                    metadata={"summarized": False}
                )

        elif message.role == "user":
            content = message.content
            try:
                if "Execution result:" in content:
                    result = content.split("Execution result:")[1].split("Updated state:")[0]
                    return Message(
                        role="user",
                        content=f"Execution result:\n{result.strip()}"
                    )
                else:
                    return Message(
                        role="user",
                        content=content.strip()
                    )
            except Exception as e:
                print(f"Error formatting user message: {str(e)}")
                return None

        return None

    def format_conversation(self, conversation: Conversation) -> List[Message]:
        formatted = []

        # Handle system message if present
        if conversation.messages and conversation.messages[0].role == "system":
            formatted.append(self.format_message(conversation.messages[0]))
            messages = conversation.messages[1:]
        else:
            messages = conversation.messages

        last_message_role = messages[-1].role

        # Format each message
        for i, msg in enumerate(messages):
            if last_message_role == 'assistant':
                formatted_msg = self.format_message(msg, is_last=(i == len(messages) - 1))
            elif last_message_role == 'user':
                formatted_msg = self.format_message(msg, is_last=(i == len(messages) - 2))
            if formatted_msg:
                formatted.append(formatted_msg)

        return formatted