local player = game.get_player(arg1)
player.teleport({x=arg2, y=arg3})
rcon.print(player.position)