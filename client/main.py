
from client.factorio import Factorio
from client.utils import render_images

factorio = Factorio(bounding_box=100)
factorio.initialise(pipe=50)
factorio.trail('pipe')

for k in range(50000):
    #[factorio.move(random.randrange(0, 4)) for i in range(2)]
    factorio.move(1)
    #response, execution = factorio.observe_local(trace=True)
    response, _, _ = factorio.observe_chunk()
    statistics, lua_execution = factorio.observe_statistics()
    #print(len(response['localEnvironment']))
    #print(response['localEnvironment'])
    print(k, lua_execution, statistics)
    #[move(0) for i in range(10)]
    #[move(2) for i in range(10)]
    #[move(1) for i in range(10)]
    #[move(3) for i in range(10)]

render_images(factorio)

factorio.trail(None)
    #[move(random.randrange(0, 3)) for i in range(10)]
#    place('iron-chest', 0)