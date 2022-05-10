local player = game.players[arg1]
local surface = player.surface
local chunk_x, chunk_y = arg2, arg3

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

rcon.print(1)
rcon.print(dump(counts))