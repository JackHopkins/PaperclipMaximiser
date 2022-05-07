import random

from client.actions import move, place

for k in range(1000):
    #[move(random.randrange(0, 3)) for i in range(10)]
    place('iron-chest', 0)