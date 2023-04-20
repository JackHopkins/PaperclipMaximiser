global.actions.place_entity = function(player_index, entity, direction, x, y)
    local player = game.players[player_index]
    local position = {x=x, y=y}

    if game.entity_prototypes[entity] == nil then
        name = entity:gsub(" ", "_"):gsub("-", "_")
        abort(name .. " isnt something that exists. Did you make a typo? ")
        return
    end

    local count = player.get_item_count(entity)

    if count == 0 then
        name = entity:gsub(" ", "_"):gsub("-", "_")
        abort("No ".. name .." in inventory.")
        return
    end

    local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
    local prototype = game.entity_prototypes[arg2]
    local collision_box = prototype.collision_box
    local width = math.abs(collision_box.right_bottom.x - collision_box.left_top.x)
    local height = math.abs(collision_box.right_bottom.y - collision_box.left_top.y)

    local function player_collision(player, target_area)
        local character_box = player.character.prototype.collision_box
        local character_area = {
            {player.position.x + character_box.left_top.x, player.position.y + character_box.left_top.y},
            {player.position.x + character_box.right_bottom.x, player.position.y + character_box.right_bottom.y}
        }
        return (character_area[1][1] < target_area[2][1] and character_area[2][1] > target_area[1][1]) and
                (character_area[1][2] < target_area[2][2] and character_area[2][2] > target_area[1][2])
    end

    local target_area = {
        {position.x - width / 2, position.y - height / 2},
        {position.x + width / 2, position.y + height / 2}
    }

    while player_collision(player, target_area) do
        player.teleport({player.position.x + width + 1, player.position.y}, player.surface)
    end

    local can_build = player.can_place_entity{name=entity, force=player.force, position=position, direction=cardinals[direction]}

    if can_build == false or can_build == 0 then
        local entities = player.surface.find_entities_filtered{area = target_area, type = "entity"}
        local blocking_entities = {}

        for _, blocking_entity in ipairs(entities) do
            local entity_box = blocking_entity.prototype.collision_box
            local entity_area = {
                {blocking_entity.position.x + entity_box.left_top.x, blocking_entity.position.y + entity_box.left_top.y},
                {blocking_entity.position.x + entity_box.right_bottom.x, blocking_entity.position.y + entity_box.right_bottom.y}
            }

            if (entity_area[1][1] < target_area[2][1] and entity_area[2][1] > target_area[1][1]) and
                    (entity_area[1][2] < target_area[2][2] and entity_area[2][2] > target_area[1][2]) then

                local name = blocking_entity.name
                local size = " with the size "..width
                table.insert(blocking_entities, name..size)
            end
        end
        if #blocking_entities > 0 then
            abort("Cant place there due to existing " .. table.concat(blocking_entities, "___"):gsub("-", "_") .. ", Need "..width.." space, Maybe inspect your surroundings.")
        else
            --local have_built = player.surface.create_entity{name=entity, force="player", position=position, direction=cardinals[direction], player=player}
            --if have_built then
            --    player.remove_item{name=entity, count=1}
            --    rcon.print(1)
            --else
            abort("Maybe inspect your surroundings before placing")
            --end
        end
    else
        local have_built = player.surface.create_entity{name=entity, force="player", position=position, direction=cardinals[direction], player=player}
        if have_built then
            player.remove_item{name=entity, count=1}
            rcon.print(dump({x= position.x, y = position.y}))
        end
    end
end