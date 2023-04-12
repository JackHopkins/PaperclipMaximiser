local player = game.players[arg1]
local entity = arg2
local direction = arg3
local position = {x=arg4+player.position.x, y=arg5+player.position.y}

if game.entity_prototypes[entity] == nil then
    name = entity:gsub(" ", "_"):gsub("-", "_")
    abort(name .. " isnt something that exists. Did you make a typo? ")
    return
end

local count = player.get_item_count(entity)

if count == 0 then
    name = entity:gsub(" ", "_"):gsub("-", "_")
    abort("No ".. name .." in inventory.")
    return
end

local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
local prototype = game.entity_prototypes[arg2]
local collision_box = prototype.collision_box
local width = math.abs(collision_box.right_bottom.x - collision_box.left_top.x)
local height = math.abs(collision_box.right_bottom.y - collision_box.left_top.y)

local can_build = player.can_place_entity{name=entity, force=player.force, position=position, direction=cardinals[arg3]}

if can_build == false or can_build == 0 then
    local target_area = {
        {position.x - width / 2, position.y - height / 2},
        {position.x + width / 2, position.y + height / 2}
    }
    local entities = player.surface.find_entities_filtered{area = target_area}
    local blocking_entities = {}

    for _, blocking_entity in ipairs(entities) do
        local entity_box = blocking_entity.prototype.collision_box
        local entity_area = {
            {blocking_entity.position.x + entity_box.left_top.x, blocking_entity.position.y + entity_box.left_top.y},
            {blocking_entity.position.x + entity_box.right_bottom.x, blocking_entity.position.y + entity_box.right_bottom.y}
        }

        if (entity_area[1][1] < target_area[2][1] and entity_area[2][1] > target_area[1][1]) and
           (entity_area[1][2] < target_area[2][2] and entity_area[2][2] > target_area[1][2]) then

            local name = blocking_entity.name
            local position = " at "..(blocking_entity.position.x-player.position.x).."___"..(blocking_entity.position.y-player.position.y).." and the size of the entity is "..width
            table.insert(blocking_entities, name..position)
        end
    end
    if #blocking_entities > 0 then
        abort("Cant build there due to existing " .. table.concat(blocking_entities, "___") .. ", Need "..width.." space, Maybe inspect your surroundings.")
    else
        abort("Cant build there, Maybe inspect your surroundings " .. tostring(can_build))
    end
else
    local have_built = player.surface.create_entity{name=entity, force="player", position=position, direction=cardinals[arg3], player=player}
    if have_built then
        player.remove_item{name=entity, count=1}
        rcon.print(1)
    end
end