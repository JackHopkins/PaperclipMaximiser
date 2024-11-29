global.actions.production_stats = function(player)
    local production_diff = {}
    local consumption_diff = {}
    -- Get total production counts for force
    local force = game.forces.player

    local item_input_counts = force.item_production_statistics.input_counts
    local item_production_counts = force.item_production_statistics.output_counts
    local fluid_input_counts = force.fluid_production_statistics.input_counts
    local fluid_production_counts = force.fluid_production_statistics.output_counts

    for name, count in pairs(item_input_counts) do
        consumption_diff[name] = count
    end

    for name, count in pairs(item_production_counts) do
        production_diff[name] = count
    end

    for name, count in pairs(fluid_input_counts) do
        consumption_diff[name] = count
    end

    for name, count in pairs(fluid_production_counts) do
        production_diff[name] = count
    end
    return {
        output = consumption_diff,
        input = production_diff
    }
end