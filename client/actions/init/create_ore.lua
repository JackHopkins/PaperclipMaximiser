local surface = game.player.surface;
for y=-YPOS, YPOS do
for x=-XPOS, XPOS do
  surface.create_entity({name="ORE", amount=Z, position={game.player.position.x+x, game.player.position.y+y}})
end
end