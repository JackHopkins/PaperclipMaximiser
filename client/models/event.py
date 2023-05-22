import json

from models.event_type import EventType
from models.role_type import RoleType

class Event:
    def __init__(self,
                 role: RoleType = RoleType.USER,
                 type: EventType = EventType.COMMAND,
                 score: int = 0,
                 message: str = None):
        self.role = role
        self.type = type
        self.message = message
        self.score = score

    def to_message(self):
        return {"role": self.role, "content": self.message}

    def __str__(self):
        return f"{self.score} - {self.message}"

    def __repr__(self):
        return self.__str__()


class EventEncoder(json.JSONEncoder):
    def default(self, obj: Event):
            return {
                "message": obj.message,
                "score": obj.score,
               # "type": obj.type,
                "role": obj.role
            }