local player = game.players[arg1]
--defines.inventory.character_main
rcon.print(dump(player.get_main_inventory().get_contents()))