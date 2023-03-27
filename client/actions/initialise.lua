--Initialise.lua
local player = game.players[arg1]
--local position = player.position

--player.game_view_settings.show_controller_gui = false
--player.game_view_settings.show_minimap = false
--player.game_view_settings.show_side_menu = false
--player.game_view_settings.show_quickbar = false
--player.game_view_settings.show_shortcut_bar = false
--player.game_view_settings.show_map_view_options = false
--player.game_view_settings.show_shortcut_bar = false

--player.character=nil

global.points_of_interest = {}
global.distances_to_nearest = {}
global.relative_points_of_interest = {}
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

local surface=player.surface
local pp = player.position
local cnt = 0
for key, entity in pairs(surface.find_entities_filtered({force="enemy", radius=250, position=pp })) do
	cnt = cnt+1
	entity.destroy()
 end

local beam_duration = 9

global.crafting_queue = {}

script.on_event(defines.events.on_tick, function(event)
  -- Iterate over the crafting queue and update the remaining ticks
  for i, task in ipairs(global.crafting_queue) do
    task.remaining_ticks = task.remaining_ticks - 1

    -- If the crafting is finished, consume the ingredients, insert the crafted entity, and remove the task from the queue
    if task.remaining_ticks <= 0 then
      for _, ingredient in pairs(task.recipe.ingredients) do
        task.player.remove_item({name = ingredient.name, count = ingredient.amount * task.count})
      end
      task.player.insert({name = task.entity_name, count = task.count})
      table.remove(global.crafting_queue, i)
    end
  end
end)

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
    local enemy = surface.find_nearest_enemy{position=player.position, max_distance=search_radius}
    if enemy ~= nil then
        global.points_of_interest['enemy'] = enemy.position
    end

    for k, v in pairs(global.points_of_interest) do
        global.relative_points_of_interest[k] = {
            x=v.x-player.position.x,
            y=v.y-player.position.y
        }
    end

    rcon.print(1)
    return dump(global.relative_points_of_interest)
end

function find_passable_tiles2(player, localBoundingBox)

    -- Generate a 100x100 bounding box centered on the player
    local origin = player.position
    local offset = localBoundingBox / 2

    local left = origin.x - offset
    local right = origin.x + offset
    local top = origin.y - offset
    local bottom = origin.y + offset

    local bounding_box = {
        left_top = {x = left, y = top},
        right_bottom = {x = right, y = bottom}
    }
    local impassable_tiles = {}
    local xmin = bounding_box.left_top.x
    local ymin = bounding_box.left_top.y
    local xmax = bounding_box.right_bottom.x
    local ymax = bounding_box.right_bottom.y

    local area = {{xmin, ymin}, {xmax, ymax}}

    local entities = player.surface.find_entities_filtered{area = area, force = player.force}

    local function coords_to_index(x, y)
        return (x - xmin) * localBoundingBox + (y - ymin) --(x - xmin) * (xmax - xmin) + (y - ymin) -- Changed (ymax - ymin) to (xmax - xmin)
    end

    for x = xmin, xmax do
        for y = ymin, ymax do
            local tile = player.surface.get_tile(x, y)
            local is_impassable = tile.prototype.collision_mask["player-layer"]

            if is_impassable then
                local relative_x, relative_y = x - xmin, y - ymin

                -- Ensure the coordinates are integers by rounding them
                --local index_x = math.floor(relative_entity_x + offset)
                --local index_y = math.floor(relative_entity_y + offset)

                --local index = index_y * localBoundingBox + index_x

                local index = coords_to_index(relative_x, relative_y)
                impassable_tiles[index] = 100--{x = relative_x, y = relative_y}
            end
        end
  end

  for _, entity in ipairs(entities) do
    local collision_box = entity.prototype.collision_box
    local is_passable = (collision_box.left_top.x == 0 and collision_box.left_top.y == 0 and
                         collision_box.right_bottom.x == 0 and collision_box.right_bottom.y == 0)
    if is_passable then
      local x, y = math.floor(entity.position.x), math.floor(entity.position.y)
      local relative_x, relative_y = x - xmin, y - ymin
      local index = coords_to_index(relative_x, relative_y)

      if not impassable_tiles[index] then
        impassable_tiles[index] = 100--{x = relative_x, y = relative_y, entity = entity}
      end
    end
  end

  return impassable_tiles
end

function find_passable_tiles(player, localBoundingBox)
    -- Generate a 100x100 bounding box centered on the player
    local origin = player.position
    local offset = localBoundingBox / 2

    local left = origin.x - offset
    local right = origin.x + offset
    local top = origin.y - offset
    local bottom = origin.y + offset

    local bounding_box = {
        left_top = {x = left, y = top},
        right_bottom = {x = right, y = bottom}
    }
    local impassable_tiles = {}
    for x = left, right do
        for y = top, bottom do
            local tile = player.surface.get_tile(x, y)
            local is_impassable = tile.prototype.collision_mask["player-layer"]

            if is_impassable then
                --(x - xmin) * localBoundingBox + (y - ymin)
                local relative_x, relative_y = x + offset, y + offset
                --local index = coords_to_index(relative_x, relative_y)
                local index = relative_y * localBoundingBox + relative_x
                if not impassable_tiles[index] then
                    impassable_tiles[index] = 100
                end
            end

        end

    end

    -- Find all entities within the bounding box
    local entities = player.surface.find_entities_filtered{area = {{left, top}, {right, bottom}}, force = player.force}

    for _, entity in ipairs(entities) do
        local collision_box = entity.prototype.collision_box
        local is_passable = (collision_box.left_top.x == 0 and collision_box.left_top.y == 0 and
                             collision_box.right_bottom.x == 0 and collision_box.right_bottom.y == 0)
        if not is_passable then -- Change this condition to check for impassable entities
            local x, y = math.floor(entity.position.x), math.floor(entity.position.y)
            local relative_x, relative_y = x - left, y - top
            local index = relative_y * localBoundingBox + relative_x

            if not impassable_tiles[index] then
                impassable_tiles[index] = 99--{x = relative_x, y = relative_y, entity = entity}
            end
        end
  end

    -- Convert the X, Y coordinates of each entity into coordinates relative to the origin
    local relative_entities = {}
    for _, entity in ipairs(entities) do
        table.insert(relative_entities, {x = left, y = top, entity = entity})
    end

    -- Create a 1D sparse index of the x, y coordinate and entity, starting from the top left of the bounding box
    local sparse_index = {}
    for _, relative_entity in ipairs(relative_entities) do
        -- Ensure the coordinates are integers by rounding them
        local index_x = math.floor(relative_entity.x + offset)
        local index_y = math.floor(relative_entity.y + offset)

        local index = index_y * localBoundingBox + index_x
        --impassable_tiles[index] = 99
    end

    rcon.print(1)
    return impassable_tiles
end

function get_locality(player, surface, localBoundingBox)
    -- Generate a 100x100 bounding box centered on the player
    local origin = player.position
    local offset = localBoundingBox / 2

    local left = origin.x - offset
    local right = origin.x + offset
    local top = origin.y - offset
    local bottom = origin.y + offset

    local bounding_box = {
        left_top = {x = left, y = top},
        right_bottom = {x = right, y = bottom}
    }

    -- Find all entities within the bounding box
    local entities = surface.find_entities(bounding_box)

    -- Convert the X, Y coordinates of each entity into coordinates relative to the origin
    local relative_entities = {}
    for _, entity in ipairs(entities) do
        local relative_x = entity.position.x - origin.x
        local relative_y = entity.position.y - origin.y
        table.insert(relative_entities, {x = relative_x, y = relative_y, entity = entity})
        local name = entity.name
        set_points_of_interest(player, name, 1, relative_x, relative_y)
    end

    -- Create a 1D sparse index of the x, y coordinate and entity, starting from the top left of the bounding box
    local sparse_index = {}
    for _, relative_entity in ipairs(relative_entities) do
        -- Ensure the coordinates are integers by rounding them
        local index_x = math.floor(relative_entity.x + offset)
        local index_y = math.floor(relative_entity.y + offset)

        local index = index_y * localBoundingBox + index_x
        local name = relative_entity.entity.name
        sparse_index[index] = name:gsub("-", "_")
    end

    rcon.print(1)
    return sparse_index
end


function get_local_environment (player, surface, localBoundingBox, field_x, field_y, debug)

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

            mt[math.floor(x_pos*(top-bottom) + y_pos)] = name:gsub("-", "_")
            set_points_of_interest(player, name, 1, x_pos, y_pos)

    end

    rcon.print(1)
    return mt
end

function observe_statistics (player)
    performance = {
        item = {
            input_counts=player.force.item_production_statistics.input_counts,
            output_counts=player.force.item_production_statistics.output_counts
        },
        fluid = {
            input_counts=player.force.fluid_production_statistics.input_counts,
            output_counts=player.force.fluid_production_statistics.output_counts
        },
        kills = {
            input_counts=player.force.kill_count_statistics.input_counts,
            output_counts=player.force.kill_count_statistics.output_counts
        },
        built = {
            input_counts=player.force.entity_build_count_statistics.input_counts,
            output_counts=player.force.entity_build_count_statistics.output_counts
        }
    }
    return performance
end

function clean_nils(t)
  local ans = {}
  for _,v in pairs(t) do
    ans[ #ans+1 ] = v
  end
  return ans
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
        --if count ~= 0 then
        set_points_of_interest(player, field_name, count, chunk_x, chunk_y)
        --else
            --table.remove(counts, field_name)
        --end
    end

    rcon.print(1)
    return counts
end

function observe_buildable (player, inventory)
    local recipes = {}
    for field_name, recipe in pairs(player.force.recipes) do
        local name = field_name:gsub("-", "_")
        local can_build = 0
        for i, ingredient in pairs(recipe.ingredients) do
            if inventory[ingredient.name] ~= nil then
                local max_build = inventory[ingredient.name] / ingredient.amount
                can_build = math.floor(max_build)
            else
                can_build = 0
                break
            end
        end
        if can_build ~= 0 then
            recipes[name] = can_build
        end
    end
    return serpent.line(recipes)
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
        distance_square = x_distance + y_distance

        if global.distances_to_nearest[field] == nil then
            global.distances_to_nearest[field] = 100000
        end

        if global.distances_to_nearest[field] > distance_square then
            global.distances_to_nearest[field] = math.sqrt(distance_square) --only compute expensive sqrt when necessary
            global.points_of_interest[field] = {x=chunk_x*32, y=chunk_y*32}
        end
    end
end

rcon.print(1)