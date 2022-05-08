local player = game.players[arg1]
local entity_name_to_fuel = 'stone-furnace'
local fuel_item = 'arg2'
local fuel_count = arg3


local position = player.position
local surface = player.surface

function abort (message)
    rcon.print(message)
    rcon.print(0)
end

-- If the player has enough fuel
local player_fuel_count = player.get_item_count(fuel_item)

if player_fuel_count == 0 then
    abort('No fuel')
    return
end


local stack = {name=fuel_item, count=1}

-- If we can find an entity to fuel at the players x, y position
local entity_to_fuel = surface.find_entity(entity_name_to_fuel, position)
local entity_fuel_count = entity_to_fuel.get_item_count(fuel_item)

if entity_to_fuel == nil then
    abort('No possible entity to fuel')
    return
end

-- If we can pick up the fuel
local can_set_stack = player.cursor_stack.can_set_stack(stack)

if can_set_stack then
    player.cursor_stack.set_stack(stack)
else
    abort('Cannot set the cursor with a stack')
    return
end

-- Check the fuel was picked up
if player.is_cursor_empty() then
    abort('Fuel was not deposited')
    return
end

-- Make transaction
number_inserted = entity_to_fuel.insert(stack)
number_removed = player.remove_item(stack)

rcon.print(number_inserted .. ":" .. number_removed)

if number_inserted ~= number_removed then
    entity_to_fuel.remove_item(stack)
    player.insert(stack)
    abort('Transaction not executed')
end

player.clear_cursor()
rcon.print(1)