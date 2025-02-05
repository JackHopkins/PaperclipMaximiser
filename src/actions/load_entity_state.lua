-- Helper function to unquote strings
local function unquote_string(str)
    if not str then return nil end
    return string.gsub(str, '"', '')
end

-- Main deserialization function
global.actions.load_entity_state = function(player, stored_json_data)
    local player_entity = game.players[player]
    local surface = player_entity.surface
    local created_entities = {}
    local stored_data = game.json_to_table(stored_json_data)
    local character_state = nil
    -- First pass: Create all non-character entities and store character state
    for _, state in pairs(stored_data) do
        local name = unquote_string(state.name)

        if name == "character" then
            character_state = state
        else
            local entity = surface.create_entity({
                name = name,
                position = {
                    x = tonumber(state.position.x),
                    y = tonumber(state.position.y)
                },
                direction = tonumber(state.direction),
                force = game.forces.player,
                raise_built = true
            })

            if entity then
                created_entities[state.entity_number] = {
                    entity = entity,
                    state = state
                }
            end
        end
    end

    -- Handle character separately
    if character_state then
        -- Store old character position if it exists
        local old_position = nil
        if player_entity.character then
            old_position = player_entity.character.position
            player_entity.character.destroy()
        end

        -- Create new character at the stored position or old position
        local position = {
            x = tonumber(character_state.position.x),
            y = tonumber(character_state.position.y)
        }
        if not surface.can_place_entity{name="character", position=position} then
            position = old_position or {x=0, y=0}
        end

        local new_character = surface.create_entity({
            name = "character",
            position = position,
            direction = tonumber(character_state.direction),
            force = game.forces.player,
        })

        if new_character then
            player_entity.character = new_character
            -- Restore character inventory
            if character_state.inventory then
                local main_inventory = new_character.get_inventory(defines.inventory.character_main)
                if main_inventory then
                    for item_name, count in pairs(character_state.inventory) do
                        -- Remove quotes if they exist
                        item_name = unquote_string(item_name)
                        if item_name and item_name ~= "" then
                            if game.item_prototypes[item_name] then
                                main_inventory.insert({
                                    name = item_name,
                                    count = tonumber(count)
                                })
                            else
                                game.print("Warning: Unknown item " .. item_name)
                            end
                        end
                    end
                else
                    game.print("Warning: Could not get character main inventory")
                end
            end

            -- Add character to created_entities for inventory restoration
            created_entities[character_state.entity_number] = {
                entity = new_character,
                state = character_state
            }
        end
    end

    -- Second pass: Restore states
    for unit_number, data in pairs(created_entities) do
        local entity = data.entity
        local state = data.state
        local entity_type = entity.type

        game.print("Processing entity: " .. entity.name .. " (type: " .. entity_type .. ")")

        -- Restore inventories based on entity type
        for inv_name, contents in pairs(state.inventories or {}) do
            local inventory = nil

            -- Only try to access inventories that match the entity type
            if inv_name == "chest" and entity_type == "container" then
                inventory = entity.get_inventory(defines.inventory.chest)
            elseif inv_name == "furnace_source" and entity_type == "furnace" then
                inventory = entity.get_inventory(defines.inventory.furnace_source)
            elseif inv_name == "furnace_result" and entity_type == "furnace" then
                inventory = entity.get_inventory(defines.inventory.furnace_result)
            elseif inv_name == "fuel" and entity.burner then
                inventory = entity.get_inventory(defines.inventory.fuel)
            elseif inv_name == "burnt_result" and entity.burner then
                inventory = entity.get_inventory(defines.inventory.burnt_result)
            elseif inv_name == "assembling_machine_input" and entity_type == "assembling-machine" then
                inventory = entity.get_inventory(defines.inventory.assembling_machine_input)
            elseif inv_name == "assembling_machine_output" and entity_type == "assembling-machine" then
                inventory = entity.get_inventory(defines.inventory.assembling_machine_output)
            elseif inv_name == "turret_ammo" and entity_type == "ammo-turret" then
                inventory = entity.get_inventory(defines.inventory.turret_ammo)
            elseif inv_name == "lab_input" and entity_type == "lab" then
                inventory = entity.get_inventory(defines.inventory.lab_input)
            end

            if inventory then
                game.print("Found valid inventory for " .. inv_name)
                for quoted_item_name, count in pairs(contents) do
                    local item_name = unquote_string(quoted_item_name)
                    if item_name and item_name ~= "" then
                        if game.item_prototypes[item_name] then
                            game.print("Inserting " .. count .. " " .. item_name)
                            inventory.insert({
                                name = item_name,
                                count = tonumber(count)
                            })
                        else
                            game.print("Warning: Unknown item " .. item_name)
                        end
                    else
                        game.print("Warning: Empty item name in " .. inv_name)
                    end
                end
            else
                game.print("No valid inventory found for " .. inv_name)
            end
        end

        game.print("Restore burner")

        -- Restore burner
        if state.burner and entity.burner then
            if state.burner.currently_burning then
                local burning_name = unquote_string(state.burner.currently_burning)
                if game.item_prototypes[burning_name] then  -- Verify burning item exists
                    entity.burner.currently_burning = game.item_prototypes[burning_name]
                    entity.burner.remaining_burning_fuel = tonumber(state.burner.remaining_burning_fuel)
                    entity.burner.heat = tonumber(state.burner.heat)
                else
                    game.print("Warning: Unknown burning item " .. burning_name)
                end
            end
        end

        -- Restore recipe - only for entities that can have recipes
        if state.recipe then
            -- Only try to set recipe on appropriate entity types
            if (entity.type == "assembling-machine" or
                entity.type == "furnace" or
                entity.type == "rocket-silo") and
               entity.get_recipe then  -- Double check entity supports recipes

                local recipe_name = unquote_string(state.recipe.name)
                if game.recipe_prototypes[recipe_name] then
                    game.print("Setting recipe " .. recipe_name .. " on " .. entity.name)
                    pcall(function()
                        entity.set_recipe(recipe_name)
                    end)
                else
                    game.print("Warning: Unknown recipe " .. recipe_name)
                end
            else
                game.print("Warning: Skipping recipe for incompatible entity type: " .. entity.type)
            end
        end

        -- Restore energy and active state
        if state.energy then
            entity.energy = tonumber(state.energy)
        end
        if state.active ~= nil then
            entity.active = state.active
        end
    end

    return true
end