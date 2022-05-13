from threading import Lock
from anyio import create_task_group

from client.factorio_instance import FactorioInstance
from client.utils import print_timing


class FactorioPool:

    def __init__(self, instance_num=2, bounding_box=64, tcp_port=27015):
        self.mutex = Lock()
        self.instances = self._create(instance_num, bounding_box, tcp_port)
        self.vocabulary = {}
        self.i_vocabulary = {}

    def _update_vocabulary(self, item):
        """
        Including a mutex to ensure that the vocabulary is managed in a threadsafe way.
        Otherwise, two processes may allocate different items to the same index.
        """
        self.mutex.acquire()
        try:
            keys = self.vocabulary.keys()
            next_index = len(keys)
            if item not in keys:
                self.vocabulary[item] = next_index
                self.i_vocabulary[next_index] = item
                print(f"vocab: {item} = {next_index}")
        finally:
            self.mutex.release()
        return self.vocabulary[item]

    def _create(self, instance_num, bounding_box=64, tcp_port=27015):
        instances = []
        for i in range(instance_num):
            port = tcp_port+i
            instance = FactorioInstance('localhost', self._update_vocabulary, bounding_box, port)
            instances.append(instance)
        return instances

    async def connect(self):
        for instance in self.instances:
            await instance.connect()

    async def initialise(self, **kwargs):
        for instance in self.instances:
            await instance.initialise(**kwargs)


    @print_timing
    async def act(self, action, *args):
        results = {}
        async with create_task_group() as tg:
            for i, instance in enumerate(self.instances):
                results[i] = {}
                tg.start_soon(instance.move, results[i], *args)
        print(action, args, results)
        return results

    @print_timing
    async def observe(self, *args):
        results = {}
        async with create_task_group() as tg:
            for i, instance in enumerate(self.instances):
                results[i] = {}
                tg.start_soon(instance.observe, results[i], *args)
        print('observe', args, results)
        return results


