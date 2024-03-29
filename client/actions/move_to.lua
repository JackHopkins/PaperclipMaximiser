--Move.lua
global.actions.move_to = function(player_index, offset_x, offset_y, trailing_entity, is_trailing)
    local player = game.players[player_index]
    local offset = {offset_x, offset_y}
    local trailing_entity = trailing_entity
    local is_trailing = is_trailing
    local surface = player.surface

    local function rotate_entity(entity, direction)
        entity.direction = direction
    end

    local function place(place_position, direction)
        if surface.can_place_entity{name=trailing_entity, position=place_position, direction=direction, force='player', build_check_type=defines.build_check_type.manual} then
            if player.get_item_count(trailing_entity) > 0 then
                local created = surface.create_entity{name=trailing_entity, position=place_position, direction=direction, force='player', player=player, build_check_type=defines.build_check_type.manual, fast_replace=true}
                if created then
                    player.remove_item({name=trailing_entity, count=1})
                end
            else
                error("No ".. trailing_entity .." in the inventory")
            end
        else
            error("Cannot place " ..trailing_entity)
        end
    end

    local function get_direction(offset)
        local direction = 0
        if offset[1] > 0 then
            direction = defines.direction.east
        elseif offset[1] < 0 then
            direction = defines.direction.west
        elseif offset[2] > 0 then
            direction = defines.direction.south
        elseif offset[2] < 0 then
            direction = defines.direction.north
        end
        return direction
    end


    local trailing_position = {x=player.position.x+0.5, y=player.position.y+0.5}
    local current_position = player.position

    if is_trailing == 1 or is_trailing == 0 then
        if game.entity_prototypes[trailing_entity] == nil then
            error('No entity exists that can be laid')
        end
    end

    if is_trailing == 1 then
        rcon.print('trailing')
        local existing_entity = surface.find_entity(trailing_entity, current_position)
        if existing_entity then
            rotate_entity(existing_entity, get_direction(offset))
        end

        player.teleport(offset[1], offset[2])
        place(trailing_position, get_direction(offset))
    elseif is_trailing == 0 then
        rcon.print('leading')
        local inverse_offset = {-offset[1], -offset[2]}
        trailing_position = {x=player.position.x-inverse_offset[1]-0.5, y=player.position.y-inverse_offset[2]-0.5}
        player.teleport(offset[1], offset[2])

        local existing_entity = surface.find_entity(trailing_entity, current_position)
        if existing_entity then
            rotate_entity(existing_entity, get_direction(offset))
        end
        place(trailing_position, get_direction(inverse_offset))
    else
        player.teleport(offset[1], offset[2])
    end

    return player.position
end