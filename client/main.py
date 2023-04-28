# !/usr/bin/env python3
from timeit import default_timer as timer
from factorio_runner import FactorioRunner

observe_local_times = []
iterations = 100



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



test = \
"""
ore = nearest("coal")
craft_item('burner-inserter', quantity=4)
place_entity('burner-inserter', direction=LEFT, position=(ore[0]-15,ore[1]))
place_entity('burner-inserter', direction=RIGHT, position=(ore[0]+5,ore[1]))
place_entity('burner-inserter', direction=UP, position=(ore[0],ore[1]-15))
place_entity('burner-inserter', direction=DOWN, position=(ore[0],ore[1]+5))

craft_item('burner-mining-drill', quantity=1)
place_entity('burner-mining-drill', direction=LEFT, exact=True, position=(ore[0]-5,ore[1]))
place_entity('burner-mining-drill', direction=RIGHT, exact=True, position=(ore[0],ore[1]))
#place_entity('burner-mining-drill', direction=UP, position=(ore[0],ore[1]-15))
#place_entity('burner-mining-drill', direction=DOWN, position=(ore[0],ore[1]+5))

place_entity('transport-belt', direction=LEFT, position=(ore[0]-14,ore[1]))
place_entity('transport-belt', direction=RIGHT, position=(ore[0]+4,ore[1]))
place_entity('transport-belt', direction=UP, position=(ore[0],ore[1]-14))
place_entity('transport-belt', direction=DOWN, position=(ore[0],ore[1]+4))
inspect_entities(5)
"""

if __name__ == '__main__':

    import openai

    factorio_runner = FactorioRunner("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",
                                     #model="gpt-3.5-turbo",
                                     buffer_size=16,
                                     beam=1
                                     )
                                     #trace="15-17-01-04-2023")

    rcon = factorio_runner.instance.rcon_client

    try:
        #factorio_runner.instance.eval(test)
        pass
    except Exception as e:
        print(e)

    for i in range(400):
        next(factorio_runner)
