
from client.factorio import Factorio
from client.utils import render_images

factorio = Factorio(bounding_box=100)
factorio.initialise(pipe=50, copper_plate=10, iron_plate=10)
factorio.trail('pipe')
observe_local_times = []

for k in range(1000):
    #[factorio.move(random.randrange(0, 4)) for i in range(2)]
    new_position, move_time = factorio.move(1)
    local, observe_time = factorio.observe()
    #chunk, observe_chunk_time, _ = factorio.observe_chunk()
    #position, observe_position_time = factorio.observe_position()
    #inventory, observe_inventory_time = factorio.observe_inventory()
    #buildable, observe_buildable_time = factorio.observe_buildable()
    #points_of_interest, observe_nearest_points_of_interest_time = factorio.observe_nearest_points_of_interest()
    #statistics, observe_statistics_time = factorio.observe_statistics()
    observe_local_times.append(observe_time)
    print(local)
    #print(k, sum([move_time, observe_local_time, observe_chunk_time, observe_inventory_time, observe_buildable_time, observe_nearest_points_of_interest_time, observe_statistics_time]))

observe_local_time_mean = sum(observe_local_times) / len(observe_local_times)
print(observe_local_time_mean)
exit(0)


#173 - no points of interest
#187 - points of interest


render_images(factorio)

factorio.trail(None)
    #[move(random.randrange(0, 3)) for i in range(10)]
#    place('iron-chest', 0)