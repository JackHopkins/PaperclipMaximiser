import json
from typing import List

import bcolors
from models.slot import Slot


class Frame(object):

    def __init__(self, size=10, max_history=100):
        self._history = []
        self.max_size = max_history
        self.size = size

    def __iter__(self, *args, **kwargs) -> List[Slot]:
        """
        Get a frame of messages to pass to GPT.
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def log_error(self, message):
        output = f"{bcolors.FAIL}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, "user", error=True)

    def log_command(self, message):
        output = f"{bcolors.OKBLUE}{message}"
        self._log_to_trace(message)
        self._log_to_file(output)
        print(output)
        self._log_history(message, "assistant")

    def log_observation(self, message):
        output = f"{bcolors.OKGREEN}{message}"
        self._log_to_file(output)
        print(output)
        self._log_history(message, "user")

    def _log_to_file(self, message):
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def _log_history(self, message, role, error=False):
        if isinstance(message, dict):
            message = json.dumps(message, indent = 4)

        if self.history and self.history[-1]['role'] == role and not error:
            self.history[-1]['content'] += f"\n{message}"
        else:
            self.history.append({
                "role": role, "content": message
            })
