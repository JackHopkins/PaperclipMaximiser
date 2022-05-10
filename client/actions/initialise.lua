global.points_of_interest = {}
global.distances_to_nearest = {}
global.interesting_entities = {
    ['enemy']=true,
    ['trees']=true,
    ['iron-ore']=true,
    ['stone']=true,
    ['copper-ore']=true,
    ['uranium-ore']=true,
    ['crude-oil']=true,
    ['water']=true,
    ['coal']=true
}

local beam_duration = 9

function create_beam_bounding_box (player, surface, direction, top_left, bottom_right)
    local bottom_left = {x=top_left.x, y=bottom_right.y}
    local top_right = {x=bottom_right.x, y=top_left.y}
    local direction = 0
    surface.create_entity{name='laser-beam', position=player.position, source_position=top_left, target_position=top_right, duration=beam_duration, direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=top_right, target_position=bottom_right, duration=beam_duration, direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=bottom_right, target_position=bottom_left, duration=beam_duration,  direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=bottom_left, target_position=top_left, duration=beam_duration,  direction=direction, force='player', player=player}
    surface.create_entity{name='laser-beam', position=player.position, source_position=player.position, duration=beam_duration, target_position={x=player.position.x, y=player.position.y+0.1}, direction=direction, force='player', player=player}
end

function observe_points_of_interest (surface, player, search_radius)
    nearest_enemy = surface.find_nearest_enemy{position=player.position, max_distance=search_radius}
    points_of_interest = {
        enemy=nearest_enemy.position,
        iron=global.nearest_iron
    }
    rcon.print(1)
    return dump(global.points_of_interest)
end

function get_local_environment (player,  surface, localBoundingBox, field_x, field_y, debug)

    local top = player.position.y-localBoundingBox/2
    local left = player.position.x-localBoundingBox/2
    local bottom = player.position.y+localBoundingBox/2
    local right = player.position.x+localBoundingBox/2

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
        create_beam_bounding_box(player, surface, direction, bounding_box_top_left, bounding_box_bottom_right)
        entities = surface.find_entities_filtered{name="laser-beam", invert=true, area={bounding_box_top_left, bounding_box_bottom_right}}
    else
        entities = surface.find_entities({bounding_box_top_left, bounding_box_bottom_right})
    end

    mt = {}          -- create the matrix
    for i,entity in pairs(entities) do
        local x_pos = left-entity.position.x
        local y_pos = top-entity.position.y
        local name = entity.name
        rcon.print(x_pos .. ", " .. y_pos .. ": " .. name)
        rcon.print(x_pos*(top-bottom)+ y_pos .. ": ".. name)
        mt[math.floor(x_pos*(top-bottom) + y_pos)] = name:gsub("-", "_")
        set_points_of_interest(player, name, 1, x_pos, y_pos)

    end

    rcon.print(1)
    return dump(mt)
end

function observe_chunk(player, surface, chunk_x, chunk_y)
    counts = {}
    key = chunk_x .. ", " ..chunk_y

    chunk_area = {{chunk_x*32, chunk_y*32}, {(chunk_x+1)*32, (chunk_y+1)*32}}

    counts['all'] = surface.count_entities_filtered{area=chunk_area}

    -- Environment
    counts['trees'] = surface.count_entities_filtered{area=chunk_area, type = "tree"}
    counts['water'] = surface.count_tiles_filtered{area=chunk_area, name = 'water'}
    counts['pollution'] = surface.get_pollution({chunk_x*32,chunk_y*32})

    -- Forces
    counts['factory'] = surface.count_entities_filtered{area=chunk_area, force = "player"}
    counts['enemy'] = surface.count_entities_filtered{area=chunk_area, force = "enemy"}

    -- Resources
    counts['iron-ore'] = surface.count_entities_filtered{area=chunk_area, name = "iron-ore"}
    counts['coal'] = surface.count_entities_filtered{area=chunk_area, name = "coal"}
    counts['copper-ore'] = surface.count_entities_filtered{area=chunk_area, name = "copper-ore"}
    counts['uranium-ore'] = surface.count_entities_filtered{area=chunk_area, name = "uranium-ore"}
    counts['stone'] = surface.count_entities_filtered{area=chunk_area, name = "stone"}
    counts['crude-oil'] = surface.count_entities_filtered{area=chunk_area, name = "crude-oil"}

    for field_name, count in pairs(counts) do
        set_points_of_interest(player, field_name, count, chunk_x, chunk_y)
    end

    rcon.print(1)
    return dump(counts)
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

function set_points_of_interest (player, field, count, chunk_x, chunk_y)
    if count > 0 and global.interesting_entities[field] then
        x_distance = (chunk_x*32 - player.position.x) * (chunk_x*32 - player.position.x)
        y_distance = (chunk_y*32 - player.position.y) * (chunk_y*32 - player.position.y)
        distance = math.sqrt(x_distance, y_distance)

        if global.distances_to_nearest[field] == nil then
            global.distances_to_nearest[field] = 100000
        end

        if global.distances_to_nearest[field] > distance then
            global.distances_to_nearest[field] = distance
            global.points_of_interest[field] = {x=chunk_x*32, y=chunk_y*32}
        end
    end
end