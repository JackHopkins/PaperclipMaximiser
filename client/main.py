import time
from multiprocessing import Lock, Manager
from timeit import default_timer as timer
# from gym.envs.registration import register

import gym
from anyio import run, move_on_after
from anyio import create_task_group, TASK_STATUS_IGNORED
from anyio.abc import TaskStatus
from joblib._multiprocessing_helpers import mp

#from client.factorio_pool import FactorioPool
from multiprocessing import Pool, Process

#!/usr/bin/env python3
from functools import partial
from itertools import repeat
from multiprocessing import Pool, freeze_support

from .envs import *

#factorio_pool = FactorioPool(instance=2, bounding_box=64, tcp_port=27016, pipe=50, copper_plate=10, iron_plate=10)

#a_args = [1,2,3]
#second_arg = 1

#factorio_pool.get(0).trail('pipe')

#factorio_pool.map([0,1,2,3], ['a', 'b', 'c', 'd'])

    #with Pool(2) as pool:
    #    start_time = time.perf_counter()
    #    L = pool.starmap(func, [(factorio_pool.get(0), 1), (factorio_pool.get(1), 1)])
    #    end_time = time.perf_counter()
    #    print(start_time-end_time)
        #M = pool.starmap(func, zip(a_args, repeat(second_arg)))
        #N = pool.map(partial(func, b=second_arg), a_args)
        #assert L == M == N


#exit(0)
#factorio = FactorioInstance(bounding_box=64, tcp_port=27015)
#factorio.initialise(pipe=50, copper_plate=10, iron_plate=10)

#factorio_pool.get(0).trail('pipe')

#factorio_pool.get(1).trail('pipe')

observe_local_times = []
iterations = 100

async def main():
    servers = 4

    factorio_pool = None#FactorioPool(servers, 64, 27016)
    await factorio_pool.connect()
    await factorio_pool.initialise(iron_ore=20)
    iterations = 1000
    time = timer()
    for i in range(iterations):
        await factorio_pool.act('move', 2)
        responses = await factorio_pool.observe()
        #print(responses)
        #[tg.start_soon(instance.move, 1) for instance in factorio_pool.instances]

    end = (timer() - time)
    print(f"Async: servers={servers} seconds_elapsed={end}, iterations_ps={(timer() - time) / iterations} command_throughput={1/(((timer() - time) / iterations) / servers)}")

#run(main)

#for k in range(iterations):
    #[factorio.move(random.randrange(0, 4)) for i in range(2)]

    #with Pool(2) as p:
    #    print(p.map(f, [factorio_pool.get(0).move, factorio_pool.get(1).move]))

    #for i in range(1):
    #    new_position, move_time_1 = factorio_pool.get(0).move(1)
     #   local, observe_time = factorio_pool.get(0).observe(trace=False)
   #     observe_local_times.append(observe_time)
    #print(observe_time)
    #print(k, sum([move_time, observe_local_time, observe_chunk_time, observe_inventory_time, observe_buildable_time, observe_nearest_points_of_interest_time, observe_statistics_time]))

#print("---")
#print(timer()-start)
#observe_local_time_mean = sum(observe_local_times) / iterations
#print(observe_local_time_mean)
#exit(0)


#173 - no points of interest
#187 - points of interest


#render_images(factorio)

#factorio.trail(None)
    #[move(random.randrange(0, 3)) for i in range(10)]
#    place('iron-chest', 0)

class Vocabulary:

    def __init__(self):
        self.mutex = Lock()

        self.vocabulary = {}
        self.i_vocabulary = {}

    def _get_vocabulary(self):
        return self.vocabulary, self.i_vocabulary

    def _update_vocabulary(self, item):
        """
        Including a mutex to ensure that the vocabulary is managed in a threadsafe way.
        Otherwise, two processes may allocate different items to the same index.
        """
        with self.mutex:
            keys = self.vocabulary.keys()
            next_index = len(keys)
            if item not in keys:
                self.vocabulary[item] = next_index
                self.i_vocabulary[next_index] = item
                print(f"vocab: {item} = {next_index}")

        return self.vocabulary[item]


if __name__ == '__main__':

    freeze_support()
    vocabulary = Vocabulary()
    inventory = {
        'coal': 50
    }
    env = gym.vector.AsyncVectorEnv([
        lambda: gym.make("Factorio-v0", address='localhost', vocabulary=vocabulary, bounding_box=100, tcp_port=27016, inventory=inventory),
        # lambda: gym.make("Factorio-v0", address='localhost', vocabulary=vocabulary, bounding_box=100, tcp_port=27017, inventory=inventory),
        #lambda: gym.make("Factorio-v0", address='localhost', vocabulary=vocabulary, bounding_box=100, tcp_port=27018, inventory=inventory),
        #lambda: gym.make("Factorio-v0", address='localhost', vocabulary=vocabulary, bounding_box=100, tcp_port=27019, inventory=inventory)
    ])
    env.reset()
    start = timer()
    for step in range(1000):
        # take random action, but you can also do something more intelligent
        action = env.action_space.sample()
        print("Action: ", action)
        # apply the action
        obs, reward, done, info = env.step(action)
        print("Step:", step)

    print(timer() - start)

    #env.step()
    #env.render()