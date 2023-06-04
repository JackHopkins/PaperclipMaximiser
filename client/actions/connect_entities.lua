-- Function to get the direction from one position to another
local function get_direction(from_position, to_position)
    local dx = to_position.x - from_position.x
    local dy = to_position.y - from_position.y

    if math.abs(dx) > math.abs(dy) then
        -- East or West
        if dx > 0 then
            return 2 -- East
        else
            return 6 -- West
        end
    else
        -- North or South
        if dy > 0 then
            return 4 -- South
        else
            return 0 -- North
        end
    end
end


global.actions.connect_entities = function(player_index, source_x, source_y, target_x, target_y, connection_type)
    local player = game.players[player_index]

    --local distance = math.sqrt(direction.x ^ 2 + direction.y ^ 2)
    -- Calculate the Manhattan distance
    if source_x == target_x and source_y == target_y then
        error("Source and target positions are the same.")
    end


    local current_position = {x = source_x, y = source_y}
    if target_y < source_y and target_x == source_x then
        target_y = target_y - 0.5
        --current_position.y = current_position.y - 0.5
    elseif target_y < source_y and target_x < source_x then
        target_x = target_x - 0.5
        current_position.y = current_position.y - 0.5
    elseif target_y < source_y and target_x > source_x then
        target_y = target_y + 0.5
        target_x = target_x + 1.5
        current_position.x = current_position.x + 0.5
        --current_position.y = current_position.y -- - 0.5
    elseif target_y > source_y and target_x < source_x then
        current_position.x = current_position.x - 0.5
        current_position.y = current_position.y + 0.5
    elseif target_y > source_y and target_x > source_x then
        current_position.x = current_position.x + 0.5
        current_position.y = current_position.y + 0.5
    end
    local distance = math.abs(target_x - source_x) + math.abs(target_y - source_y)



    --direction.x = direction.x / distance
    --direction.y = direction.y / distance

    -- Check if player has the required items in their inventory
    local count = player.get_main_inventory().get_item_count(connection_type)
    if count < distance then
        error("\"You need "..math.ceil(distance).." "..connection_type.." in your inventory, but you only have "..count..".\"")
    end

    -- Check for overlapping entities and place the connection entities
    game.print("Current position: (" .. current_position.x .. ", " .. current_position.y .. ")")
    game.print("Target position: (" .. target_x .. ", " .. target_y .. ")")

    local serialized_entities = {}
    for i = 1, distance do
        -- Check for overlapping entities
        local entities = game.surfaces[1].find_entities_filtered{area={{current_position.x - 0.5, current_position.y - 0.5}, {current_position.x + 0.5, current_position.y + 0.5}}, force = "player"}
        if #entities > 0 then
            error("Cannot place entity at position (" .. current_position.x .. ", " .. current_position.y .. ") due to overlapping "..entities[1].name..".")
        end

        -- Print current position vs target position

        local direction = {x = 0, y = 0}
        -- If we need to lay connection upwards first.
        if target_y < source_y then
            if target_y > current_position.y then
                direction.y = 1
            elseif target_y < current_position.y then
                direction.y = -1
            elseif target_x > current_position.x then
                direction.x = 1
            elseif target_x < current_position.x then
                direction.x = -1
            elseif target_x == current_position.x then
                direction.x = 0
            elseif target_y == current_position.y then
                direction.y = 0
            end
        else
            if target_x > current_position.x then
                direction.x = 1
            elseif target_x < current_position.x then
                direction.x = -1
            elseif target_y > current_position.y then
                direction.y = 1
            elseif target_y < current_position.y then
                direction.y = -1
            elseif target_x == current_position.x then
                direction.x = 0
            elseif target_y == current_position.y then
                direction.y = 0
            end
        end
        -- Place the connection entity
        local direction_to_next = {x = direction.x, y = direction.y}
        if i == distance then
            direction_to_next = {x = 0, y = 0}  -- The last entity should not point to any direction
        end

        --place_position = {x = math.floor(current_position.x), y = math.floor(current_position.y)}
        local placed_entity = game.surfaces[1].create_entity({name = connection_type, position = current_position, direction = get_direction(current_position, direction_to_next), force = player.force})
        game.print("Placed entity at position (" .. current_position.x .. ", " .. current_position.y .. ")")

        -- Serialize the entity and add it to the list
        local serialized = global.utils.serialize_entity(placed_entity)
        table.insert(serialized_entities, serialized)

        -- Remove the placed entity from the player's inventory
        player.remove_item({name = connection_type, count = 1})

        -- Move to the next position
        current_position.x = current_position.x + direction.x
        current_position.y = current_position.y + direction.y

        game.print("New position: (" .. current_position.x .. ", " .. current_position.y .. ")")
    end

    return serialized_entities
end
