-- Observe.lua
function observe ()
    local player = game.players[arg1]
    local inventory = player.get_main_inventory().get_contents()
    local surface = player.surface
    local chunk_x, chunk_y = arg2, arg3
    local localBoundingBox = arg4
    local field_x, field_y = arg5, arg6
    local search_radius = arg7
    local debug = arg8
    local include = arg9

    local response = {}

    if include['inventory'] == nil or include['inventory'] then
        response['inventory'] = inventory
    end

    if include['points_of_interest'] == nil or include['points_of_interest'] then
        response['points_of_interest'] = observe_points_of_interest(surface, player, search_radius)
        response['distance_to_points_of_interest'] = global.distances_to_nearest
    end

    if include['local_environment'] == nil or include['local_environment'] then
        response['local_environment'] = get_local_environment(player,  surface, localBoundingBox, field_x, field_y, debug)
    end

    if include['buildable'] == nil or include['buildable'] then
        response['buildable'] = observe_buildable(player, inventory)
    end

    if include['chunk'] == nil or include['chunk'] then
        response['chunk'] = observe_chunk(player, surface, chunk_x, chunk_y)
    end

    if include['position'] == nil or include['position'] then
        response['position'] = player.position
    end

    if include['objective'] == nil or include['objective'] then
        response['objective'] = observe_statistics(player)
    end

    return dump(response)
end


--rcon.print(observe())
local status, response = pcall(observe)

if status ~= true then
    rcon.print(status)
    rcon.print(dump(response))--> a 121
else
    rcon.print(dump(response))
end

--serpent.line(response)
