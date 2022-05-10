local player = game.players[arg1]
local surface = player.surface
local search_radius = arg2

rcon.print(observe_points_of_interest(surface, player, search_radius))