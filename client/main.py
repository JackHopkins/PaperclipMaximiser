# !/usr/bin/env python3
from timeit import default_timer as timer
from factorio_runner import FactorioRunner

observe_local_times = []
iterations = 100


brief = \
    """
You are playing a computer game Factorio.

In order to issue commands, you submit programs with the following commands in them:

```
nature() # look around and describe what resources and nature you see
inspect() # inspect the entities immediately around you
inventory() # look to see what items you have
goto((10, 5), trailing='transport-belt') #move 10m east, 5 south creating transport as you go.
craft('iron-chest', count=1) #craft 1 iron chest.
place('assembling-machine-1', UP, (1,1)) # places at 1m north and east of the player, facing up.
wait(5) # wait 5 seconds.
insert('coal', (0, 0), count=1) # inserts 1 coal into nearby entity from inventory
extract('coal', (0, 1), count=1) # picks up 1 coal from the entity 1m to the south
set_recipe('iron-chest') # set recipe of nearby entity to craft 'iron-chest'
goto((0, -40)) # move north 40 metres
goto(nearest('tree')) # move to the nearest tree
interact((-2, 0), count=5) # harvest or mine 5 of the entity under the player
rotate((0,0), LEFT) # rotate nearby entity to face left
``` 
- Positions are relative to the player, not absolute.
- Only speak using the commands above. 
- Gain score from creating a higher production factory. 
- Explain your thought process by using comments.
- Maximize your score.
- If a command fails, think about what went wrong and continue from there.
"""


async def main():
    servers = 4

    factorio_pool = None  # FactorioPool(servers, 64, 27016)
    await factorio_pool.connect()
    await factorio_pool.initialise(iron_ore=20)
    iterations = 1000
    time = timer()
    for i in range(iterations):
        await factorio_pool.act('move', 2)
        responses = await factorio_pool.observe()
        # print(responses)
        # [tg.start_soon(instance.move, 1) for instance in factorio_pool.instances]

    end = (timer() - time)
    print(
        f"Async: servers={servers} seconds_elapsed={end}, iterations_ps={(timer() - time) / iterations} command_throughput={1 / (((timer() - time) / iterations) / servers)}")


program = \
    """
# First, let's gather some resources
goto(nearest('coal'))
interact(count=5)
goto(nearest('iron-ore'))
interact(count=5)
goto(nearest('stone'))
interact(count=5)
goto(nearest('copper-ore'))
interact(count=5)

# Now, let's start setting up production
# Craft a stone furnace, an assembling machine, and a transport belt
craft('stone-furnace', count=1)
craft('assembling-machine-1', count=1)
craft('transport-belt', count=10)
"""

history = [] #queue.Queue(maxsize=10)
global buffer
buffer = ""

def log_history(message, role):
    print(message)

    history.append({
        "role": role, "content": message
    })



def log_error(message):
    log_history(message, "user")


def log_command(message):
    log_history(message, "assistant")


def log_observation(message):
    log_history(message, "user")


def get_program_generator():
    messages = [{"role": "system", "content": brief}] + history[-10:]
    return openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=64,
        messages=messages,
        stop="\n\n#",
        stream=True
    )
test = \
"""
place_entity('burner-mining-drill', direction=DOWN, position=nearest('iron_ore'))
tree_position = nearest('tree')
move_to(tree_position)
harvest_resource(tree_position, quantity=1)
"""
test2 = \
"""
move_to(nearest('iron_ore'))
harvest_resource(nearest('iron_ore'), quantity=5)
#stone_furnace_position = place_entity('stone-furnace', direction=DOWN, position=nearest('iron_ore'))
# move_to(nearest('iron_ore'))
#place_entity_next_to('burner-mining-drill', reference_position=stone_furnace_position, direction=LEFT, gap=1)

# Stone furnace is placed at a specific position
craft_item('steam-engine', quantity=1)

steam_engine_position = place_entity('steam-engine', direction=UP, position=(0,7))
craft_item('boiler', quantity=1)

# Place a burner-mining-drill to the left of the existing stone furnace
boiler_position = place_entity_next_to('boiler', reference_position=steam_engine_position, direction=UP, gap=2)

craft_item('pipe', quantity=2)

#inspect_entities(50)
# Connect the burner-mining-drill's output to the stone-furnace's input using an inserter
connect_entities(source_position=steam_engine_position, target_position=boiler_position, connection_type='pipe')
score()
"""

if __name__ == '__main__':

    import openai

    factorio_runner = FactorioRunner("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",
                                     #model="gpt-3.5-turbo",
                                     buffer_size=10,
                                     beam=1
                                     )
                                     #trace="15-17-01-04-2023")

    rcon = factorio_runner.instance.rcon_client
   # score = Score(rcon, )

    try:
        pass
        #factorio_runner.instance.eval(test)
    except Exception as e:
        print(e)

    #factorio_runner.replay()
    #for i in range(4):
    #    factorio_runner.instance.move_to((10, 10))
    #    factorio_runner.instance.move_to((0, 0))
    #factorio_runner.instance.craft_item('burner-mining-drill', quantity=2);
    #factorio_runner.instance.place_entity('stone-furnace', 2, (0, 0));
    #factorio_runner.instance.place('assembling-machine-1', 0, (1,1))
    #factorio_runner.instance.set_recipe((1, 1), 'iron-chest')
    #r = factorio_runner.instance.inspect()
    for i in range(400):
        next(factorio_runner)
    bar = getattr(instance, 'inventory')
    result = bar()

    start = timer()
    inventory = instance.check_inventory()
    description = instance.inspect_resources()
    inspect = instance.inspect_entities()

    try:
        # Let's craft some iron gear wheels first
        instance.craft_item('iron-gear-wheel', quantity=5)

        # Now, let's attempt to craft an assembling machine and transport belts again
        instance.craft_item('assembling-machine-1', quantity=1)
        instance.craft_item('transport-belt', quantity=10)
    except Exception as e:
        pass
    finally:
        result = instance.observe()
        score = result['score']

        pass

    groups = instance.inspect_resources()
    # instance.goto((0, -40))

    # instance.see('water', 'coal')

    for step in range(1000):
        # take random action, but you can also do something more intelligent
        instance.run_tasks()
        # if not path:
        # action = env.action_space.sample()
        #    print("Action: ", action)
        # apply the action
        # obs, reward, done, info = env.step(action)

        # path = goto((1,1), obs['local'])
        #    grid = obs['local'][0]

        #    path = goto((25, -100), grid)

        #    print(path)

        print("Step:", step)

    print(timer() - start)

    # env.step()
    # env.render()
