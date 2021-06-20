local entity="arg1"
local surface=game.players[1].surface
local count=0
for key, ent in pairs(surface.find_entities_filtered({force=game.players[1].force})) do
	if string.find(ent.name,entity) then
		count=count+1
	end
end
rcon.print(entity+count)