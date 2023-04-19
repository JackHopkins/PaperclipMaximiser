local score = production_score.get_production_scores()
game.players[1].set_goal_description(score['player'])
rcon.print(dump(score))
