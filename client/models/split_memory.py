from bcolors import bcolors
from models.event_type import EventType
from models.memory import Memory


class SplitMemory(Memory):
    """
    This only provides views of the last N action / observation loops.
    """

    def __init__(self, max_observations=5, max_commands=10, max_errors=5, ignore_members=[]):
        super().__init__(size=10, max_history=max_commands, ignore_members=ignore_members)
        self.observations = []
        self.commands = []
        self.errors = []
        self.warnings = []
        self.max_observations = max_observations
        self.max_commands = max_commands
        self.variable_prompt = "Variables: "
        self.warning_prompt = "Warnings: "
        self.command_prompt = "Recent Commands: "

    def __next__(self):

        var_string = self.get_last_events(EventType.VARIABLE)
        variables_slot = [{"role": "user", "content": f"{self.variable_prompt}\n{var_string}"}] if var_string else []

        warning_string = self.get_last_events(EventType.WARNING)
        warnings_slot = [{"role": "user", "content": f"{self.warning_prompt}\n{warning_string}"}] if warning_string else []

        messages = [{"role": "system", "content": self.brief}]
        if warnings_slot:
            messages += warnings_slot
        if variables_slot:
            messages += variables_slot

        events = self.get_last_events([EventType.COMMAND, EventType.OBSERVATION, EventType.ERROR], number=self.max_commands)
        for event in events:
            messages += [{
                "role": event.role,
                "content": event.message
            }]

        return messages