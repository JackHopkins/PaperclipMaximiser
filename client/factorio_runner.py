import ast
import re
import time
from multiprocessing import freeze_support

from backoff import on_exception, expo
from openai.openai_object import OpenAIObject

from factorio_instance import FactorioInstance
from models.insufficient_score_exception import InsufficientScoreException
from models.split_memory import SplitMemory
from vocabulary import Vocabulary

"""
nearest().get("burner-mining-drill").rotate(NORTH)
nearest().place("burner-mining-drill").rotate(EAST)
at(0,0).place("burner-mining-drill").rotate(NORTH)
at(0,0).get("burner-mining-drill").
inventory.get("burner-mining-drill").place(0,0).rotate(NORTH)
"""

import openai


class FactorioRunner:

    def __init__(self,
                 api_key,
                 instance,
                 model="gpt-4",
                 buffer_size=10,
                 beam=1,
                 courtesy_delay=0,
                 fast=True,
                 trace=False,
                 ):

        self.beam = beam
        self.buffer = {}
        self.model = model
        self.buffer_size = buffer_size
        openai.api_key = api_key
        self.max_sequential_exception_count = 3
        self.courtesy_delay = courtesy_delay

        freeze_support()
        self.instance = instance
        self.memory = self.set_memory()
        self.history = []
        self.program_generator = self._get_program_generator
        if not trace:
            pass
        else:
            self.trace = trace

    def set_memory(self):
        static_instance_members = [attr for attr in dir(self.instance)
                                   if not callable(getattr(self.instance, attr))
                                   and not attr.startswith("__")]
        return SplitMemory(ignore_members=static_instance_members, max_commands=self.buffer_size)

    def replay(self):
        with open(f"log/{self.trace}.trace", "r") as f:
            lines = f.readlines()
            for line in lines:
                print(line)
                if line[0] != "#":
                    try:
                        score, response = self.instance.eval(line.rstrip("\n;"))
                        print(response)
                    except Exception as e:
                        print(e)

    @on_exception(expo,
                  (openai.error.RateLimitError, openai.error.APIError))
    def _get_program_generator(self):

        time.sleep(self.courtesy_delay)
        return openai.ChatCompletion.create(
            n=self.beam,
            model=self.model,  # "gpt-3.5-turbo",x
            max_tokens=200,
            messages=next(self.memory),
            stop=["\n\n", "\n#"],
            #stream=True
        )

    def is_valid_python(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _replace_comments(self, code):
        # Regular expression pattern to match a single-line comment
        pattern = r'^#(.*)'

        # Callback function to replace the comment with a method call
        def comment_replacer(match):
            comment_text = match.group(1).strip()
            return f'comment("{comment_text}")'

        # Replace comments in the code
        new_code = re.sub(pattern, comment_replacer, code)
        return new_code

    def _append_buffer(self):
        chunk_generator = self.program_generator()

        if isinstance(chunk_generator, OpenAIObject):
            for index, choice in enumerate(chunk_generator['choices']):
                message = choice['message']
                if index not in self.buffer:
                    self.buffer[index] = ""

                self.buffer[index] += message['content'].strip()
        else:
            # Accumulate the entire content
            for chunk in chunk_generator:
                choice = chunk['choices'][0]
                chunk_message = choice['delta']
                if chunk_message.get('content'):
                    content = chunk_message.get('content')
                    if choice['index'] not in self.buffer:
                        self.buffer[choice['index']] = ""
                    self.buffer[choice['index']] += content
                    self.buffer[choice['index']] = self.buffer[choice['index']].lstrip()

    def __next__(self):
        self._append_buffer()
        # Check if the entire buffer is syntactically valid Python code
        for index, buffer in self.buffer.items():
            if self.is_valid_python(buffer):
                self._execute_buffer(buffer)
                self.buffer[index] = ""
            elif self.is_valid_python("# " + buffer):
                self.buffer[index] = ("# "+buffer+"\n")
                #self.buffer[index] = "\n"
            else:
                # If sampling stops part way through a line, pop the line and interpret.
                non_valid, valid = self.split_on_last_line(buffer)
                if self.is_valid_python(valid):
                    self._execute_buffer(valid)
                else:
                    try:
                        self.memory.log_command(buffer)
                        self.memory.log_error("The provided code is not syntactically valid Python. Only write valid python.")
                    except InsufficientScoreException as e:
                        self._reset()

                self.buffer[index] = ""

    def split_on_last_line(self, s):
        if s.find("\n") != -1:
            return s[s.rfind('\n'):], s[:s.rfind('\n')]
        return "", s

    def _execute_buffer(self, buffer):
        buffer = self._replace_comments(buffer)
        try:
            self.memory.log_command(buffer)
            score, result = self.instance.eval(buffer.strip())
            if score != -1:
                self.memory.log_score(score)
            self.memory.log_variables(self.instance)
            if result and isinstance(result, str):
                if "Error" in result:
                    find_i = result.find(":")
                    message_i = result.rfind(":")
                    if message_i == -1:
                        message = result
                    else:
                        message = result[message_i+1:]
                    try:
                        line = int(result[:find_i])
                        self.memory.log_error(f"Error line {line}: {message.strip()}", line=line)
                    except:
                        self.memory.log_error(result)
                else:
                    self.memory.log_observation(result)
        except InsufficientScoreException as e1:
            self._reset()
        except Exception as e:
            try:
                error, reason = e.args
                self.memory.log_error(f"Error line {error}: {str(reason).replace('_', ' ')}", line=int(error))
            except Exception as e2:
                self.memory.log_error(f"You can't do that action. {str(e)}")
        alerts = self.instance.get_alerts()

        if alerts:
            try:
                self.memory.log_warnings(alerts)
            except InsufficientScoreException as e1:
                self._reset()

    def _reset(self):
        self.instance.reset()
        self.memory = self.set_memory()