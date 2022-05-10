local player = game.players[arg1]
rcon.print(player.get_main_inventory().insert{name=arg2:gsub("-", "_"), count=arg3})