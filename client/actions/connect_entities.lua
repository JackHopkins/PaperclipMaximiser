-- Direction vectors for North, East, South, and West respectively.
local directions = {{x = 0, y = -1}, {x = 1, y = 0}, {x = 0, y = 1}, {x = -1, y = 0}}

function math.round(x)
    return x >= 0 and math.floor(x + 0.5) or math.ceil(x - 0.5)
end

-- Function to get the direction from one position to another.
local function get_direction(from_position, to_position)
    local dx = to_position.x - from_position.x
    local dy = to_position.y - from_position.y
    local adx = math.abs(dx)
    local ady = math.abs(dy)

    if adx > ady then
        if dx > 0 then return 2 end -- East
        if dx < 0 then return 6 end -- West
    else
        if dy > 0 then return 4 end -- South
        if dy < 0 then return 0 end -- North
    end
end

local function place_at_position(player, connection_type, current_position, next_position)
    -- Place the connection entity
    --local dir = next_position and get_direction(current_position, next_position) or 0
    local dir = (next_position and get_direction(current_position, next_position)) or 0
    --local dir = get_direction(current_position, next_position)
    create_beam_point_with_direction(player, dir, current_position)

    -- Check for overlapping entities
    local entities = game.surfaces[1].find_entities_filtered{
        area={{current_position.x - 0.25, current_position.y - 0.25}, {current_position.x + 0.25, current_position.y + 0.25}},
        force = "player"
    }
    if #entities > 0 then
        for _, entity in pairs(entities) do
            if entity.name ~= connection_type and entity.name ~= 'laser-beam' then
                error("Cannot place entity at position (" .. current_position.x .. ", " .. current_position.y .. ") due to overlapping "..entity.name..".")
            end
        end
    end

    local placed_entity = game.surfaces[1].create_entity({
        name = connection_type,
        position = current_position,
        direction = dir,
        force = player.force
    })

    -- Serialize the entity and add it to the list
    local serialized = global.utils.serialize_entity(placed_entity)

    -- Remove the placed entity from the player's inventory
    player.remove_item({name = connection_type, count = 1})

    return serialized
end

-- Additional functions: place_at_position, move_and_place, etc.
local function place_at_position2(player, connection_type, current_position, direction)
    -- Place the connection entity
        local direction_to_next = {x = current_position.x + direction.x, y = current_position.y + direction.y}
        local dir = get_direction(current_position, direction_to_next)

        create_beam_point_with_direction(player, dir, current_position)

        -- Check for overlapping entities
        local entities = game.surfaces[1].find_entities_filtered{area={{current_position.x - 0.25, current_position.y - 0.25}, {current_position.x + 0.25, current_position.y + 0.25}}, force = "player"}
        if #entities > 0 then
           for _, entity in pairs(entities) do
               if entity.name ~= connection_type and entity.name ~= 'laser-beam' then
                   error("Cannot place entity at position (" .. current_position.x .. ", " .. current_position.y .. ") due to overlapping "..entity.name..".")
               end
           end
        end


        --place_position = {x = math.floor(current_position.x), y = math.floor(current_position.y)}
        local placed_entity = game.surfaces[1].create_entity({name = connection_type, position = current_position, direction = dir, force = player.force})

        -- Serialize the entity and add it to the list
        local serialized = global.utils.serialize_entity(placed_entity)

        -- Remove the placed entity from the player's inventory
        player.remove_item({name = connection_type, count = 1})

        return serialized
end

local function move_and_place(player, serialized_entities, connection_type, current_position, direction, distance, axis)
    for i = 1, distance do

        local placed_entity = place_at_position(player, connection_type, current_position, direction)
        table.insert(serialized_entities, placed_entity)

        -- Move to the next position
        current_position[axis] = current_position[axis] + direction[axis]
    end
end

-- Function to find the shortest path.
local function shortest_path(player, source_position, target_position)
    -- Initialize the distances and previous nodes arrays.
    -- Calculate the grid size based on the source and target positions.
    local grid_size_x = math.ceil(math.abs(target_position.x - source_position.x))
    local grid_size_y = math.ceil(math.abs(target_position.y - source_position.y))
    local grid_size = math.max(grid_size_x, grid_size_y)+5
    game.print("Grid size: " .. grid_size)

    -- Initialize the distances and previous nodes arrays.
    local distances = {}
    local previous = {}
    for dx = -grid_size, grid_size do
        distances[dx] = {}
        previous[dx] = {}
        for dy = -grid_size, grid_size do
            distances[dx][dy] = {distance = math.huge, direction = nil, turns = math.huge}
        end
    end

    -- Get the initial direction towards the target.
    local initial_direction = get_direction(source_position, target_position)

    -- The source node is at (0, 0) in our local grid.
    distances[0][0] = {distance = 0, direction = nil, turns = 0}

    local queue = {{x = 0, y = 0}}

    while #queue > 0 do
        local pos = table.remove(queue, 1)

        for i = 1, 4 do
            local nx = pos.x + directions[i].x
            local ny = pos.y + directions[i].y
            local new_direction = i

            -- Make sure we are still inside the local grid.
            if nx >= -grid_size and nx <= grid_size and ny >= -grid_size and ny <= grid_size then
                local entities = game.surfaces[1].find_entities_filtered{
                    area={
                        {source_position.x + nx - 0.5, source_position.y + ny - 0.5},
                        {source_position.x + nx + 0.5, source_position.y + ny + 0.5}
                    },
                    force = "player"
                }
                game.print("Entities at (" .. nx .. ", " .. ny .. "): " .. #entities)

                local turns = distances[pos.x][pos.y].turns
                if distances[pos.x][pos.y].direction ~= nil and distances[pos.x][pos.y].direction ~= new_direction then
                    turns = turns + 1
                end



                local new_distance = distances[pos.x][pos.y].distance + 1
                if #entities > 0 then
                    new_distance = new_distance + 100
                end
                if new_distance < distances[nx][ny].distance or (new_distance == distances[nx][ny].distance and turns < distances[nx][ny].turns) and #entities == 0 then
                    distances[nx][ny] = {distance = new_distance, direction = new_direction, turns = turns}
                    table.insert(queue, {x = nx, y = ny})
                end
                -- Determine the direction based on the next position in the queue
                -- nextPos = queue[1]  -- Peek at next position in queue
                --if nextPos then
                --    new_direction = get_direction({x = nx, y = ny}, {x = nextPos.x, y = nextPos.y})
                --end
            end
        end
    end

    -- Build the path from the target position to the source position.
    local path = {}
    local pos = {x = math.floor(target_position.x - source_position.x), y = math.floor(target_position.y- source_position.y)}
    table.insert(path, 1, target_position)
    while pos.x ~= 0 or pos.y ~= 0 do
        table.insert(path, 1, {x = pos.x + source_position.x, y = pos.y + source_position.y})
        local dir = distances[pos.x][pos.y].direction
        pos = {x = pos.x - directions[dir].x, y = pos.y - directions[dir].y}
    end
    table.insert(path, 1, source_position)

    -- Handle the fractional part of the target position.
    local last_path_position = path[#path]
    local diff_x = target_position.x - last_path_position.x
    local diff_y = target_position.y - last_path_position.y
    local fractional_distance = math.sqrt(diff_x ^ 2 + diff_y ^ 2)

    if fractional_distance > 0 then
        local dir = get_direction(last_path_position, target_position)
        local fractional_pos = {
            x = last_path_position.x + math.floor(fractional_distance * directions[dir].x),
            y = last_path_position.y + math.floor(fractional_distance * directions[dir].y)
        }
        table.insert(path, fractional_pos)
    end

    return path
end

-- Using the new shortest_path function.
global.actions.connect_entities = function(player_index, source_x, source_y, target_x, target_y, connection_type)
    local player = game.players[player_index]
    local start_position = {x = source_x, y = source_y}
    local end_position = {x = target_x, y = target_y}

    if source_x == target_x and source_y == target_y then
        error("Source and target positions are the same.")
    end

    create_beam_point(player, {x = source_x, y = source_y})
    create_beam_point(player, {x = target_x, y = target_y})

    -- Get the shortest path.
    local path = shortest_path(player, start_position, end_position)
    game.print(#path)
    -- Create the connection entities along the path.
    local serialized_entities = {}
    for i = 1, #path - 1 do
        local placed_entity = place_at_position(player, connection_type, path[i], path[i + 1])
        table.insert(serialized_entities, placed_entity)
    end

    return serialized_entities
end
