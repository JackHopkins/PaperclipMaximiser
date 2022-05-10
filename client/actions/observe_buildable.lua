local player = game.players[arg1]
local inventory = player.get_main_inventory().get_contents()

rcon.print(observe_buildable(player, inventory))