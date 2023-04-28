from bcolors import bcolors
from models.memory import Memory


class SplitMemory(Memory):
    """
    This only provides views of the last N action / observation loops.
    """

    def __init__(self, max_observations=5, max_commands=10, max_errors=5, ignore_members=[]):
        super().__init__(size=10, max_history=100, ignore_members=ignore_members)
        self.observations = []
        self.commands = []
        self.errors = []
        self.max_observations = max_observations
        self.max_commands = max_commands
        self.variable_prompt = "Variables: "
        self.command_prompt = "Recent Commands: "

    def __next__(self):
        variables = [(key, self.variables[key]) for key in list(dict.fromkeys(self.variables))[-self.max_observations:]]
        var_string = '\n'.join([f"{key} = {val}" for key, val in variables])
        variables_slot = [{"role": "user", "content": f"{self.variable_prompt}\n{var_string}"}] if variables else []
        messages = [{"role": "system", "content": self.brief}] + \
                    variables_slot + \
                   [{"role": role, "content": command} for role, command in self.commands[-self.max_commands:]]
        return messages

    def log_observation(self, message):
        output = f"{bcolors.OKGREEN}{message}"
        self._log_to_file(output)
        print(output)
        self.observations.append(("assistant", message))

    def log_command(self, message):
        output = f"{bcolors.OKBLUE}{message}"
        self._log_to_trace(message)
        self._log_to_file(output)
        print(output)
        self.commands.append(("assistant", message))

    def log_error(self, message, line=0):
        output = f"{bcolors.FAIL}{message}"
        self._log_to_file(output)
        print(output)
        role, last_command = self.commands[-1]
        lines = last_command.split("\n")
        last_command_lines = lines[:line+1]
        rewritten_last_message = "\n".join(last_command_lines)
        self.commands[-1] = role, rewritten_last_message

        self.commands.append(("user", message))