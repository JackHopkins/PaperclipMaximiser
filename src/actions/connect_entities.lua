-- connect_entities.lua

local wire_reach = {
    ['small-electric-pole'] = 4,
    ['medium-electric-pole'] = 9,
    ['big-electric-pole'] = 30,
    ['substation'] = 18
}


function get_step_size(connection_type)
    -- Adjust the step size based on the connection type's wire reach
    return wire_reach[connection_type] or 1
end

function math.round(x)
    return x >= 0 and math.floor(x + 0.5) or math.ceil(x - 0.5)
end

local function has_valid_fluidbox(entity)
    return entity.fluidbox and #entity.fluidbox > 0 and entity.fluidbox[1] and entity.fluidbox[1].get_fluid_system_id
end

local function are_fluidboxes_connected(entity1, entity2)
    if has_valid_fluidbox(entity1) and has_valid_fluidbox(entity2) then
        return entity1.fluidbox[1].get_fluid_system_id() == entity2.fluidbox[1].get_fluid_system_id()
    end
    return false
end

local function is_placeable(position)
    local tile = game.surfaces[1].get_tile(position.x, position.y)
    return tile.collides_with('player-layer') == false
end

local function find_placeable_neighbor(pos, previous_pos)
    local directions = {
        {dx = 0, dy = -1},  -- up
        {dx = 1, dy = 0},   -- right
        {dx = 0, dy = 1},   -- down
        {dx = -1, dy = 0}   -- left
    }

    if previous_pos then
        local desired_dx = pos.x - previous_pos.x
        local desired_dy = pos.y - previous_pos.y
        table.sort(directions, function(a, b)
            local a_score = math.abs(a.dx - desired_dx) + math.abs(a.dy - desired_dy)
            local b_score = math.abs(b.dx - desired_dx) + math.abs(b.dy - desired_dy)
            return a_score < b_score
        end)
    end

    for _, dir in ipairs(directions) do
        local test_pos = {x = pos.x + dir.dx, y = pos.y + dir.dy}
        if is_placeable(test_pos) then
            return test_pos
        end
    end
    return nil
end

local function interpolate_manhattan(pos1, pos2)
    local interpolated = {}
    local dx = pos2.x - pos1.x
    local dy = pos2.y - pos1.y
    local manhatten_distance = math.abs(dx) + math.abs(dy)
    if manhatten_distance > 2 then
        game.print("Interpolating path between " .. serpent.line(pos1) .. " and " .. serpent.line(pos2) .. " with distance " .. manhatten_distance)
    end
    if manhatten_distance > 2 then
        -- Get the number of steps in the path
        local steps = math.max(math.abs(dx), math.abs(dy))
        local x_step = dx / steps
        local y_step = dy / steps
        for i = 1, steps - 1 do
            local new_pos = {x = pos1.x + math.round(x_step * i), y = pos1.y + math.round(y_step * i)}
            if is_placeable(new_pos) then
                table.insert(interpolated, {position = new_pos})
            else
                -- If the position is not placeable, try to find a placeable neighbor
                local neighbor = find_placeable_neighbor(new_pos, pos1)
                if neighbor then
                    table.insert(interpolated, {position = neighbor})
                end
            end
        end

    -- If we are missing a chunk of the path (due to weird game pathing behaviour), we need to interpolate
    elseif math.abs(dx) == 1 and math.abs(dy) == 1 then
        -- Try horizontal then vertical
        local mid_pos = {x = pos2.x, y = pos1.y}
        if is_placeable(mid_pos) then
            table.insert(interpolated, {position = mid_pos})
        else
            -- Try vertical then horizontal
            mid_pos = {x = pos1.x, y = pos2.y}
            if is_placeable(mid_pos) then
                table.insert(interpolated, {position = mid_pos})
            else
                -- If neither works, try to find a placeable neighbor
                mid_pos = find_placeable_neighbor(mid_pos, pos1)
                if mid_pos then
                    table.insert(interpolated, {position = mid_pos})
                end
            end
        end
    end
    --game.print("Interpolated path: " .. serpent.line(interpolated))
    return interpolated
end


global.actions.normalise_path = function(original_path, start_position)
    --- This function interpolates the path to ensure that all positions are placeable and within 1 tile of each other

    local path = {}
    local seen = {}  -- To track seen positions

    -- Helper function to add unique positions
    local function add_unique(pos)
        local key = pos.x .. "," .. pos.y
        if not seen[key] then
            if is_placeable(pos) then
                table.insert(path, {position = pos})
                seen[key] = true
                return pos
            else
                local alt_pos = find_placeable_neighbor(pos, previous_pos)
                if alt_pos then
                    local alt_key = alt_pos.x .. "," .. alt_pos.y
                    if not seen[alt_key] then
                        table.insert(path, {position = alt_pos})
                        seen[alt_key] = true
                        return alt_pos
                    end
                end
            end
        end
        return nil
    end


    -- Add start position first
    local previous_pos = nil
    previous_pos = add_unique(start_position) or start_position

    for i = 1, #original_path - 1 do
        local current_pos = add_unique(original_path[i].position, previous_pos)
        if current_pos then
            previous_pos = current_pos
            local interpolated = interpolate_manhattan(current_pos, original_path[i+1].position)
            for _, point in ipairs(interpolated) do
                local new_pos = add_unique(point.position, previous_pos)
                if new_pos then previous_pos = new_pos end
            end
        end
    end

    add_unique(original_path[#original_path].position)

    --- @jack: Do we need this?
    local previous_pos = path[1].position
    for i = 1, #path do
        local manhatten_distance = math.abs(path[i].position.x - previous_pos.x) + math.abs(path[i].position.y - previous_pos.y)
        if manhatten_distance > 1 then
            local interpolated = interpolate_manhattan(previous_pos, path[i].position)
            -- for each interpolated point, add it to the path at the correct index
            for _, point in ipairs(interpolated) do
                table.insert(path, i, point)
                i = i + 1
            end
        end
        previous_pos = path[i].position
    end

    return path
end

global.utils.reverse_path = function(path)
    local reversed = {}
    for i = #path, 1, -1 do
        table.insert(reversed, path[i])
    end
    return reversed
end

local function get_direction(from_position, to_position)
    local dx = to_position.x - from_position.x
    local dy = to_position.y - from_position.y
    local adx = math.abs(dx)
    local ady = math.abs(dy)

    -- Threshold for considering movement as diagonal
    local diagonal_threshold = 0.5

    if adx > ady then
        if dx > 0 then
            if ady / adx > diagonal_threshold then
                return dy > 0 and 3 or 1  -- Southeast or Northeast
            else
                return 2  -- East
            end
        else
            if ady / adx > diagonal_threshold then
                return dy > 0 and 5 or 7  -- Southwest or Northwest
            else
                return 6  -- West
            end
        end
    else
        if dy > 0 then
            if adx / ady > diagonal_threshold then
                return dx > 0 and 3 or 5  -- Southeast or Southwest
            else
                return 4  -- South
            end
        else
            if adx / ady > diagonal_threshold then
                return dx > 0 and 1 or 7  -- Northeast or Northwest
            else
                return 0  -- North
            end
        end
    end
end

local function place_at_position(player, connection_type, current_position, dir, serialized_entities)

    -- Check if the connection_type is an electricity pole
    local is_electric_pole = wire_reach[connection_type] ~= nil
    local placement_position = current_position
    local existing_entity = nil
    if is_electric_pole then
        -- For electric poles, find a non-colliding position nearby
        placement_position = game.surfaces[1].find_non_colliding_position(connection_type, current_position, 3, 0.1)
        if not placement_position then
            error("Cannot find a suitable position to place " .. connection_type .. " near (" .. current_position.x .. ", " .. current_position.y .. ").")
        end
    else
        local entities = game.surfaces[1].find_entities_filtered{
            position = current_position,
            force = "player"
        }
        for _, entity in pairs(entities) do
            if entity.name == connection_type then
                existing_entity = entity
                break
            elseif entity.name ~= 'laser-beam' and entity.name ~= 'character' then
                --error("Cannot place entity at position (" .. current_position.x .. ", " .. current_position.y .. ") due to overlapping " .. entity.name .. ".")
            end
        end
    end

    if existing_entity then
        if existing_entity.direction ~= dir then
            existing_entity.direction = dir
            -- Find and update the existing entity in serialized_entities
            for i, serialized in ipairs(serialized_entities) do
                if serialized.position.x == current_position.x and serialized.position.y == current_position.y then
                    serialized_entities[i] = global.utils.serialize_entity(existing_entity)
                    return  -- Exit the function as we've updated the existing entity
                end
            end
            -- If not found in serialized_entities, add it
            table.insert(serialized_entities, global.utils.serialize_entity(existing_entity))
        end
        return  -- Exit the function as we've handled the existing entity
    end

    -- Check if the player has the entity in their inventory
    local has_item = false
    for _, inv in pairs({defines.inventory.character_main}) do
        if player.get_inventory(inv) then
            local count = player.get_inventory(inv).get_item_count(connection_type)
            if count > 0 then
                has_item = true
                break
            end
        end
    end
    if not has_item then
        error("Player does not have the required item in their inventory.")
    end

    -- Check if the entity can be placed at the given position
    if not game.surfaces[1].can_place_entity{
        name = connection_type,
        position = placement_position,
        direction = dir,
        force = player.force
    } then
        global.actions.avoid_entity(player.index, connection_type, placement_position)
    end

    if game.surfaces[1].can_place_entity{
        name = connection_type,
        position = placement_position,
        direction = dir,
        force = player.force
    } then
        local placed_entity = game.surfaces[1].create_entity({
            name = connection_type,
            position = placement_position,
            direction = dir,
            force = player.force
        })

        if placed_entity ~= nil then
            player.remove_item({name = connection_type, count = 1})
            local serialized = global.utils.serialize_entity(placed_entity)
            table.insert(serialized_entities, serialized)
        end
    end
end


local function get_closest_entity(player, position)
    local closest_distance = math.huge
    local closest_entity = nil
    local surface = player.surface
    -- local distance = 0
    -- local position = {x = math.floor(position.x), y = math.floor(position.y)}
    -- local area = {{position.x - 1, position.y - 1}, {position.x + 1, position.y + 1}}

    local entities = surface.find_entities_filtered{position = position, force = "player", radius = 3}

    -- Find the closest entities
    for _, entity in ipairs(entities) do
        if entity.name ~= 'character' and entity.name ~= 'laser-beam' then
            local distance = ((position.x - entity.position.x) ^ 2 + (position.y - entity.position.y) ^ 2) ^ 0.5
            if distance < closest_distance then
                closest_distance = distance
                closest_entity = entity
            end
        end
    end

    --if closest_entity == nil then
    --    error("No entity at the given coordinates." .. position.x .. ", " .. position.y)
    --end

    return closest_entity
end

-- Using the new shortest_path function.
global.actions.connect_entities = function(player_index, source_x, source_y, target_x, target_y, path_handle, connection_type)
    local player = game.get_player(player_index)

    local start_position = {x = math.floor(source_x*2)/2, y = math.floor(source_y*2)/2}
    local end_position = {x = math.floor(target_x*2)/2, y = math.floor(target_y*2)/2}

    local raw_path = global.paths[path_handle]

    -- Check if path is valid
    if not raw_path or type(raw_path) ~= "table" or #raw_path == 0 then
        error("Invalid path: " .. serpent.line(path))
    end

    --- This invocation interpolates the path to ensure that all positions are placeable and within 1 tile of each other
    local path = global.actions.normalise_path(raw_path, start_position) --{x = source_x, y = source_y})

    --create_beam_point_with_direction(player, 0, start_position)
    --create_beam_point_with_direction(player, 2, end_position)
    for i = 1, #path - 1 do
        --create_arrow_with_direction(player, get_direction(path[i].position, path[i + 1].position), path[i].position)
    end

    local serialized_entities = {}
    local xdiff = math.abs(source_x-target_x)
    local ydiff = math.abs(source_y-target_y)


    if xdiff + ydiff < 1 then
        local dir = get_direction(start_position, end_position)
        local entity_dir = global.utils.get_entity_direction(connection_type, dir/2)
        place_at_position(player, connection_type, start_position, entity_dir, serialized_entities)
        return {entities = serialized_entities, connected = true}
    end

    --game.print("Diff: " .. xdiff + ydiff)
    local step_size = get_step_size(connection_type)
    local initial_offset = 0
    if step_size ~= 1 then
        initial_offset = step_size - 1
    end
    local dir

    if connection_type == 'pipe' then
        place_at_position(player, connection_type, start_position, dir, serialized_entities)
    end

    local last_position = path[1].position
    local last_dir
    for i = 1, #path-1, step_size do
        original_dir = (path[i + step_size] and get_direction(path[i].position, path[i + step_size].position)) or get_direction(path[i].position, end_position)
        dir = global.utils.get_entity_direction(connection_type, original_dir/2)
        place_at_position(player, connection_type, path[i].position, dir, serialized_entities)
        last_position = path[i].position
        last_dir = dir
    end

    local preemptive_target = {x = (target_x + last_position.x)/2, y = (target_y + last_position.y)/2}

    -- If the connection_type is a belt
    if connection_type == 'transport-belt' then

        -- if the last path position is the same as the target, then we don't need to place a new entity
        if path[#path].position.x == target_x and path[#path].position.y == target_y then
            place_at_position(player, connection_type, path[#path].position, last_dir, serialized_entities) -- original_dir/2, serialized_entities)
        else
            local dir = get_direction(path[#path].position, {x = target_x, y = target_y})
            local ndir = global.utils.get_entity_direction(connection_type, dir/2)
            place_at_position(player, connection_type, path[#path].position, ndir, serialized_entities)
        end
        place_at_position(player, connection_type, end_position, get_direction(preemptive_target, { x = target_x, y = target_y }), serialized_entities)

        -- We might want to remove this last one
        -- if the path is longer than 2, we need to place the last entity at the target position to ensure connection
        if #path > 2 then
            place_at_position(player, connection_type, preemptive_target, get_direction(path[#path-2].position, preemptive_target), serialized_entities)
        end

    elseif connection_type == 'pipe' then
        -- If the connection_type is a pipe, we have to do some extra work to ensure no missing pipes
        place_at_position(player, connection_type, path[#path].position, get_direction(path[#path].position, preemptive_target), serialized_entities)
        place_at_position(player, connection_type, end_position, get_direction(preemptive_target, { x = target_x, y = target_y }), serialized_entities)
        place_at_position(player, connection_type, preemptive_target, get_direction(path[#path].position, preemptive_target), serialized_entities)
        --place_at_position(player, connection_type, path[#path-1].position, get_direction(path[#path].position, preemptive_target), serialized_entities)

    else
        -- If the connection_type is an electricity pole, we need to place the last entity at the target position to ensure connection
        place_at_position(player, connection_type, path[#path].position, get_direction(path[#path].position, preemptive_target), serialized_entities)
        place_at_position(player, connection_type, end_position, get_direction(preemptive_target, { x = target_x, y = target_y }), serialized_entities)
    end


        --create_beam_point(game.players[1], path[#path].position)
        --create_beam_point(game.players[1], end_position)

        --if connection_type ~= 'transport-belt' then
        --original_dir = path[1] and get_direction(end_position, path[1].position) or 0
        --else
        --    original_dir = path[1] and get_direction(path[1].position, end_position) or 0
        --end
        --dir = global.utils.get_entity_direction(connection_type, original_dir/2)

        --game.print("Source entity: " .. source_entity.fluidbox[1].get_fluid_system_id())
        --game.print("Target entity: " .. target_entity.fluidbox[1].get_fluid_system_id())

        -- Check if entities are connected
        local source_entity = get_closest_entity(player, {x = source_x, y = source_y})
        local target_entity = get_closest_entity(player, {x = target_x, y = target_y})
        local is_connected = false

        if source_entity and target_entity then
            is_connected = are_fluidboxes_connected(source_entity, target_entity)
        end

        if not is_connected then
            is_connected = (#serialized_entities > 0)
        end

        game.print("Connection status: " .. tostring(is_connected))

        return {
            entities = serialized_entities,
            connected = is_connected
        }
    end
