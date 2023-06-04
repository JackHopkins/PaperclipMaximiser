global.actions.place_entity_next_to = function(player_index, entity, ref_x, ref_y, direction, gap)
    --- Places an entity next to a reference entity:
    --- Find the reference entity at (ref_x, ref_y)
    --- If there is a reference entity, find the edge of the entity in the `direction`, take a step of size `gap` before placing the entity.
    --- If there is not a reference entity, take a step of size `gap` from the (ref_x, ref_y) position.
    --- Before placing the entity, check to see if an entity exists at this new position (If so, raise an `error`)
    --- If there is no error, place the entity and remove the item from the inventory.
    --- Return the resultant entity by calling the `global.utils.serialize_entity(new_entity)` method.
    ---
    --- @param player_index number
    --- @param entity string
    --- @param ref_x number
    --- @param ref_y number
    --- @param direction defines.direction
    --- @param gap number
    --- @return boolean
    ---
    local player = game.players[player_index]
    local ref_position = {x = ref_x, y = ref_y}
    local direction_map = {defines.direction.north, defines.direction.south, defines.direction.west, defines.direction.east}
    local entity_prototype = game.entity_prototypes[entity]
    -- local ref_entity = player.surface.find_entity(entity, ref_position)
    -- Find the reference entity at (ref_x, ref_y) with a bounding box of size (1, 1)
    local ref_entities = player.surface.find_entities_filtered({
        area = {
            {ref_x, ref_y},
            {ref_x + 1, ref_y + 1}
        }
    })
    local ref_entity = nil
    if #ref_entities > 0 then
        ref_entity = ref_entities[1]
    end

    game.print("ref_entity: " .. serpent.line(ref_entity))
    game.print("ref_position: " .. serpent.line(ref_position))
    local new_position = {x = ref_x, y = ref_y}
    local entity_size = {
        x = entity_prototype.tile_width,
        y = entity_prototype.tile_height
    }

    if ref_entity then
        --new_position = ref_entity.position
        local ref_bounding_box = ref_entity.prototype.collision_box
        local ref_size = {
            x = ref_bounding_box.right_bottom.x - ref_bounding_box.left_top.x,
            y = ref_bounding_box.right_bottom.y - ref_bounding_box.left_top.y
        }

        -- self.UP, self.ABOVE, self.TOP = 1
        -- self.RIGHT, self.EAST = 4
        -- self.LEFT, self.WEST = 3
        -- self.DOWN, self.BELOW, self.BOTTOM = 2

        if direction == 1 then
            new_position.y = new_position.y - ref_size.y - ( gap) -- entity_size.y
        elseif direction == 2 then
            new_position.y = new_position.y + ref_size.y + ( gap)
        elseif direction == 4 then
            new_position.x = new_position.x + ref_size.x + ( gap)
        else -- direction == defines.direction.west
            new_position.x = new_position.x - ref_size.x - ( gap)
        end
    else
        if direction == 1 then
            new_position.y = new_position.y - (1 + gap) -- entity_size.y
        elseif direction == 2 then
            new_position.y = new_position.y + (1 + gap)
        elseif direction == 4 then
            new_position.x = new_position.x + (1 + gap)
        else -- direction == defines.direction.west
            new_position.x = new_position.x - (1 + gap) - entity_size.x
        end
    end

    -- Check if there's an entity at the new position
    if player.surface.find_entity(entity, new_position) then
        error("An entity already exists at the new position " .. serpent.line(new_position) .. ".")
    end

    -- Check to see if can create the entity at the new position
    local can_build = player.surface.can_place_entity({
        name = entity,
        position = new_position,
        direction = direction_map[direction],
        force = player.force
    })
    if not can_build then
        error("Cannot place entity at the position " .. serpent.line(new_position) .. " with direction " .. serpent.line(direction) .. "." )
    end


    -- Place the entity and remove the item from the inventory
    local new_entity = player.surface.create_entity({
        name = entity,
        position = new_position,
        force = player.force,
        direction = direction_map[direction],
    })

    -- Remove the item from the player's inventory
    local item_stack = {name = entity, count = 1}
    if player.get_main_inventory().can_insert(item_stack) then
        player.get_main_inventory().remove(item_stack)
        -- Return the resultant entity
        return global.utils.serialize_entity(new_entity)
    else
        error("Not enough items in inventory.")
    end
end


global.actions.place_entity_next_to_8 = function(player_index, entity, ref_x, ref_y, direction, gap)
    --- Places an entity next to a reference entity.
    --- @param player_index number
    --- @param entity string
    --- @param ref_x number
    --- @param ref_y number
    --- @param direction defines.direction
    --- @param gap number
    --- @return boolean
    ---
    local player = game.players[player_index]
    local ref_position = {x = ref_x, y = ref_y}
    local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
    local entity_prototype = game.entity_prototypes[entity]

    local function clear_items(surface, area)
        local items = surface.find_entities_filtered{area = area, type = "item-entity"}
        for _, item in pairs(items) do
            item.destroy()
        end
    end

    local surface = player.surface
    local ref_entities = player.surface.find_entities_filtered{area = {{ref_position.x - 0.5, ref_position.y - 0.5}, {ref_position.x + 0.5, ref_position.y + 0.5}}}
    -- local ref_entities = player.surface.find_entities_filtered{name=entity, position=ref_position, radius=2}
    local ref_entity = ref_entities[1]
    local target_position

    if ref_entity then
        local ref_bb = ref_entity.prototype.selection_box
        local entity_bb = entity_prototype.selection_box
        local dx, dy
        local ref_height = ref_bb.right_bottom.y - ref_bb.left_top.y
        local ref_width = ref_bb.right_bottom.x - ref_bb.left_top.x
        game.print("ref_height: " .. ref_height)
        game.print("ref_width: " .. ref_width)
        game.print("ref_tile_width: " .. ref_entity.prototype.tile_width)
        game.print("ref_tile_height: " .. ref_entity.prototype.tile_height)

        --- THIS HAS A BUG IN IT
        if direction == 1 then -- North
            dx = 0
            dy = -(ref_bb.right_bottom.y - ref_bb.left_top.y + entity_bb.right_bottom.y - entity_bb.left_top.y - ref_entity.prototype.tile_height/2 + gap)
        elseif direction == 2 then -- South
            dx = 0
            dy = (ref_bb.right_bottom.y - ref_bb.left_top.y + entity_bb.right_bottom.y - entity_bb.left_top.y - ref_entity.prototype.tile_height/2 + gap + (1-ref_height))
        elseif direction == 3 then -- East
            dx = (ref_bb.right_bottom.x - ref_bb.left_top.x + entity_bb.right_bottom.x - entity_bb.left_top.x -  ref_entity.prototype.tile_width/2 + gap + (1-ref_width))
            dy = 0
        else -- West
            dx = -(ref_bb.right_bottom.x - ref_bb.left_top.x + entity_bb.right_bottom.x - entity_bb.left_top.x - ref_entity.prototype.tile_width/2 + gap)
            dy = 0
        end
        ---

    if direction == 1 then -- North
        dx = 0
        dy = -(ref_height / 2 + entity_bb.right_bottom.y - entity_bb.left_top.y / 2 + gap)
    elseif direction == 2 then -- South
        dx = 0
        dy = ref_height / 2 + entity_bb.right_bottom.y - entity_bb.left_top.y / 2 + gap
    elseif direction == 3 then -- East
        dx = ref_width / 2 + entity_bb.right_bottom.x - entity_bb.left_top.x / 2 + gap
        dy = 0
    else -- West
        dx = -(ref_width / 2 + entity_bb.right_bottom.x - entity_bb.left_top.x / 2 + gap)
        dy = 0
    end


        target_position = {x = ref_x + dx, y = ref_y + dy}

        game.print("dx: " .. dx)
        game.print("dy: " .. dy)
        game.print("ref_x: " .. ref_x)
        game.print("ref_y: " .. ref_y)
        game.print("target_position.x: " .. target_position.x)
        game.print("target_position.y: " .. target_position.y)
    else

        local direction_vector = {
            [1] = {x = 0, y = -gap - entity_prototype.selection_box.right_bottom.y},
            [2] = {x = 0, y = gap + entity_prototype.selection_box.right_bottom.y},
            [3] = {x = gap + entity_prototype.selection_box.right_bottom.x, y = 0},
            [4] = {x = -gap - entity_prototype.selection_box.right_bottom.x, y = 0},
        }

        target_position = {x = ref_x + direction_vector[direction].x, y = ref_y + direction_vector[direction].y}
    end

    local target_area = {
        left_top = {x = target_position.x + entity_prototype.selection_box.left_top.x, y = target_position.y + entity_prototype.selection_box.left_top.y},
        right_bottom = {x = target_position.x + entity_prototype.selection_box.right_bottom.x, y = target_position.y + entity_prototype.selection_box.right_bottom.y}
    }

    clear_items(surface, target_area)

    if surface.count_entities_filtered{area = target_area, name = entity} > 0 then
        error("There is an existing entity in the target position.")
    end
    local can_build = player.surface.can_place_entity{name=entity, force=player.force, position=target_position, direction = direction}
    if can_build then
        local new_entity = surface.create_entity{name = entity, position = target_position, direction = direction, force = player.force}
        player.remove_item{name=entity, count=1}
        local serialized = global.utils.serialize_entity(new_entity)
        local entity_json = game.table_to_json(serialized)-- game.table_to_json(entity)
        game.print(dump(entity_json))
        return serialized
    else
        error("There is an existing entity in the target position.")
    end
end


global.actions.place_entity_next_to_6 = function(player_index, entity, ref_x, ref_y, direction, gap)
    local function clear_items_inside_area(surface, area)
        local items = surface.find_entities_filtered{area = area, type = "item-entity"}
        for _, item in ipairs(items) do
            item.destroy()
        end
    end

    local player = game.players[player_index]
    local ref_position = {x = ref_x, y = ref_y}
    local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
    local entity_prototype = game.entity_prototypes[entity]
    local collision_box = entity_prototype.collision_box
    local width = math.abs(collision_box.right_bottom.x - collision_box.left_top.x)
    local height = math.abs(collision_box.right_bottom.y - collision_box.left_top.y)

    local existing_entities = player.surface.find_entities_filtered{area = {{ref_position.x - 0.25, ref_position.y - 0.25}, {ref_position.x + 0.25, ref_position.y + 0.25}}}
    local existing_entity = existing_entities[1]
    local existing_height = 0
    local existing_width = 0
    local tile_height = 0
    local tile_width = 0
    if existing_entity then
        local existing_collision_box = existing_entity.prototype.collision_box
        existing_width = math.abs(existing_collision_box.right_bottom.x - existing_collision_box.left_top.x)
        existing_height = math.abs(existing_collision_box.right_bottom.y - existing_collision_box.left_top.y)
        --width = width + existing_width
        --height = height + existing_height
        tile_height = existing_entity.prototype.tile_height
        tile_width = existing_entity.prototype.tile_width

        -- Correct reference position to be the centroid of the existing entity
        ref_position.x = existing_entity.position.x + tile_width-- math.floor(width/2)
        ref_position.y = existing_entity.position.y + tile_height--math.floor(height/2)


    end

    local target_position = {x = ref_position.x, y = ref_position.y}


    if direction == 1 then
        target_position.y = target_position.y - (gap  + (2-tile_height))-- +1
    elseif direction == 2 then
        target_position.y = target_position.y + (gap )
    elseif direction == 3 then
        target_position.x = target_position.x + (gap)
    else
        target_position.x = target_position.x - (gap + (2-tile_width))-- +1
    end

    local orientation = cardinals[direction]

    local area = {{target_position.x - width / 2, target_position.y - height / 2}, {target_position.x + width / 2, target_position.y + height / 2}}
    clear_items_inside_area(player.surface, area)

    local can_build = player.surface.can_place_entity{name=entity, force=player.force, position=target_position, direction=orientation}
    if can_build then
        local placed_entity = player.surface.create_entity{name=entity, force=player.force, position=target_position, direction=orientation}
        if placed_entity then
            player.remove_item{name=entity, count=1}
            return {x=target_position.x, y=target_position.y}
        else
            error("\"Cannot place here, although I thought I could. Please check your entity or position.\"")
        end
    else
        local colliding_entities = player.surface.find_entities_filtered{area = {{target_position.x - width / 2, target_position.y - height / 2}, {target_position.x + width / 2, target_position.y + height / 2}}}
        local collision_info = ""

        for _, colliding_entity in ipairs(colliding_entities) do
            collision_info = collision_info .. "\nEntity: " .. colliding_entity.name .. ", Position: x=" .. colliding_entity.position.x .. ", y=" .. colliding_entity.position.y
        end

        if collision_info == "" then
            error("\"Cannot place here. Entity: " .. entity .. " at target position: x=" .. target_position.x .. ", y=" .. target_position.y.."\"")
        else
            error("\"Cannot place here due to collision with the following entities:" .. collision_info.."\"")
        end
    end
    error("Something went wrong")
end

global.actions.place_entity_next_to_7 = function(player_index, entity, ref_x, ref_y, direction, gap)
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
        ref_position.x = existing_entity.position.x + existing_width / 2
        ref_position.y = existing_entity.position.y + existing_height / 2
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
            game.print(dump(entity))
            return {x=target_position.x, y=target_position.y}

        else
            error("\"Cannot place here, although I thought I could.\"")
        end
    else
        error("\"Cannot place here.\"")
    end
end
