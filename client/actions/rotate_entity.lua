global.actions.rotate_entity = function(player_index, x, y, direction)
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
    local area = {{position.x - 0.5, position.y - 0.5}, {position.x + 0.5, position.y + 0.5}}
    local buildings = surface.find_entities_filtered{area = area, force = "player"}

    game.print("Found "..#buildings.." entities")
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
        error("\"Invalid direction "..(direction).." provided. Please use 0 (north), 2 (east), 4 (south), or 6 (west).\"")
    end

    local current_direction = closest_entity.direction

    game.print("Current direction: "..current_direction)
    for i=0, math.abs(current_direction - direction*2) do
        if current_direction > direction*2 then
            closest_entity.rotate()
        else
            closest_entity.rotate{reverse=true}
        end
    end


    game.print("Rotated "..closest_entity.name.." to "..closest_entity.direction)
    game.print(dump(closest_entity))
    --closest_entity.direction = direction

    local serialized = global.utils.serialize_entity(closest_entity)
    local entity_json = game.table_to_json(serialized)-- game.table_to_json(entity)
    game.print(entity_json)

    return serialized
end