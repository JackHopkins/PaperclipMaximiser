global.actions.check_inventory = function(player_index)
    local function get_player_inventory_items(player)
        local inventory = player.get_main_inventory()
        if not inventory or not inventory.valid then
            return nil
        end

        local item_counts = inventory.get_contents()
        return item_counts
    end

    local player = game.players[player_index]
    if not player then
        abort("Player not found")
    end

    local inventory_items = get_player_inventory_items(player)

    if inventory_items then
        rcon.print(dump(inventory_items))
    else
        abort("Could not get player inventory")
    end
end