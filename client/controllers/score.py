from controllers.controller import Controller


class Score(Controller):

    def __init__(self, connection, initial_score):
        Controller.__init__(self, connection)
        self.initial_score = initial_score

    def __call__(self, *args, **kwargs):
        response, execution_time = self._send('score', *args)
        if self.initial_score:
            response['player'] -= self.initial_score
        return response['player']


if __name__ == "__main__":
    score = Score("connection", 0)
    score.load()
    pass
