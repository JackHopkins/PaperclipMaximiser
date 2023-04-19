local function place_entity_next_to(player_index, entity, ref_x, ref_y, direction, gap)
    local player = game.players[player_index]
    local ref_position = {x = ref_x, y = ref_y}
    local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
    local entity_prototype = game.entity_prototypes[entity]
    local collision_box = entity_prototype.collision_box
    local width = math.abs(collision_box.right_bottom.x - collision_box.left_top.x)
    local height = math.abs(collision_box.right_bottom.y - collision_box.left_top.y)

    local existing_entities = player.surface.find_entities_filtered{area = {{ref_position.x - 0.1, ref_position.y - 0.1}, {ref_position.x + 0.1, ref_position.y + 0.1}}}
    local existing_entity = existing_entities[1]

    if existing_entity then
        local existing_collision_box = existing_entity.prototype.collision_box
        local existing_width = math.abs(existing_collision_box.right_bottom.x - existing_collision_box.left_top.x)
        local existing_height = math.abs(existing_collision_box.right_bottom.y - existing_collision_box.left_top.y)
        width = width + existing_width
        height = height + existing_height

        -- Correct reference position to be the centroid of the existing entity
        ref_position.x = existing_entity.position.x --+ existing_width / 2
        ref_position.y = existing_entity.position.y --+ existing_height / 2
    end

    local target_position = {x = ref_position.x, y = ref_position.y}
    if direction == 0 then
        target_position.y = target_position.y - gap - height / 2
    elseif direction == 1 then
        target_position.y = target_position.y + gap + height / 2
    elseif direction == 2 then
        target_position.x = target_position.x + gap + width / 2
    else
        target_position.x = target_position.x - gap - width / 2
    end

    if ref_position.y > target_position.y then
        orientation = defines.direction.south
    elseif ref_position.y < target_position.y then
        orientation = defines.direction.north
    elseif ref_position.x < target_position.x then
        orientation = defines.direction.west
    else
        orientation = defines.direction.east
    end

    local can_build = player.surface.can_place_entity{name=entity, force=player.force, position=target_position, direction=orientation}
    if can_build then
        local placed_entity = player.surface.create_entity{name=entity, force=player.force, position=target_position, direction=orientation}
        if placed_entity then
            player.remove_item{name=entity, count=1}
            rcon.print(dump({x=target_position.x, y=target_position.y}))

        else
            abort("Cannot place here, although I thought I could.")
        end
    else
        abort("Cannot place here.")
    end

end
place_entity_next_to(arg1, arg2, arg3, arg4, arg5, arg6)
