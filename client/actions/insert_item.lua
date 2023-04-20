local player = game.players[arg1]

local insert_item = arg2
local count = arg3
local x, y = arg4, arg5

local position = {x=player.position.x+x, y=player.position.y+y}
local surface = player.surface


-- If the player has enough items
local item_count = player.get_item_count(insert_item)

if item_count == 0 then
    abort('No item to place')
end

local closest_distance = math.huge
local closest_entity = nil
local area = {{position.x - 10, position.y - 10}, {position.x + 10, position.y + 10}}
local buildings = surface.find_entities_filtered{area = area}

-- Find the closest building
for _, building in ipairs(buildings) do
    if building.get_inventory(defines.inventory.chest) ~= nil and building.name ~= 'character' then
        local distance = ((position.x - building.position.x) ^ 2 + (position.y - building.position.y) ^ 2) ^ 0.5
        if distance < closest_distance then
            closest_distance = distance
            closest_entity = building
        end
    end
end

if closest_entity == nil then
    abort("Could not find a nearby entity to insert into.")
else

    -- Check if the entity can accept the item
    local closest_entity_count = closest_entity.get_item_count(insert_item)

    if closest_entity_count == nil then
        abort('No possible entity to fuel')
    end

    -- Make transaction
    local number_removed = player.remove_item{name=insert_item, count=count}
    local number_inserted = closest_entity.insert{name=insert_item, count=number_removed}

    if number_inserted ~= number_removed then
        closest_entity.remove_item{name=insert_item, count=number_inserted}
        player.insert{name=insert_item, count=number_removed}
        abort('Transaction not executed')
    end

    rcon.print(1)

end