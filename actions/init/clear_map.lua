local player = game.players[1]
local surface=player.surface

for _, entity in ipairs(player.surface.find_entities_filtered{ area={{player.position.x-arg1,
player.position.y-arg1}, {player.position.x+arg1, player.position.y+arg1}}, type="resource"}) do
entity.destroy()
end