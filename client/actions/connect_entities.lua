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

        if direction == defines.direction.north then
            edge_position.y = edge_position.y + entity_collision_box.right_bottom.y
        elseif direction == defines.direction.south then
            edge_position.y = edge_position.y + entity_collision_box.left_top.y
        elseif direction == defines.direction.east then
            edge_position.x = edge_position.x + entity_collision_box.left_top.x
        elseif direction == defines.direction.west then
            edge_position.x = edge_position.x + entity_collision_box.right_bottom.x
        end

        return edge_position
    end

    local current_position = get_edge_position(source_entity.position, source_collision_box, direction)

    local connector_prototype = game.entity_prototypes[connection_type]
    local connector_points = connector_prototype.electric_wire_connection_points
    local connector_length = 1

    if connector_points and #connector_points > 0 then
        connector_length = connector_points[1].max_wire_distance
    end

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
    local final_connector_position = {x = (current_position.x + target_position.x) / 2, y = (current_position.y + target_position.y) / 2}
    local can_build, colliding_entities = player.surface.can_place_entity{name=connection_type, force=player.force, position=final_connector_position, direction=direction, build_check_type=defines.build_check_type.script, forced=true}

    local target_entity = target_entities[1] -- Assuming the first entity is the correct one
    local can_build_final_connector = can_build or (#colliding_entities == 1 and colliding_entities[1].equals(target_entity))

    if can_build_final_connector then
        local placed_connector = player.surface.create_entity{name=connection_type, force=player.force, position=final_connector_position, direction=direction}

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