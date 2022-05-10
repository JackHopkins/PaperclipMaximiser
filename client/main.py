
from client.factorio import Factorio
from client.utils import render_images

factorio = Factorio(bounding_box=100)
factorio.initialise(pipe=50)
factorio.trail('pipe')

for k in range(50000):
    #[factorio.move(random.randrange(0, 4)) for i in range(2)]
    factorio.move(1)
    local, observe_local_time = factorio.observe_local(trace=False)
    chunk, observe_chunk_time, _ = factorio.observe_chunk()
    position, observe_position_time = factorio.observe_position()
    inventory, observe_inventory_time = factorio.observe_inventory()
    points_of_interest, observe_nearest_points_of_interest_time = factorio.observe_nearest_points_of_interest()
    statistics, observe_statistics__time = factorio.observe_statistics()
    #print(len(response['localEnvironment']))
    #print(response['localEnvironment'])
    print(k, observe_chunk_time, statistics)
    #[move(0) for i in range(10)]
    #[move(1) for i in range(10)]
    #[move(3) for i in range(10)]

render_images(factorio)

factorio.trail(None)
    #[move(random.randrange(0, 3)) for i in range(10)]
#    place('iron-chest', 0)