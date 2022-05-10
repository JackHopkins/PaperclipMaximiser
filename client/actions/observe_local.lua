local player = game.players[arg1]
local surface = player.surface
local localBoundingBox = arg2
local field_x, field_y = arg3, arg4
local debug = arg5

rcon.print(get_local_environment(player,  surface, localBoundingBox, field_x, field_y, debug))