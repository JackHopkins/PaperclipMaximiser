local function find_nearest(player, resource)
    local surface = player.surface
    local position = player.position
    local closest_distance = math.huge
    local closest = nil

    for _, entity in ipairs(surface.find_entities_filtered{area = {{position.x - 500, position.y - 500}, {position.x + 500, position.y + 500}},
                                                          type = "resource",
                                                          name = resource
    }) do
        --if entity.amount > 0 then
        local distance = ((position.x - entity.position.x) ^ 2 + (position.y - entity.position.y) ^ 2) ^ 0.5
        if distance < closest_distance then
            closest_distance = distance
            closest = entity.position
        end
        --end
    end

    return { x= position.x-closest.x, y= position.y-closest.y }
end


-- Observe.lua
function find()
    local player = game.players[arg1]
    local resource = arg2

    response = find_nearest(player, resource)
    rcon.print(player.position)
    return dump(response)
end

--rcon.print(observe())
local status, response = pcall(find)

if status ~= true then
    rcon.print(status)
    rcon.print(dump(response))--> a 121
else
    rcon.print(dump(response))
end