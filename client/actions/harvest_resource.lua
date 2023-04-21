global.actions.harvest_resource = function(player_index, x, y, count)
    local player = game.players[player_index]

    local position = {x=x, y=y}
    local surface = player.surface

    local success = 0


    function mine_entity(entity)
        if not (entity and entity.valid and player and player.valid) then
            error("Could not mine due to invalid entity")
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
    function harvest(entities, count)
        local remaining_count = count

        while remaining_count > 0 do
            local did_mine = false

            for _, entity in pairs(entities) do
                if entity.valid and entity.minable and player.can_reach_entity(entity) then
                    did_mine = player.mine_entity(entity)
                    if did_mine then
                        remaining_count = remaining_count - 1
                        if not entity.valid or remaining_count <= 0 then
                            break
                        end
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
    local mineable_entities = surface.find_entities_filtered{position=position, radius=3, type = "resource"}
    local mined_count = harvest(mineable_entities, count)

    -- Attempt to harvest trees if mining was not fully successful
    if mined_count < count then
        local tree_entities = surface.find_entities_filtered{position=position, radius=3, type = "tree"}
        local harvested_count = harvest(tree_entities, count - mined_count)
        success = (mined_count + harvested_count) > 0
    else
        success = true
    end

    if success == 0 then
        error("Nothing within reach to harvest")
    else
        return 1
    end
end