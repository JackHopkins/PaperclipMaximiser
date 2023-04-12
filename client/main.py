# !/usr/bin/env python3
import queue
from multiprocessing import freeze_support
from timeit import default_timer as timer

# factorio_pool.get(1).trail('pipe')
from factorio_instance import FactorioInstance
from factorio_runner import FactorioRunner
from vocabulary import Vocabulary

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
place('assembling-machine-1', 0, (1,1)) # places at 1m north and east of the player, facing north.
wait(5) # wait 5 seconds.
insert('coal', (0, 0), count=1) # inserts 1 coal into nearby entity from inventory
extract('coal', (0, 1), count=1) # picks up 1 coal from the entity 1m to the south
set_recipe('iron-chest') # set recipe of nearby entity to craft 'iron-chest'
goto((0, -40)) # move north 40 metres
goto(nearest('tree')) # move to the nearest tree
interact((-2, 0), count=5) # harvest or mine 5 of the entity under the player
rotate((0,0), 1) # rotate nearby entity to face east
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


if __name__ == '__main__':

    import os
    import openai

    factorio_runner = FactorioRunner("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",)
                                     #model="gpt-3.5-turbo")
                                     #trace="15-17-01-04-2023")
    #factorio_runner.replay()
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
    description = instance.observe_nature()
    inspect = instance.inspect_radius()

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

    groups = instance.observe_nature()
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
