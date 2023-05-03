global.actions.connect_entities = function(player_index, source_x, source_y, target_x, target_y, connection_type)
    local player = game.players[player_index]
    local source_position = {x = source_x, y = source_y}
    local target_position = {x = target_x, y = target_y}

    local source_entities = player.surface.find_entities_filtered{area = {{source_position.x - 0.25, source_position.y - 0.25}, {source_position.x + 0.25, source_position.y + 0.25}}}
    local target_entities = player.surface.find_entities_filtered{area = {{target_position.x - 0.25, target_position.y - 0.25}, {target_position.x + 0.25, target_position.y + 0.25}}}

    if #source_entities == 0 then
        error("Source entity not found.")
    end
    if #target_entities == 0 then
        error("Target entity not found.")
    end

    local is_vertical
    local function get_direction(source_position, target_position)
        if math.abs(source_position.y - target_position.y) > math.abs(source_position.x - target_position.x) then
            is_vertical = true
            if source_position.y > target_position.y then
                direction = defines.direction.south
            else
                direction = defines.direction.north
            end
        else
            is_vertical = false
            if source_position.x > target_position.x then
                direction = defines.direction.west
            else
                direction = defines.direction.east
            end
        end
        return direction
    end


    local direction = get_direction(source_position, target_position)
    local source_entity = source_entities[1] -- Assuming the first entity is the correct one
    local source_collision_box = source_entity.prototype.collision_box

    local function get_edge_position(entity_position, entity_collision_box, direction)
        local edge_position = {x = entity_position.x, y = entity_position.y}

        local height = entity_collision_box.left_top.y - entity_collision_box.right_bottom.y
        game.print(height)
        if direction == defines.direction.north then
            edge_position.y = edge_position.y + entity_collision_box.right_bottom.y - height/2
        elseif direction == defines.direction.south then
            edge_position.y = edge_position.y + entity_collision_box.left_top.y - height/2
        elseif direction == defines.direction.east then
            edge_position.x = edge_position.x + entity_collision_box.left_top.x
        elseif direction == defines.direction.west then
            edge_position.x = edge_position.x + entity_collision_box.right_bottom.x
        end

        return edge_position
    end
    local function calculate_direction_vector(src, tgt)
        local dx = tgt.x - src.x
        local dy = tgt.y - src.y
        local magnitude = math.sqrt(dx * dx + dy * dy)
        return {x = dx / magnitude, y = dy / magnitude}
    end

    local function calculate_distance(src, tgt)
        local dx = tgt.x - src.x
        local dy = tgt.y - src.y
        return math.sqrt(dx * dx + dy * dy)
    end

    local function opposite_direction(dir)
        game.print(dir)
        if dir == 2 then
            return defines.direction.west
        elseif dir == 6 then
            return defines.direction.east
        elseif dir == 0 then
            return defines.direction.south
        end

        return defines.direction.north
    end

    local function calculate_direction(pos1, pos2)
        local dx = pos2.x - pos1.x
        local dy = pos2.y - pos1.y

        if math.abs(dx) > math.abs(dy) then
            if dx > 0 then
                return defines.direction.east
            else
                return defines.direction.west
            end
        else
            if dy > 0 then
                return defines.direction.south
            else
                return defines.direction.north
            end
        end
    end

    function direction_to_vector(direction)
        if direction == defines.direction.north then
            return {x = 0, y = -1}
        elseif direction == defines.direction.east then
            return {x = 1, y = 0}
        elseif direction == defines.direction.south then
            return {x = 0, y = 1}
        elseif direction == defines.direction.west then
            return {x = -1, y = 0}
        end
    end

    function find_belt_placement_directions_jagged(source_position, target_position, increments)
        local direction_vector = calculate_direction_vector(source_position, target_position)
        local distance = calculate_distance(target_position, source_position)
        local steps = math.floor(distance)*1.4*increments

        local directions = {}
        --local current_position = {x = source_position.x-direction_vector.x/increments, y = source_position.y-direction_vector.y/increments}
        local current_position = {x = source_position.x- direction_vector.x/increments, y = source_position.y- direction_vector.y/increments}

        for i = 0, steps do
            local possible_directions = {
                {direction = defines.direction.north, vector = {x = 0, y = -1}},
                {direction = defines.direction.east, vector = {x = 1, y = 0}},
                {direction = defines.direction.south, vector = {x = 0, y = 1}},
                {direction = defines.direction.west, vector = {x = -1, y = 0}},
            }

            local best_direction
            local best_distance = math.huge
            for _, possible_direction in ipairs(possible_directions) do
                local next_position = {
                    x = current_position.x + possible_direction.vector.x/increments,
                    y = current_position.y + possible_direction.vector.y/increments,
                }
                local next_distance = calculate_distance(target_position, next_position)
                if next_distance <= best_distance then
                    best_direction = possible_direction
                    best_distance = next_distance
                end
            end

            table.insert(directions, best_direction)
            local direction_vector = direction_to_vector(best_direction.direction)
            current_position.x = current_position.x + direction_vector.x/increments
            current_position.y = current_position.y + direction_vector.y/increments
        end

        return directions
    end

    local current_position = get_edge_position(source_entity.position, source_collision_box, direction)
    local distance = calculate_distance(source_position, target_position)

    local connector_prototype = game.entity_prototypes[connection_type]
    local connector_length = 1

    if connector_prototype.type == "electric-pole" then
        local copper_wire_prototype = game.item_prototypes["copper-cable"]
        connector_length = copper_wire_prototype and copper_wire_prototype.max_wire_distance or 1
    elseif connector_prototype.type == "inserter" then
        if distance > 3 then
            local direction_vector = calculate_direction_vector(source_position, target_position)
            local belt_name = 'transport-belt' -- Change to the desired transport belt type

            local source_entity
            local is_source_drill = false
            if #source_entities > 0 then
                source_entity = source_entities[1]
                is_source_drill = source_entity.type == "mining-drill"
            end

            -- Create terminal inserters
            local target_inserter_position = {
                x = target_position.x,-- - direction_vector.x * connector_length,
                y = target_position.y-- - direction_vector.y * connector_length
            }
            local can_build = false
            -- Look for a place to build a target inserter
            while not can_build do
                target_inserter_position.x = target_inserter_position.x - direction_vector.x /4
                can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=target_inserter_position, direction=direction}
                if can_build then
                    break
                end
                target_inserter_position.y = target_inserter_position.y - direction_vector.y /4
                can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=target_inserter_position, direction=direction}
            end
            local target_direction = opposite_direction(calculate_direction(target_inserter_position, target_position))
            local target_inserter = player.surface.create_entity{name = connection_type, position = target_inserter_position, force = player.force, direction = target_direction}

            local belt_end_position = {x=target_inserter.position.x + (target_inserter.pickup_position.x-target_inserter.position.x)/2,
                                         y=target_inserter.position.y + (target_inserter.pickup_position.y-target_inserter.position.y)/2}

            -- Look for a place to build a source inserter
            local can_build = false
            local belt_start_position
            if not is_source_drill then
                local source_inserter_position = {
                    x = source_position.x + direction_vector.x * connector_length,
                    y = source_position.y + direction_vector.y * connector_length,
                }

                can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=source_inserter_position, direction=direction}
                while not can_build do
                    source_inserter_position.x = source_inserter_position.x + direction_vector.x/4
                    can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=source_inserter_position, direction=direction}
                    if can_build then
                        break
                    end
                    source_inserter_position.y = source_inserter_position.y + direction_vector.y/4
                    can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=source_inserter_position, direction=direction}
                end
                local source_direction = calculate_direction(source_inserter_position, source_position)

                local source_inserter = player.surface.create_entity{name = connection_type, position = source_inserter_position, force = player.force, direction = source_direction}
                can_build = false
                belt_start_position = {x=source_inserter.position.x + (source_inserter.drop_position.x-source_inserter.position.x)/2,
                                       y=source_inserter.position.y + (source_inserter.drop_position.y-source_inserter.position.y)/2}
            else
                -- Rotate the drill to the orientation that ensures the nearest drop_position to belt_end_position
                local closest_direction, closest_distance
                for _, direction in ipairs({defines.direction.north, defines.direction.east, defines.direction.south, defines.direction.west}) do
                    source_entity.direction = direction
                    local drop_position = source_entity.drop_position
                    local distance = calculate_distance(drop_position, belt_end_position)
                    if not closest_distance or distance < closest_distance then
                        closest_distance = distance
                        closest_direction = direction
                    end
                end
                source_entity.direction = closest_direction
                belt_start_position = source_entity.drop_position
            end

            local increments = 4
            local belt_sequence = find_belt_placement_directions_jagged(belt_start_position, belt_end_position, increments)
            local current_position = {x = belt_start_position.x, y = belt_start_position.y}

            for i, belt_direction in ipairs(belt_sequence) do
                local direction_vector = belt_direction.vector

                local adjusted_position = {
                    x = math.floor(current_position.x) + direction_vector.x/increments + 0.5,
                    y = math.floor(current_position.y) + direction_vector.y/increments + 0.5,
                }

                local can_build = player.surface.can_place_entity{name=belt_name, force=player.force, position=adjusted_position, direction=belt_direction.direction}
                if can_build then
                    player.surface.create_entity{name = belt_name, position = adjusted_position, force = player.force, direction = belt_direction.direction}
                end
                -- Move the current position in the direction of the belt
                current_position.x = current_position.x + direction_vector.x/increments
                current_position.y = current_position.y + direction_vector.y/increments

                local distance = calculate_distance(current_position, belt_end_position)
                if distance < 0.1 then
                    local next_position = {
                        x=current_position.x + direction_vector.x,
                        y=current_position.y + direction_vector.y
                    }
                    local can_build = player.surface.can_place_entity{name=belt_name, force=player.force, position=next_position, direction=belt_direction.direction}
                    if can_build then
                        player.surface.create_entity{name = belt_name, position = next_position, force = player.force, direction = belt_direction.direction}
                        break
                    end

                end
            end
            return 1
        else
            connector_length = 2
        end
    else
        error("Unsupported connection type.")
    end

    if connector_prototype.type ~= "inserter" then
        while (is_vertical and math.abs(current_position.y - target_position.y) > connector_length) or (not is_vertical and math.abs(current_position.x - target_position.x) > connector_length) do
            if is_vertical then
                current_position.y = current_position.y + (direction == defines.direction.north and connector_length or -connector_length)
            else
                current_position.x = current_position.x + (direction == defines.direction.east and connector_length or -connector_length)
            end

            local can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=current_position, direction=direction}

            if can_build then
                local placed_connector = player.surface.create_entity{name=connection_type, force=player.force, position=current_position, direction=direction}
                if placed_connector then
                    player.remove_item{name=connection_type, count=1}
                else
                    error("Cannot place connector, although I thought I could.")
                end
            else
                error("Cannot place connector here.")
            end
        end

        -- Connect to the target entity
        local final_connector_position = is_vertical and
                {x = current_position.x, y = (current_position.y + target_position.y) / 2} or
                {x = (current_position.x + target_position.x) / 2, y = current_position.y}

        local can_build, colliding_entities = player.surface.can_place_entity{
            name=connection_type,
            force=player.force,
            position=final_connector_position,
            direction=direction,
            build_check_type=defines.build_check_type.script,
            forced=true
        }

        local target_entity = target_entities[1] -- Assuming the first entity is the correct one
        local can_build_final_connector = can_build or (#colliding_entities == 1 and colliding_entities[1].equals(target_entity))

        if can_build_final_connector then
            local placed_connector = player.surface.create_entity{
                name=connection_type,
                force=player.force,
                position=final_connector_position - direction_vector.x,
                direction=direction
            }

            if placed_connector then
                player.remove_item{name=connection_type, count=1}
                return 1
            else
                error("Cannot place final connector, although I thought I could.")
            end
        else
            error("Cannot place final connector here.")
        end

    end

    game.print("Placed "..connection_type.." at "..serpent.block(final_connector_position))
end

global.actions.connect_entities_2 = function(player_index, source_x, source_y, target_x, target_y, connection_type)
    local player = game.players[player_index]
    local source_position = {x = source_x, y = source_y}
    local target_position = {x = target_x, y = target_y}

    local source_entities = player.surface.find_entities_filtered{area = {{source_position.x - 0.25, source_position.y - 0.25}, {source_position.x + 0.25, source_position.y + 0.25}}}
    local target_entities = player.surface.find_entities_filtered{area = {{target_position.x - 0.25, target_position.y - 0.25}, {target_position.x + 0.25, target_position.y + 0.25}}}

    if #source_entities == 0 then
        error("Source entity not found.")
    end
    if #target_entities == 0 then
        error("Target entity not found.")
    end

    local direction
    local is_vertical

    if math.abs(source_position.y - target_position.y) > math.abs(source_position.x - target_position.x) then
        is_vertical = true
        if source_position.y > target_position.y then
            direction = defines.direction.south
        else
            direction = defines.direction.north
        end
    else
        is_vertical = false
        if source_position.x > target_position.x then
            direction = defines.direction.west
        else
            direction = defines.direction.east
        end
    end

    local source_entity = source_entities[1] -- Assuming the first entity is the correct one
    local source_collision_box = source_entity.prototype.collision_box

    local function get_edge_position(entity_position, entity_collision_box, direction)
        local edge_position = {x = entity_position.x, y = entity_position.y}

        local height = entity_collision_box.left_top.y - entity_collision_box.right_bottom.y
        game.print(height)
        if direction == defines.direction.north then
            edge_position.y = edge_position.y + entity_collision_box.right_bottom.y - height/2
        elseif direction == defines.direction.south then
            edge_position.y = edge_position.y + entity_collision_box.left_top.y - height/2
        elseif direction == defines.direction.east then
            edge_position.x = edge_position.x + entity_collision_box.left_top.x
        elseif direction == defines.direction.west then
            edge_position.x = edge_position.x + entity_collision_box.right_bottom.x
        end

        return edge_position
    end
    local function calculate_direction_vector(src, tgt)
        local dx = tgt.x - src.x
        local dy = tgt.y - src.y
        local magnitude = math.sqrt(dx * dx + dy * dy)
        return {x = dx / magnitude, y = dy / magnitude}
    end

    local function calculate_distance(src, tgt)
        local dx = tgt.x - src.x
        local dy = tgt.y - src.y
        return math.sqrt(dx * dx + dy * dy)
    end
    local function calculate_direction(src, tgt)
        local dx = tgt.x - src.x
        local dy = tgt.y - src.y

        if math.abs(dy) > math.abs(dx) then
            return dy > 0 and defines.direction.north or defines.direction.south
        else
            return dx < 0 and defines.direction.east or defines.direction.west
        end
    end

    local function opposite_direction(dir)
        game.print(dir)
        if dir == 2 then
            return defines.direction.west
        elseif dir == 6 then
            return defines.direction.east
        elseif dir == 0 then
            return defines.direction.south
        end

        return defines.direction.north
    end

    local current_position = get_edge_position(source_entity.position, source_collision_box, direction)
    local distance = calculate_distance(source_position, target_position)


    local connector_prototype = game.entity_prototypes[connection_type]
    local connector_length = 1

    if connector_prototype.type == "electric-pole" then
        local copper_wire_prototype = game.item_prototypes["copper-cable"]
        connector_length = copper_wire_prototype and copper_wire_prototype.max_wire_distance or 1
    elseif connector_prototype.type == "inserter" then
        if distance > 3 then
            local direction_vector = calculate_direction_vector(source_position, target_position)
            local belt_direction = calculate_direction(source_position, target_position)
            local belt_name = 'transport-belt' -- Change to the desired transport belt type

            -- Create terminal inserters
            local source_inserter_position = {
                x = source_position.x + direction_vector.x*connector_length,
                y = source_position.y + direction_vector.y*connector_length,
            }
            local target_inserter_position = {
                x = target_position.x - direction_vector.x*connector_length,
                y = target_position.y - direction_vector.y*connector_length
            }
            local can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=source_inserter_position, direction=direction}
            while not can_build do
                    source_inserter_position.x = source_inserter_position.x + direction_vector.x/2
                    source_inserter_position.y = source_inserter_position.y + direction_vector.y/2
                    can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=source_inserter_position, direction=direction}
            end
            local source_inserter = player.surface.create_entity{name = connection_type, position = source_inserter_position, force = player.force, direction = belt_direction}
            local target_inserter = player.surface.create_entity{name = connection_type, position = target_inserter_position, force = player.force, direction = belt_direction}

            -- Set pickup and drop positions for terminal inserters
            source_inserter.pickup_position = source_entity.position
            source_inserter.drop_position = {x = source_inserter_position.x + direction_vector.x, y = source_inserter_position.y + direction_vector.y}
            target_inserter.pickup_position = {x = target_inserter_position.x - direction_vector.x, y = target_inserter_position.y - direction_vector.y}
            target_inserter.drop_position = target_position

            -- Create transport belts between terminal inserters
            local current_position = {
                x = source_inserter_position.x + direction_vector.x,
                y = source_inserter_position.y + direction_vector.y
            }

            while calculate_distance(current_position, target_inserter_position) > 1 do
                local can_build = player.surface.can_place_entity{name=belt_name, force=player.force, position=current_position, direction=direction}
                if can_build then
                    player.surface.create_entity{name = belt_name, position = current_position, force = player.force, direction = belt_direction}
                end
                current_position.x = current_position.x + direction_vector.x/2

                local can_build = player.surface.can_place_entity{name=belt_name, force=player.force, position=current_position, direction=direction}
                if can_build then
                    player.surface.create_entity{name = belt_name, position = current_position, force = player.force, direction = opposite_direction(belt_direction)}
                end
                current_position.y = current_position.y + direction_vector.y/2


            end
            return 1
        else
            connector_length = 2
        end
    else
        error("Unsupported connection type.")
    end

    if connector_prototype.type ~= "inserter" then
        while (is_vertical and math.abs(current_position.y - target_position.y) > connector_length) or (not is_vertical and math.abs(current_position.x - target_position.x) > connector_length) do
            if is_vertical then
                current_position.y = current_position.y + (direction == defines.direction.north and connector_length or -connector_length)
            else
                current_position.x = current_position.x + (direction == defines.direction.east and connector_length or -connector_length)
            end

            local can_build = player.surface.can_place_entity{name=connection_type, force=player.force, position=current_position, direction=direction}

            if can_build then
                local placed_connector = player.surface.create_entity{name=connection_type, force=player.force, position=current_position, direction=direction}
                if placed_connector then
                    player.remove_item{name=connection_type, count=1}
                else
                    error("Cannot place connector, although I thought I could.")
                end
            else
                error("Cannot place connector here.")
            end
        end

        -- Connect to the target entity
        local final_connector_position = is_vertical and
                {x = current_position.x, y = (current_position.y + target_position.y) / 2} or
                {x = (current_position.x + target_position.x) / 2, y = current_position.y}

        local can_build, colliding_entities = player.surface.can_place_entity{
            name=connection_type,
            force=player.force,
            position=final_connector_position,
            direction=direction,
            build_check_type=defines.build_check_type.script,
            forced=true
        }

        local target_entity = target_entities[1] -- Assuming the first entity is the correct one
        local can_build_final_connector = can_build or (#colliding_entities == 1 and colliding_entities[1].equals(target_entity))

        if can_build_final_connector then
            local placed_connector = player.surface.create_entity{
                name=connection_type,
                force=player.force,
                position=final_connector_position - direction_vector.x,
                direction=direction
            }

            if placed_connector then
                player.remove_item{name=connection_type, count=1}
                return 1
            else
                error("Cannot place final connector, although I thought I could.")
            end
        else
            error("Cannot place final connector here.")
        end

    end

    game.print("Placed "..connection_type.." at "..serpent.block(final_connector_position))
end