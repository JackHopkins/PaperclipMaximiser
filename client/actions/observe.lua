local player = game.players[arg1]
local inventory = player.get_main_inventory().get_contents()
local surface = player.surface
local chunk_x, chunk_y = arg2, arg3
local localBoundingBox = arg4
local field_x, field_y = arg5, arg6
local search_radius = arg7
local debug = arg8

local response = {
    inventory=inventory,
    points_of_interest=observe_points_of_interest(surface, player, search_radius),
    local_environment=get_local_environment(player,  surface, localBoundingBox, field_x, field_y, debug),
    buildable=observe_buildable(player, inventory),
    chunk=observe_chunk(player, surface, chunk_x, chunk_y),
    position=player.position
}
--serpent.line(response)
rcon.print(serpent.line(response))
