from controllers._action import Action


class Print(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def load(self):
        pass

    def __call__(self, message: str) -> bool:

        response, elapsed = self.execute(message)
        if not response:
            raise Exception("Could not print.", response)
        return True
