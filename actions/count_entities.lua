local entity="arg1"
local surface=game.players[1].surface
local count=0
local out=0
for key, ent in pairs(surface.find_entities_filtered({force=game.players[1].force})) do
    rcon.print(ent.name)
	if string.find(ent.name,entity) then
		count=count+1
	end
	out=out+1
end
rcon.print(surface)
rcon.print(out)
rcon.print(count)