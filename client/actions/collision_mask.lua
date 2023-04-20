-- Observe.lua
global.actions.collision_mask = function(player, localBoundingBox)
    local player = game.players[arg1]
    local localBoundingBox = arg2

    response = find_passable_tiles(player, localBoundingBox)
    rcon.print(player.position)
    return dump(response)
end



--rcon.print(observe())
local status, response = global.actions.collision_mask(arg1, arg2) --pcall(observe)

if status ~= true then
    rcon.print(status)
    rcon.print(dump(response))--> a 121
else
    rcon.print(dump(response))
end