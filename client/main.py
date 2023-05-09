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

ore = nearest("stone")
five = place_entity('burner-mining-drill', position=ore)
six = place_entity_next_to('stone-furnace', reference_position=ore, direction=LEFT, gap=1)
connect_entities(connection_type="burner-inserter", source_position=five, target_position=six)

#seven = place_entity('stone-furnace', position=(ore[0]-8, ore[1]+8))
#connect_entities(source_position=five, target_position=seven)

#eight = place_entity('stone-furnace', position=(ore[0]+8, ore[1]-8))
#connect_entities(source_position=five, target_position=eight)

#nine = place_entity('stone-furnace', position=(ore[0]-8, ore[1]-8))
#connect_entities(source_position=five, target_position=nine)

#ore = nearest("coal")
#entity_pos = place_entity('iron-chest', position=ore)

#one = place_entity_next_to('stone-furnace', reference_position=entity_pos, direction=UP, gap=5)
#two = place_entity_next_to('stone-furnace', reference_position=entity_pos, direction=RIGHT, gap=3)
#three = place_entity_next_to('stone-furnace', reference_position=entity_pos, direction=DOWN, gap=2)
#four = place_entity_next_to('stone-furnace', reference_position=entity_pos, direction=LEFT, gap=6)

#connect_entities(source_position=one, target_position=entity_pos)
#connect_entities(source_position=two, target_position=entity_pos)
#connect_entities(source_position=three, target_position=entity_pos)
#connect_entities(source_position=four, target_position=entity_pos)


#place_entity_next_to('stone-furnace', reference_position=ore, direction=UP, gap=1)
#place_entity_next_to('stone-furnace', reference_position=ore, direction=RIGHT, gap=1)
#place_entity_next_to('stone-furnace', reference_position=ore, direction=DOWN, gap=1)
#place_entity_next_to('stone-furnace', reference_position=ore, direction=LEFT, gap=1)
"""

if __name__ == '__main__':

    inventory = {
        'coal': 50,
        'copper-plate': 50,
        'iron-plate': 50,
        'iron-chest': 1,
        'burner-mining-drill': 1,
        'assembling-machine-1': 1,
        'stone-furnace': 1,
        #'small-electric-pole': 10,
        'transport-belt': 50,
        #'pipe': 50
    }

    factorio_runner = FactorioRunner("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",
                                     model="gpt-3.5-turbo",
                                     inventory=inventory,
                                     buffer_size=16,
                                     beam=1
                                     )
                                     #trace="15-17-01-04-2023")

    rcon = factorio_runner.instance.rcon_client

    try:
        #factorio_runner.instance.eval("move_to((-5, -5))")
        factorio_runner.instance.eval(test)
        #pass
    except Exception as e:
        print(e)

    for i in range(400):
        next(factorio_runner)
