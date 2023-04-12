local player = game.players[arg1]
local entity = arg2
local direction = arg3
local position = {x=arg4+player.position.x, y=arg5+player.position.y}
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

local can_build = player.can_place_entity{name=entity, position=position, direction=cardinals[arg3]}

if can_build == false or can_build == 0 then
    local entities = player.surface.find_entities_filtered{
        area = {
            {position.x - width / 2, position.y - height / 2},
            {position.x + width / 2, position.y + height / 2}
        }
    }
    local blocking_entities = {}
    for _, blocking_entity in ipairs(entities) do
        --abort(blocking_entity.name)
        --if blocking_entity.name ~= "character" then
        local name = blocking_entity.name:gsub("-", "_")
        local position = " at "..(blocking_entity.position.x-player.position.x).."___"..(blocking_entity.position.y-player.position.y)
        table.insert(blocking_entities, name..position)
        --end
    end
    abort("Cant build there due to existing " .. table.concat(blocking_entities, ", ") .. ". Need "..width.." space. Maybe inspect your surroundings.")
else
    local have_built = player.surface.create_entity{name=entity, force="player", position=position, direction=cardinals[arg3], player=player}
    if have_built then
        player.remove_item{name=entity, count=1}
        rcon.print(1)
    end
end
