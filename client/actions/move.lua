local cardinals = {defines.direction.north, defines.direction.south, defines.direction.east, defines.direction.west}
local teleport_offsets = {{0, -1}, {0, 1}, {1, 0}, {-1, 0}}
local player = game.players[arg1]
local surface = player.surface
local direction = cardinals[arg2+1]
local teleport_direction = teleport_offsets[arg2+1]
local trailing_entity = arg3
local trailing_position_x = arg4
local trailing_position_y = arg5

function place (to_position)

    local place_position = {x=to_position.x, y=to_position.y}
    local can_place = surface.can_place_entity{name=trailing_entity, position=place_position, direction=direction, force='player', build_check_type=defines.build_check_type.manual}

    if can_place == true then

        local count = player.get_item_count(arg3)
        if count == 0 then
            rcon.print("No ".. trailing_entity .." in the inventory")
            rcon.print(0)
            return
        end

        local created = surface.create_entity{name=trailing_entity, position=place_position, direction=direction, force='player', player=player, build_check_type=defines.build_check_type.manual, fast_replace=true}

        if created ~= nil then
            player.remove_item({name=arg3, count=1})
        end

    else
        rcon.print("Cannot place " ..trailing_entity)
        rcon.print(0)
        return
    end
end

local trailing_position = {x=trailing_position_x, y=trailing_position_y}
--rcon.print(teleport_direction)
if trailing_entity ~= nil then
    place(player.position)
end

player.teleport(teleport_direction[1], teleport_direction[2])

--rcon.print({x=player.position.x+teleport_direction[1], y=player.position.y+teleport_direction[2]})
rcon.print(player.position)

--player.walking_state = {walking = true, direction = direction}