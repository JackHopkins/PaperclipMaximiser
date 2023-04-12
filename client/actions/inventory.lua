function get_player_inventory_items(player)
    local inventory = player.get_main_inventory()
    if not inventory or not inventory.valid then
        return nil
    end

    local item_counts = inventory.get_contents()
    return item_counts
end

local player = game.players[arg1]
if not player then
    rcon.print("Player not found")
    return
end

local inventory_items = get_player_inventory_items(player)

if inventory_items then
    rcon.print(dump(inventory_items))
else
    rcon.print("Could not get player inventory")
end