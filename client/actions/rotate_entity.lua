global.actions.rotate_entity = function(player_index, direction, x, y)
    local player = game.players[player_index]
    local position = {x=x, y=y}
    local surface = player.surface

    local function table_contains(tbl, element)
        for _, value in ipairs(tbl) do
            if value == element then
                return true
            end
        end
        return false
    end

    local closest_distance = math.huge
    local closest_entity = nil
    local area = {{position.x - 1, position.y - 1}, {position.x + 1, position.y + 1}}
    local buildings = surface.find_entities_filtered{area = area}

    -- Find the closest building
    for _, building in ipairs(buildings) do
        if building.rotatable and building.name ~= 'character' then
            local distance = ((position.x - building.position.x) ^ 2 + (position.y - building.position.y) ^ 2) ^ 0.5
            if distance < closest_distance then
                closest_distance = distance
                closest_entity = building
            end
        end
    end

    if closest_entity == nil then
        error("No entity to rotate at the given coordinates.")
    end

    local valid_directions = {0, 2, 4, 6}

    if not table_contains(valid_directions, direction*2) then
        error("Invalid direction provided. Please use 0 (north), 2 (east), 4 (south), or 6 (west).")
    end
    game.print("Rotated "..closest_entity.name.." to "..direction)
    game.print(dump(closest_entity))
    closest_entity.direction = direction

    return 1
end