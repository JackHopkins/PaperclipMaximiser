local player = game.players[arg1]
local surface = player.surface
local localBoundingBox = arg2
local field_x, field_y = arg3, arg4
local debug = arg5
local globalBoundingBox = 50

local beam_duration = 9

function createBeamBoundingBox (top_left, bottom_right)
    local bottom_left = {x=top_left.x, y=bottom_right.y}
    local top_right = {x=bottom_right.x, y=top_left.y}

    surface.create_entity{name='laser-beam', position=player.position, source_position=top_left, target_position=top_right, duration=beam_duration, direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=top_right, target_position=bottom_right, duration=beam_duration, direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=bottom_right, target_position=bottom_left, duration=beam_duration,  direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=bottom_left, target_position=top_left, duration=beam_duration,  direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=player.position, duration=beam_duration, target_position={x=player.position.x, y=player.position.y+0.1}, direction=direction, force='player', player=player}
end

function dump(o)
   if type(o) == 'table' then
      local s = '{ '
      for k,v in pairs(o) do
         if type(k) ~= 'number' then k = '"'..k..'"' end
         s = s .. '['..k..'] = ' .. dump(v) .. ','
      end
      return s .. '} '
   else
      return tostring(o)
   end
end

function getPlayerPosition ()
    return player.position
end

function getLocalEnvironment ()

    local top = player.position.y-localBoundingBox/2
    local left = player.position.x-localBoundingBox/2
    local bottom = player.position.y+localBoundingBox/2
    local right = player.position.x+localBoundingBox/2
    --field_x = field_x * -1
    --field_y = field_y * -1

    if field_x > 0 then
        right = right + field_x
        left = right - field_x
    elseif field_x < 0 then
        left = left + field_x
        right = left - field_x
    end

    if field_y < 0 then
        top = top + field_y
        bottom = top-field_y
    elseif field_y > 0 then
        bottom = bottom + field_y
        top = bottom-field_y
    end

    bounding_box_top_left = {x=left, y=top}
    bounding_box_bottom_right = {x=right, y=bottom}

    if debug then
        createBeamBoundingBox(bounding_box_top_left, bounding_box_bottom_right)
        entities = surface.find_entities_filtered{name="laser-beam", invert=true, area={bounding_box_top_left, bounding_box_bottom_right}}
    else
        entities = surface.find_entities({bounding_box_top_left, bounding_box_bottom_right})
    end

    mt = {}          -- create the matrix
    for i,entity in pairs(entities) do
        x_pos = left-entity.position.x
        y_pos = top-entity.position.y
        rcon.print(x_pos .. ", " .. y_pos .. ": " .. entity.name)
        rcon.print(x_pos*(top-bottom)+ y_pos .. ": ".. entity.name)
        mt[math.floor(x_pos*(top-bottom) + y_pos)] = entity.name:gsub("-", "_")
    end

    return dump(mt)
end

function getGlobalEnvironment ()
    mt = {}
    for chunk in surface.get_chunks() do
        player.print("x: " .. chunk.x .. ", y: " .. chunk.y)
        player.print("area: " .. serpent.line(chunk.area))
        --rcon.print(surface.count_tiles_filtered{area=chunk.area, collision_mask='water-tile'})
    end

end

function getPointsOfInterest ()

end

function getBuildableRecipes ()

end

function getInventory ()

end

local observation = {}

--observation['position'] = getPlayerPosition()
--observation['localEnvironment'] = getLocalEnvironment()
--bservation['globalEnvironment'] = getGlobalEnvironment()
--observation['pointsOfInterest'] = getPointsOfInterest()
--observation['buildableRecipes'] = getBuildableRecipes()
--observation['inventory'] = getInventory()




rcon.print(1)
rcon.print(dump(getLocalEnvironment()))