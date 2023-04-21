global.actions.move_to = function(player_index, x, y)
    local target_position = {x=x, y=y}
    local player = game.players[player_index]
    local surface = player.surface
    local start_position = player.position
    local force = player.force
    local path_id = surface.request_path{
        bounding_box = {{-0.5, -0.5}, {0.5, 0.5}},
        collision_mask = "player-layer",
        force = force,
        goal = target_position,
        pathfind_flags = {prefer_straight_paths = true},
        start = start_position
    }

    return path_id
end

script.on_event(defines.events.on_script_path_request_finished, function(event)
    local path = event.path

    local function path_to_string(path)
        local path_string = ""
        for i, waypoint in ipairs(path) do
            path_string = path_string .. string.format("(%g, %g)", waypoint.x, waypoint.y)
            if i < #path then
                path_string = path_string .. " -> "
            end
        end
        return path_string
    end

    if path then
        rcon.print("Path found with " .. #path .. " waypoints.")
        local path_string = path_to_string(path)
        rcon.print("Path: " .. path_string)
    else
        rcon.print("No path found.")
    end
end)