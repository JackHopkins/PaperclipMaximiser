local player = game.players[arg1]
local position = player.position
local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
local count = player.get_item_count('arg2')

if count == 0 then
    rcon.print(0)
    return
end

local stack = {name="arg2", count=1}

if player.cursor_stack.can_set_stack(stack) then
    player.cursor_stack.set_stack(stack)
else
    rcon.print(0)
    return
end

if player.is_cursor_empty() then
    rcon.print(0)
    return
end

local can_build = player.can_build_from_cursor{position=position, direction=cardinals[arg3], terrain_building_size=2, skip_fog_of_war=false}
rcon.print(can_build)

if can_build == false then
    rcon.print(0)
    return
else
    player.remove_item(stack)
    local have_built = player.build_from_cursor{position=position, direction=cardinals[arg3], terrain_building_size=2, skip_fog_of_war=false}
    rcon.print(1)

end

player.clear_cursor()