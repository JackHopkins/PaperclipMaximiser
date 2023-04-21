
global.actions.inspect_entities = function(player_index, radius_)
    local player = game.players[player_index]
    local radius = tonumber(radius_) or 5
    function find_connected_entities(entity)
        local entities_to_search = {
            {entity = entity, dx = 0, dy = -1, dir = defines.direction.north},
            {entity = entity, dx = 0, dy = 1, dir = defines.direction.south},
            {entity = entity, dx = 1, dy = 0, dir = defines.direction.east},
            {entity = entity, dx = -1, dy = 0, dir = defines.direction.west}
        }

        local connected_entities = {}

        for _, search in ipairs(entities_to_search) do
            local search_pos = {x = entity.position.x + search.dx, y = entity.position.y + search.dy}
            local found_entity = entity.surface.find_entity(entity.name, search_pos)

            if found_entity then
                if entity.type == "transport-belt" and found_entity.direction == search.dir then
                    table.insert(connected_entities, found_entity)
                elseif entity.type == "pipe" then
                    table.insert(connected_entities, found_entity)
                end
            end
        end

        return connected_entities
    end


    function recursive_search(entity, visited, path_ends)
        if visited[entity.unit_number] then
            return
        end

        visited[entity.unit_number] = true
        local connected_entities = find_connected_entities(entity)

        if connected_entities and #connected_entities > 0 then
            local unconnected_neighbours = 0
            for _, connected_entity in ipairs(connected_entities) do
                if not visited[connected_entity.unit_number] then
                    unconnected_neighbours = unconnected_neighbours + 1
                    recursive_search(connected_entity, visited, path_ends)
                end
            end

            if unconnected_neighbours == 1 then
                path_ends[entity.unit_number] = entity
            end
        else
            path_ends[entity.unit_number] = entity
        end
    end

    function find_path_ends(entity)
        local visited = {}
        local path_ends = {}
        recursive_search(entity, visited, path_ends)
        return path_ends
    end

    local entity_data = inspect(player, radius)

    local result = {}

    for i, data in ipairs(entity_data) do
        local position = {x=data.position.x-player.position.x, y=data.position.y-player.position.y}

        local entity_info = {
            name = data.name:gsub("-", "_"),
            position = position,
            direction = data.direction,
            health = data.health,
            force = data.force,
            energy = data.energy,
            contents = data.contents,
            crafting_progress = data.crafting_progress,
            productivity_bonus = data.productivity_bonus,
            orientation = data.orientation,
            crafted_items = data.crafted_items,
            ingredients = data.ingredients,
            path_ends = data.path_ends,
            warnings = data.warnings
        }

        table.insert(result, entity_info)
    end

    return result
end