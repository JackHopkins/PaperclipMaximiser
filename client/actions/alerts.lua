global.alerts = {}

-- Define a function to check if the transport belt is blocked
local function is_transport_belt_blocked(entity)
    if entity.type == "transport-belt" then
        local line_1 = entity.get_transport_line(1)
        local line_2 = entity.get_transport_line(2)

        local direction_vector = {
            [0] = {x = 0, y = -1},  -- North
            [2] = {x = 1, y = 0},   -- East
            [4] = {x = 0, y = 1},   -- South
            [6] = {x = -1, y = 0},  -- West
        }

        local dx = direction_vector[entity.direction].x
        local dy = direction_vector[entity.direction].y
        local next_position = {x = entity.position.x + dx, y = entity.position.y + dy}
        local next_entities = entity.surface.find_entities_filtered {
            area = {{next_position.x - 0.5, next_position.y - 0.5}, {next_position.x + 0.5, next_position.y + 0.5}},
        }

        local has_sink = false
        for _, next_entity in ipairs(next_entities) do
            if next_entity.type == "transport-belt" or next_entity.type == "splitter" or next_entity.type == "loader" or (next_entity.type == "assembling-machine" and next_entity.get_recipe()) then
                has_sink = true
                break
            end
        end

        if not has_sink then
            local line_1_moving = line_1 and line_1.get_contents() and not line_1.can_insert_at_back()
            local line_2_moving = line_2 and line_2.get_contents() and not line_2.can_insert_at_back()

            if line_1_moving or line_2_moving then
                return true
            end
        end
    end
    return false
end

-- Define a function to check if the transport belt is blocked
local function is_transport_belt_blocked_5(entity)
    if entity.type == "transport-belt" then
        local line_1 = entity.get_transport_line(1)
        local line_2 = entity.get_transport_line(2)

        local line_1_blocked = line_1 and not line_1.can_insert_at_back()
        local line_2_blocked = line_2 and not line_2.can_insert_at_back()

        if line_1_blocked or line_2_blocked then
            local direction_vector = {
                [0] = {x = 0, y = -1},  -- North
                [2] = {x = 1, y = 0},   -- East
                [4] = {x = 0, y = 1},   -- South
                [6] = {x = -1, y = 0},  -- West
            }

            local dx = direction_vector[entity.direction].x
            local dy = direction_vector[entity.direction].y
            local next_position = {x = entity.position.x + dx, y = entity.position.y + dy}
            local next_belts = entity.surface.find_entities_filtered {
                area = {{next_position.x - 0.5, next_position.y - 0.5}, {next_position.x + 0.5, next_position.y + 0.5}},
                type = "transport-belt"
            }

            if #next_belts == 0 then

                local is_moving = false
                for name, count in pairs(line_1.get_contents()) do
                    if count > 0 then
                        is_moving = true
                        break
                    end
                end

                if not is_moving then
                    for name, count in pairs(line_2.get_contents()) do
                        if count > 0 then
                            is_moving = true
                            break
                        end
                    end
                end
                game.print("Blocked belt: "..tostring(is_moving))
                if not is_moving then
                    return true
                end
            end
        end
    end
    return false
end
-- Define a function to check if the transport belt is blocked
local function is_transport_belt_blocked_4(entity)
    if entity.type == "transport-belt" then
        local line_1 = entity.get_transport_line(1)
        local line_2 = entity.get_transport_line(2)

        if line_1 and line_2 and not line_1.can_insert_at_back() and not line_2.can_insert_at_back() then
            local direction_vector = {
                [0] = {x = 0, y = -1},  -- North
                [2] = {x = 1, y = 0},   -- East
                [4] = {x = 0, y = 1},   -- South
                [6] = {x = -1, y = 0},  -- West
            }
            game.print("Transport belt blocked")
            local dx = direction_vector[entity.direction].x
            local dy = direction_vector[entity.direction].y
            local next_position = {x = entity.position.x + dx, y = entity.position.y + dy}
            local next_belts = entity.surface.find_entities_filtered {
                area = {{next_position.x - 0.5, next_position.y - 0.5}, {next_position.x + 0.5, next_position.y + 0.5}},
                type = "transport-belt"
            }

            if #next_belts == 0 then
                local is_moving = false
                for name, count in pairs(line_1.get_contents()) do
                    if count > 0 then
                        is_moving = true
                        break
                    end
                end

                if not is_moving then
                    for name, count in pairs(line_2.get_contents()) do
                        if count > 0 then
                            is_moving = true
                            break
                        end
                    end
                end

                if not is_moving then
                    return true
                end
            end
        end
    end
    return false
end

-- Define a function to check if the transport belt is blocked
local function is_transport_belt_blocked_3(entity)
    if entity.type == "transport-belt" then
        local belt_speed = entity.prototype.belt_speed
        local line_1 = entity.get_transport_line(1)
        local line_2 = entity.get_transport_line(2)

        if line_1 and line_2 and not line_1.can_insert_at_back() and not line_2.can_insert_at_back() then
            local direction_vector = {
                [0] = {x = 0, y = -1},  -- North
                [2] = {x = 1, y = 0},   -- East
                [4] = {x = 0, y = 1},   -- South
                [6] = {x = -1, y = 0},  -- West
            }

            local dx = direction_vector[entity.direction].x
            local dy = direction_vector[entity.direction].y
            local next_position = {x = entity.position.x + dx, y = entity.position.y + dy}
            local next_belt = entity.surface.find_entities_filtered {
                position = next_position,
                type = "transport-belt",
                limit = 1
            }

            if not next_belt[1] then
                local is_moving = false
                for _, item in ipairs(line_1.get_contents()) do
                    if item > 0 then
                        is_moving = true
                        break
                    end
                end

                if not is_moving then
                    for _, item in ipairs(line_2.get_contents()) do
                        if item > 0 then
                            is_moving = true
                            break
                        end
                    end
                end

                if not is_moving then
                    return true
                end
            end
        end
    end
    return false
end

-- Define a function to check if the transport belt is blocked
local function is_transport_belt_blocked2(entity)
    if entity.type == "transport-belt" then
        local belt_speed = entity.prototype.belt_speed
        local line_1 = entity.get_transport_line(1)
        local line_2 = entity.get_transport_line(2)

        if line_1 and line_2 and not line_1.can_insert_at_back() and not line_2.can_insert_at_back() then
            local next_belt = entity.surface.find_entities_filtered {
                position = entity.position,
                direction = entity.direction,
                type = "transport-belt",
                limit = 1
            }

            if not next_belt[1] then
                return true
            end
        end
    end
    return false
end

-- Define a function to check if the entity is a burner and has fuel
local function has_fuel(entity)
    if entity.burner and not entity.burner.currently_burning then
        return false
    end
    return true
end

-- Define a function to check if the entity is a drill and has space to output
local function has_output_space(entity)
    if entity.type == "mining-drill" and entity.mining_target then
        local output_inventory = entity.get_output_inventory()
        if output_inventory and output_inventory.is_full() then
            return false
        end
    end
    if entity.type == "mining-drill" then
        local resource = entity.surface.find_entities_filtered{position = entity.position, type = "resource"}[1]
        local output_inventory = entity.get_output_inventory()
        local drop_position = entity.drop_position
        local items_on_ground = entity.surface.find_entities_filtered{area = {{drop_position.x - 0.5, drop_position.y - 0.5}, {drop_position.x + 0.5, drop_position.y + 0.5}}, type = "item-entity"}

        if #items_on_ground >= 1 or (resource and not output_inventory.is_empty() and output_inventory.can_insert(resource.prototype.mined_item) == false) then
            return false
        end
    end
    return true
end

-- Define a function to check if the entity requires electricity and has any
local function has_electricity(entity)
    if entity.prototype.electric_energy_source_prototype then
        if entity.energy <= 0 then
            return false
        end
    end
    return true
end

-- Define a function to check if the entity is an assembler machine and lacks resources
local function lacks_assembler_resources(entity)
    if entity.type == "assembling-machine" then
        local recipe = entity.get_recipe()
        if recipe then
            local ingredients = recipe.ingredients
            local input_inventory = entity.get_inventory(defines.inventory.assembling_machine_input)
            local missing_resources = {}

            for _, ingredient in pairs(ingredients) do
                local available_amount = input_inventory.get_item_count(ingredient.name)
                local missing_amount = ingredient.amount - available_amount
                if missing_amount > 0 then
                    table.insert(missing_resources, (ingredient.name .. " (" .. tostring(missing_amount) .. ")"):gsub(" ", "_"))
                end
            end

            if #missing_resources > 0 then
                return "cannot_create_" .. recipe.name:gsub(" ", "_") .. "_due_to_missing_resources:_" .. table.concat(missing_resources, ",_")
            end
        end
    end
    return false
end

-- Define a helper function to round a number to the nearest 0.5
local function round_to_half(number)
    return math.floor(number * 2 + 0.5) / 2
end


-- Define a function to be called every tick
local function on_tick(event)
    -- Run the check every 60 ticks (1 second)
    if event.tick % 60 == 0 then
        for _, surface in pairs(game.surfaces) do
            local entities = surface.find_entities_filtered({force = "player"})
            for _, entity in pairs(entities) do
                local issues = {}

                if not has_fuel(entity) then
                    table.insert(issues, "\"out of fuel\"")
                end
                if not has_output_space(entity) then
                    if entity.drop_position ~= nil then
                        local rounded_x = round_to_half(entity.drop_position.x)
                        local rounded_y = round_to_half(entity.drop_position.y)

                        table.insert(issues, "\"waiting for space in destination as the output is full. Place a transport-belt or furnace at (" .. rounded_x .. ", ".. rounded_y .. ") to unblock.\"")
                    else
                        table.insert(issues, "\"waiting for space in destination\"")
                    end
                end
                if not has_electricity(entity) then
                    table.insert(issues, "not_receiving_electricity")
                end
                local assembler_issue = lacks_assembler_resources(entity)
                if assembler_issue then
                    table.insert(issues, assembler_issue)
                end

                if is_transport_belt_blocked(entity) then
                    table.insert(issues, "transport_belt_blocked")
                end
                if #issues > 0 then
                    local position = entity.position
                    local entity_key = entity.name .. "_" .. position.x .. "_" .. position.y
                    local name = '"'..entity.name:gsub(" ", "_")..'"'
                    if not global.alerts[entity_key] then
                        global.alerts[entity_key] = {
                            position = position,
                            issues = issues,
                            entity_name = name,
                            tick = event.tick
                        }
                    end
                end
            end
        end
    end
end

-- Define a function to get alerts older than the number of seconds
global.get_alerts = function(seconds)
    local current_tick = game.tick
    local old_alerts = {}

    for key, alert in pairs(global.alerts) do
        if current_tick - alert.tick > 60*seconds then
            table.insert(old_alerts, alert)
            global.alerts[key] = nil
        end
    end

    return old_alerts
end

-- Register the on_tick function to the on_tick event
script.on_event(defines.events.on_tick, on_tick)