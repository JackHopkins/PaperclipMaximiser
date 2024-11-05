global.actions.nearest_buildable = function(player_index, entity_name, bounding_box)
    local player = game.get_player(player_index)
    rendering.clear()

    -- Get entity prototype once
    local entity_prototype = game.entity_prototypes[entity_name]

    -- Check if entity needs resources (has resource_categories)
    local needs_resources = entity_prototype.resource_categories ~= nil

    -- Function to check if all positions within a bounding box are buildable
    local function is_buildable_box(surface, origin, force, box_dimensions)
        -- Calculate actual corner positions relative to origin
        local actual_left_top = {
            x = origin.x + box_dimensions.left_top.x,
            y = origin.y + box_dimensions.left_top.y
        }
        local actual_right_bottom = {
            x = origin.x + box_dimensions.right_bottom.x,
            y = origin.y + box_dimensions.right_bottom.y
        }

        -- Basic water collision check
        local water_tiles = surface.count_tiles_filtered{
            area = {actual_left_top, actual_right_bottom},
            collision_mask = "water-tile"
        }

        if water_tiles > 0 then
            return false
        end


        -- Basic collision check
        local colliding_entities = surface.count_entities_filtered{
            area = {actual_left_top, actual_right_bottom},
            collision_mask = "object-layer"
        }

        if colliding_entities > 0 then
            return false
        end

        -- For miners, check if there are enough resources
        if needs_resources then
            local resource_count = surface.count_entities_filtered{
                area = {actual_left_top, actual_right_bottom},
                collision_mask = "resource-layer"
            }

            -- Area of the bounding box
            local width = actual_right_bottom.x - actual_left_top.x + 1
            local height = actual_right_bottom.y - actual_left_top.y + 1
            local area = width * height

            -- Check if resources cover the entire area
            if resource_count < area then
                return false
            end
        end

        return true, actual_left_top, actual_right_bottom
    end

    -- Function to find nearest position where the entire bounding box is buildable
    local function find_nearest_buildable_position(player, box_dimensions)
        local surface = player.surface
        local force = player.force
        local position = player.position
        local search_radius = 1
        local max_search_radius = 50
        local search_increment = 1

        -- If no bounding box provided, use single position check
        if not box_dimensions then
            while search_radius <= max_search_radius do
                for dx = -search_radius, search_radius, search_increment do
                    for dy = -search_radius, search_radius, search_increment do
                        local search_position = {x = position.x + dx, y = position.y + dy}

                        -- Check single position
                        local colliding = surface.count_entities_filtered{
                            area = {{search_position.x, search_position.y},
                                   {search_position.x + 1, search_position.y + 1}},
                            collision_mask = "object-layer"
                        }

                        if colliding == 0 and (not needs_resources or
                            surface.count_entities_filtered{
                                area = {{search_position.x, search_position.y},
                                       {search_position.x + 1, search_position.y + 1}},
                                collision_mask = "resource-layer"
                            } > 0) then
                            return search_position
                        end
                    end
                end
                search_radius = search_radius + search_increment
            end
        else
            -- Search with bounding box validation
            while search_radius <= max_search_radius do
                for dx = -search_radius, search_radius, search_increment do
                    for dy = -search_radius, search_radius, search_increment do
                        local search_position = {x = position.x + dx, y = position.y + dy}
                        local is_buildable, actual_left_top, actual_right_bottom =
                            is_buildable_box(surface, search_position, force, box_dimensions)

                        if is_buildable then
                            -- Draw the actual buildable area
                            rendering.draw_rectangle{
                                surface = player.surface,
                                left_top = actual_left_top,
                                right_bottom = actual_right_bottom,
                                filled = false,
                                color = {r=0, g=1, b=0, a=0.5}
                            }
                            return search_position
                        end
                    end
                end
                search_radius = search_radius + search_increment
            end
        end
        error("Could not find a buildable position for the entity: " .. entity_name)
    end

    return find_nearest_buildable_position(player, bounding_box)
end