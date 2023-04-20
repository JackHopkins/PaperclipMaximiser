from controllers._action import Action


class Score(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def __call__(self, *args, **kwargs):
        response, execution_time = self._send('score', *args)
        if self.initial_score:
            response['player'] -= self.game_state.initial_score
        return response['player']


if __name__ == "__main__":
    score = Score("connection", 0)
    score.load()
    pass
