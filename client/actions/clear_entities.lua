global.actions.clear_entities = function(player_index)
    local function clear_area_of_player_placed_entities(player, area)
        local surface = player.surface
        local entities = surface.find_entities_filtered{
            area = area,
            force = player.force
        }

        for _, entity in ipairs(entities) do
            if entity and entity.valid and entity.name ~= "player" then
                entity.destroy()
            end
        end
    end

    local function reset_character_inventory(character)
        for inventory_id, inventory in pairs(defines.inventory) do
            local character_inventory = character.get_inventory(inventory)
            if character_inventory then
                character_inventory.clear()
            end
        end
    end

    -- Usage example
    local player = game.players[player_index]
    local character = player.character
    local area = {
        {character.position.x - 200, character.position.y - 200},
        {character.position.x + 200, character.position.y + 200}
    }

    clear_area_of_player_placed_entities(player, area)
    reset_character_inventory(character)

    return 1
end