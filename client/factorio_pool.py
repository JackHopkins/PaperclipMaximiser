from multiprocessing import Pool, freeze_support

from anyio import create_task_group

from client.factorio_instance import FactorioInstance
from client.utils import print_timing


class FactorioPool:

    def __init__(self, instance_num=2, bounding_box=64, tcp_port=27015):
        self.instances = self._create(instance_num, bounding_box, tcp_port)

    async def connect(self):
        for instance in self.instances:
            await instance.connect()

    async def initialise(self, **kwargs):
        for instance in self.instances:
            await instance.initialise(**kwargs)

    @print_timing
    async def act(self, action, *args):
        async with create_task_group() as tg:
            [tg.start_soon(instance.move, *args) for instance in self.instances]

        print(action, args)

    def _create(self, instance_num, bounding_box=64, tcp_port=27015):
        instances = []
        for i in range(instance_num):
            port = tcp_port+i
            instance = FactorioInstance('localhost', bounding_box, port)
            instances.append(instance)
        return instances

    def map(self, actions, args):
        self.pool.map(self._act, zip(actions, args))

    def get(self, index):
        return self.instances[index]

