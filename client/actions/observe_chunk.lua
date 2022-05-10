local player = game.players[arg1]
local surface = player.surface
local chunk_x, chunk_y = arg2, arg3

rcon.print(observe_chunk(player, surface, chunk_x, chunk_y))