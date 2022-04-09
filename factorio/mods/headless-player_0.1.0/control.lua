local Player = require('__stdlib__/stdlib/event/player').register_events()
local player, player_data = Player.get(event.player_index)

Player.init(1, overwrite=True)