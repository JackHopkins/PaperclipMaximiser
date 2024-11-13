import os
from typing import Literal

import openai
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
load_dotenv()


class LLMFactory:
    def __init__(self, model: str, beam: int = 1):
        self.model = model
        self.beam = beam

    def merge_contiguous_messages(self, messages):
        if not messages:
            return messages

        merged_messages = [messages[0]]

        for message in messages[1:]:
            if message['role'] == merged_messages[-1]['role']:
                merged_messages[-1]['content'] += "\n\n" + message['content']
            else:
                merged_messages.append(message)

        return merged_messages

    def remove_whitespace_blocks(self, messages):
        return [
            message for message in messages
            if message['content'].strip()
        ]

    def call(self, *args, **kwargs):
        max_tokens = kwargs.get('max_tokens', 1000)
        model_to_use = kwargs.get('model', self.model)
        if "claude" in model_to_use:
            # Set up and call the Anthropic API
            api_key = os.getenv('ANTHROPIC_API_KEY')

            # Remove the 'system' role from the first message and replace it with 'user'
            messages = kwargs.get('messages', [])
            if messages[0]['role'] == "system":
                messages[0]['role'] = "user"

            # Remove final assistant content that ends with trailing whitespace
            if messages[-1]['role'] == "assistant":
                messages[-1]['content'] = messages[-1]['content'].strip()

            # If the most recent message is from the assistant, add a user message to prompt the assistant
            if messages[-1]['role'] == "assistant":
                messages.append({
                    "role": "user",
                    "content": "Success."
                })

            messages = self.remove_whitespace_blocks(messages)
            messages = self.merge_contiguous_messages(messages)


            try:
                response = anthropic.Anthropic().messages.create(
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=max_tokens,
                    model=model_to_use,
                    messages=messages,
                    stop_sequences=["```END"],
                )
            except Exception as e:
                print(e)
                raise

            return response
        elif "deepseek" in model_to_use:
            client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            response = client.chat.completions.create(*args,
                                                  **kwargs,
                                                  temperature=1,
                                                  model=model,
                                                  #stop=["\n\n"],
                                                  stop=["```END"],
                                                  #top_p=1,
                                                  presence_penalty=0.5,
                                                  frequency_penalty=0.8,
                                                  stream=False)
            return response

        elif "o1-mini" in model_to_use:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # replace `max_tokens` with `max_completion_tokens` for OpenAI API
            if "max_tokens" in kwargs:
                kwargs.pop("max_tokens")

            return client.chat.completions.create(*args, n=self.beam,
                                                  **kwargs,
                                                  #temperature=0.9,
                                                  #stop=["\n\n"],  # , "\n#"],
                                                  #presence_penalty=1,
                                                  #frequency_penalty=0.6,
                                                  stream=False)
        else:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            assert "messages" in kwargs, "You must provide a list of messages to the model."
            return client.chat.completions.create(model = model_to_use,
                                                  max_tokens = kwargs.get('max_tokens', 2048),
                                                  temperature=kwargs.get('temperature', 0.3),
                                                  messages=kwargs.get('messages', None),
                                                  stop=kwargs.get('stop_sequences', None),
                                                  #presence_penalty=1,
                                                  #frequency_penalty=0.6,
                                                  stream=False)

