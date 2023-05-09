from models.event_type import EventType
from models.role_type import RoleType


class Event:
    def __init__(self,
                 role: RoleType = RoleType.USER,
                 type: EventType = EventType.COMMAND,
                 message: str = None):
        self.role = role
        self.type = type
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__str__()