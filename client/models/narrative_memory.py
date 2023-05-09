from models.event_type import EventType
from models.memory import Memory

class NarrativeMemory(Memory):
    """
    This only provides views of the last N action / observation loops.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __next__(self):
        messages = [{"role": "system", "content": self.brief}]

        events = self.get_last_events([EventType.COMMAND,
                                       EventType.OBSERVATION,
                                       EventType.ERROR,
                                       EventType.VARIABLE,
                                       EventType.WARNING],
                                      number=self.size)
        for event in events:
            messages += [{
                "role": event.role,
                "content": event.message
            }]

        return messages