local player = game.players[arg1]
local surface = player.surface

function harvest (entities)
    for i,entity in pairs(mineable_entities) do
        did_mine = player.mine_entity(entity)
        rcon.print(1)
        return
    end
end

-- Attempt to mine
mineable_entities = surface.find_entities_filtered{position=player.position, radius=0.5, type = "resource"}
harvest(mineable_entities)

-- Attempt to harvest trees
tree_entities = surface.find_entities_filtered{position=player.position, radius=1, type = "tree"}
harvest(mineable_entities)

-- Attempt to pick up
player_entities = surface.find_entities_filtered{position=player.position, radius=1, force = "player"}
harvest(player_entities)
