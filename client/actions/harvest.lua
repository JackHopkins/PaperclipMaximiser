local player = game.players[arg1]
local x, y, count = arg2, arg3, arg4, arg5

local position = {x=player.position.x+x, y=player.position.y+y}
local surface = player.surface

local success = 0


function mine_entity(entity)
    if not (entity and entity.valid and player and player.valid) then
        abort("Could not ")
    end

    local mining_tool = player.character_mining_speed_modifier
    local mining_speed = 1 + mining_tool

    for _ = 1, count do
        entity.damage(mining_speed, player.force, "mining-drill")
        if not entity.valid then
            break
        end
    end
end

function harvest(entities)
    local did_mine = 0

    for _, entity in pairs(entities) do
        if entity.valid and entity.minable and player.can_reach_entity(entity) then
            for _ = 1, count do
                did_mine = player.mine_entity(entity)
                if not entity.valid then
                    success = 1
                    break
                end
            end
            if success == 1 then
                break
            end
        end
    end
end


-- Attempt to mine
mineable_entities = surface.find_entities_filtered{position=position, radius=3, type = "resource"}
harvest(mineable_entities)

-- Attempt to harvest trees
tree_entities = surface.find_entities_filtered{position=position, radius=3, type = "tree"}
harvest(tree_entities)


if success == 0 then
    abort("Nothing within reach to harvest")
else
    rcon.print(success)
end