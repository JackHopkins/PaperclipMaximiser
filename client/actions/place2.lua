local player = game.players[arg1]
local position = player.position
local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
local entity = arg2
local direction = arg3
local position = {x=arg4+player.position.x, y=arg5+player.position.y}
local count = player.get_item_count(entity)


if count == 0 then
    name = entity:gsub(" ", "_")
    abort("No ".. name .." in inventory.")
    return
end

local stack = {name=entity, count=1}

if player.cursor_stack.can_set_stack(stack) then
    player.cursor_stack.set_stack(stack)
else
    abort("Can't set the cursor")
    return
end

local prototype = game.entity_prototypes[arg2]
local collision_box = prototype.collision_box
local width = math.abs(collision_box.right_bottom.x - collision_box.left_top.x)
local height = math.abs(collision_box.right_bottom.y - collision_box.left_top.y)

local can_build = player.can_build_from_cursor{position=position, direction=cardinals[arg3], skip_fog_of_war=false}

if can_build == false or can_build == 0 then
    abort("Cant build at position")
else
    local have_built = player.build_from_cursor{position=position, direction=cardinals[arg3], skip_fog_of_war=false}
--    if have_built == true or have_built == 1 then
    rcon.print(1)
--    end
end
player.clear_cursor()