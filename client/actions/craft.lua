function craft_entity(player, entity_name, count)
  -- Ensure the player and entity_name are valid
  if not player or not player.valid or not entity_name then
    return false
  end

  -- Check if the player's force has the necessary technology researched
  local entity_prototype = game.entity_prototypes[entity_name]
  if not entity_prototype or not player.force.technologies[entity_prototype.items_to_place_this[1].prototype.name].researched then
    return false
  end

  -- Get the recipe for the entity
  local recipe = player.force.recipes[entity_name]
  if not recipe then
    return false
  end

  -- Check if the player has enough items to craft the entity
  for _, ingredient in pairs(recipe.ingredients) do
    if player.get_item_count(ingredient.name) < ingredient.amount * count then
      return false
    end
  end

  -- Craft the entity, consuming the ingredients
  for _, ingredient in pairs(recipe.ingredients) do
    player.remove_item({name = ingredient.name, count = ingredient.amount * count})
  end

  -- Insert the crafted entity into the player's inventory
  player.insert({name = entity_name, count = count})

  return true
end


function add_to_crafting_queue(player, entity_name, count)
  -- Ensure the player and entity_name are valid
  if not player or not player.valid or not entity_name then
      rcon.print("not valid entity")
      return 0
  end

  -- Check if the player's force has the necessary technology researched
  local entity_prototype = game.entity_prototypes[entity_name]
  if not entity_prototype or not player.force.technologies[entity_prototype.items_to_place_this[1].prototype.name].researched then
      rcon.print("no technology")
      return 0
  end

  -- Get the recipe for the entity
  local recipe = player.force.recipes[entity_name]
  if not recipe then
      rcon.print("no valid recipe")
      return 0
  end

  -- Check if the player has enough items to craft the entity
  for _, ingredient in pairs(recipe.ingredients) do
    if player.get_item_count(ingredient.name) < ingredient.amount * count then
        rcon.print("no ingredients")
        return 0
    end
  end
  -- Calculate the crafting time
  local crafting_time = recipe.energy_required * 60 * count -- 60 ticks per second

  rcon.print('crafting')
  -- Add the crafting task to the global crafting queue
  table.insert(global.crafting_queue, {
    player = player,
    entity_name = entity_name,
    count = count,
    recipe = recipe,
    remaining_ticks = crafting_time
  })

  return 1
end


local player = game.players[arg1]
local entity = arg2
local count = arg3

rcon.print('crafting')
success = add_to_crafting_queue(player, entity, count)

rcon.print(success)