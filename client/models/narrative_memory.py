from models.memory import Memory

class NarrativeMemory(Memory):
    """
    This only provides views of the last N action / observation loops.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __next__(self):
        messages = [{"role": "system", "content": self.brief}] + self.history[-self.size:]
        return messages