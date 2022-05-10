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

performance = {}

performance['item'] = {
    input_counts=player.force.item_production_statistics.input_counts,
    output_counts=player.force.item_production_statistics.output_counts
}
performance['fluid'] = {
    input_counts=player.force.fluid_production_statistics.input_counts,
    output_counts=player.force.fluid_production_statistics.output_counts
}
performance['kills'] = {
    input_counts=player.force.kill_count_statistics.input_counts,
    output_counts=player.force.kill_count_statistics.output_counts
}
performance['built'] = {
    input_counts=player.force.entity_build_count_statistics.input_counts,
    output_counts=player.force.entity_build_count_statistics.output_counts
}

rcon.print(1)
rcon.print(dump(performance))