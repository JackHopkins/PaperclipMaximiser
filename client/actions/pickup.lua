local player = game.players[arg1]
local x, y = arg2, arg3
local entity = arg4

local position = {x=x, y=y}--{x=player.position.x+x, y=player.position.y+y}
local surface = player.surface

local success = 0
-- Function to pick up and add entity to player's inventory
local function pickup(entities)
    for _, entity in pairs(entities) do
        if entity.valid then
            if entity.name ~= "character" then
                local products = entity.prototype.mineable_properties.products
                if products ~= nil then
                    for _, product in pairs(products) do
                        player.insert{name=product.name, count=product.amount}
                    end
                end
                if entity.get_inventory(defines.inventory.chest) then
                    for name, count in pairs(entity.get_inventory(defines.inventory.chest).get_contents()) do
                        player.insert{name=name, count=count}
                    end
                end
                player.insert{name=entity.name, count=1}
                entity.destroy()
                success = 1
                end
            end
        end
    end

-- Attempt to pick up
player_entities = surface.find_entities_filtered{name=entity, position=position, radius=3, force = "player"}
pickup(player_entities)

if success == 0 then
    abort("Nothing to here to pick up.")
else
    rcon.print(success)
end