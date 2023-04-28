global.actions.harvest_resource = function(player_index, x, y, count)
    local player = game.players[player_index]

    local position = {x=x, y=y}
    local surface = player.surface

    local success = 0

    function harvest(entities, count)
        local remaining_count = count
        while remaining_count > 0 do
            local did_mine = false

            for _, entity in pairs(entities) do
                if entity.valid and entity.minable and player.can_reach_entity(entity) then
                    did_mine = player.mine_entity(entity)
                    remaining_count = remaining_count - 1
                    if remaining_count == 0 then
                        break
                    end
                end
            end

            if not did_mine then
                break
            end
        end

        return count - remaining_count
    end




    -- Attempt to mine
    local mineable_entities = surface.find_entities_filtered{position=position, radius=5, type = "resource"}
    local mined_count = harvest(mineable_entities, count)
    local total = mined_count
    -- Attempt to harvest trees if mining was not fully successful
    if mined_count < count then
        local tree_entities = surface.find_entities_filtered{position=position, radius=5, type = "tree"}
        local harvested_count = harvest(tree_entities, count - mined_count)
        total = (mined_count + harvested_count)

        if total == 0 then
            error("Could not harvest at position ("..position.x..", "..position.y.."), possibly out of reach?")
        elseif total ~= count then
            error("Could only harvest "..total.." at position ("..position.x..", "..position.y..")")
        end
        success = total > 0
    else
        success = true
        end

    if success == 0 then
        error("Nothing within reach to harvest")
    else
        game.print("Harvested "..total)
        return 1
    end
end