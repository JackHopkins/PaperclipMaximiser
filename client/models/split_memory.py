import json

from models.event_type import EventType
from models.memory import Memory


class SplitMemory(Memory):
    """
    This only provides views of the last N action / observation loops.
    """

    def __init__(self, max_observations=5,
                 max_commands=10,
                 max_errors=5,
                 ignore_members=[],
                 score_threshold=8,
                 llama_file='llama_events.jsonl'):
        super().__init__(size=10,
                         max_history=max_commands,
                         ignore_members=ignore_members,
                         llama_file=llama_file,
                         score_threshold=score_threshold)
        self.observations = []
        self.commands = []
        self.errors = []
        self.warnings = []
        self.max_observations = max_observations
        self.max_history = max_commands
        self.variable_prompt = "Variables: "
        self.warning_prompt = "Warnings: "
        self.command_prompt = "Recent History: "

    def get_events(self):
        latest_variable_event = self.get_last_events(filters=[EventType.VARIABLE], number=1)
        if latest_variable_event and self.variable_prompt not in latest_variable_event[0].message:
            latest_variable_event[0].message = f"{self.variable_prompt}\n{latest_variable_event[0].message}"

        latest_warning_event = self.get_last_events(filters=[EventType.WARNING], number=1)
        if latest_warning_event and self.warning_prompt not in latest_warning_event[0].message:
            latest_warning_event[0].message = f"{self.warning_prompt}\n{latest_warning_event[0].message}"

        events = self.get_last_events(filters=[EventType.COMMAND, EventType.OBSERVATION, EventType.ERROR],
                                      number=self.max_history)

        if events and self.command_prompt not in events[0].message:
            events[0].message = f"{self.command_prompt}\n{events[0].message}"

        all_events = latest_variable_event + latest_warning_event + events
        return all_events

    def __next__(self):
        events = self.get_events()
        messages = self.get_messages(events)
        return messages
