import math
import os
import time
from timeit import default_timer as timer

import numpy as np
from dotenv import load_dotenv
from numpy import ndarray, zeros
from slpp import slpp as lua

from client.factorio_client import FactorioClient
from client.utils import stitch

load_dotenv()

PLAYER = '1'
NONE = 'nil'
CHUNK_SIZE = 32
MAX_SAMPLES = 5000


class Factorio:

    def __init__(self, bounding_box=100):
        self.factorio_client = FactorioClient(remote_address=os.getenv("REMOTE_ADDRESS"),
                                              remote_password="eSei2keed0aegai")
        self.trail_state = {
            "trail_on": False,
            "trail_entity": None
        }
        self.vocabulary = {}
        self.vocabulary_state = {"index": 0}
        self.player_location = (0, 0)
        self.last_location = (0, 0)
        self.movement_vector = (0, 0)
        self.last_direction = -1
        self.bounding_box = bounding_box

        self.grid_world = zeros((bounding_box, bounding_box))

        self.minimap_bounding_box = bounding_box * 4

        mu, sigma = 0, CHUNK_SIZE * 20
        self.minimap_normal = s = np.random.normal(mu, sigma, MAX_SAMPLES)
        self.chunk_cursor = 0
        self.minimaps = self._initialise_minimaps()

    def _initialise_minimaps(self):
        bounding_box = self.minimap_bounding_box
        fields = ['all', 'enemy', 'pollution', 'factory', 'water', 'iron-ore', 'uranium-ore', 'coal', 'stone', 'copper-ore', 'crude-oil', 'trees']
        minimaps = {field: zeros((bounding_box, bounding_box)) for field in fields}
        return minimaps

    def initialise(self, **kwargs):
        # items, _ = factorio_client.send('get_item_vocabulary')
        self.factorio_client.send('initialise')
        self.factorio_client.send('new_world', PLAYER)
        self.factorio_client.send('clear_inventory', PLAYER)
        self.factorio_client.send('reset_position', PLAYER, 0, 0)

        for entity, count in kwargs.items():
            self.factorio_client.send('give_item', PLAYER, entity.replace("_", "-"), count)

        self.observe_local(trace=True)

    def interact(self, x: int = 0, y: int = 0) -> bool:
        """
        If there is an entity at local position (x, y), this action triggers an
        interaction as follows: If the item can be picked up, the agent picks up the item. If the
        item can be harvested, the agent harvests the item (resource). Here, the local position
        is the (x, y) position relative to the agent as the origin (0, 0). If there is no entity at
        (x, y), this action is a no-op.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :return: True if an action happened, False if no-op.
        """
        self.factorio_client.send('interact', PLAYER)
        time.sleep(0.2)
        return True

    def fuel(self, amount=5, x: int = 0, y: int = 0) -> int:
        """
        If there is an entity at local position (x, y) that accepts a resource, the agent
        adds a default amount of resource to the entity. If there is no entity at (x, y), this action
        is a no-op.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param amount: Amount of fuel to attempt to deposit
        :return: Amount of fuel deposited
        """
        self.factorio_client.send('fuel', PLAYER, 'coal', amount)

        return True

    def place(self, entity: str, direction: int, x: int = 0, y: int = 0) -> bool:
        """
        The agent places an entity e at local position (x, y) if the agent has
        enough resources. If the agent chooses to place an empty entity at (x, y), any entity at
        (x, y) is removed. If the agent chooses to place an entity where there is already one,
        the previous entity is first removed and the new entity replaces it.
        :param x: X position relative to the agent as the origin (0).
        :param y: Y position relative to the agent as the origin (0).
        :param entity: Entity to place from inventory
        :param direction: Cardinal direction to place entity
        :return: True if action carried out, False if no-op
        """
        cardinals = ['north', 'south', 'east', 'west']
        print(self.factorio_client.send('place', PLAYER, entity, cardinals[direction]))

        return True

    def trail(self, entity: str) -> bool:
        """
        The agent toggles placement mode, where an entity e is placed at the
        local position (x, y), and every subsequent position of the agent. Trail placement is
        toggled off once the agent runs out of resources, or if it chooses the action a second
        time with an empty entity. Trail placement is switched if the agent performs the action
        again with a different resource
         :param entity: The entity that is being toggled on.
        :return: Whether the action was carried out.
        """
        if entity:
            self.trail_state["trail_on"] = True
            self.trail_state["trail_entity"] = entity
        else:
            self.trail_state["trail_on"] = False
            self.trail_state["trail_entity"] = None

        return True

    def observe_statistics(self):
        """
        At each time t, statistics on the factory are returned
        :return:
        """
        response, execution_time = self.factorio_client.send('observe_performance', PLAYER)
        return response, execution_time

    def observe_position(self):
        """
        At each time t, the agent receives the agent’s current absolute position p.
        :return:
        """
        return self.factorio_client.send('observe_position', PLAYER)

    def observe_nearest_points_of_interest(self):
        """
        At each time t, the agent receives the positions of the nearest points of interest.
        :return:
        """
        return self.factorio_client.send('observe_points_of_interest', PLAYER, 200)

    def _sample_chunk_from_normal(self, player_offset):
        normal = self.minimap_normal[self.chunk_cursor % MAX_SAMPLES]
        offset = normal + player_offset
        self.chunk_cursor += 1
        return offset // CHUNK_SIZE

    def _sample_chunk(self):
        x = self._sample_chunk_from_normal(self.player_location[0])
        y = self._sample_chunk_from_normal(self.player_location[1])
        index_x = x + int(self.minimap_bounding_box / 2)
        index_y = y + int(self.minimap_bounding_box / 2)

        return int(x), int(y), int(index_x), int(index_y)

    def observe_chunk(self):
        """
        At each time t, the agent receives a downsampled version of the full environment, as chunks of
        32 x 32 tiles. Each chunk contains a density map of resources, enemies, water, player factory
        :return:
        """
        start = timer()
        chunk_x, chunk_y, index_x, index_y = self._sample_chunk()  # random.randrange(-50, -5) #int(chunk_map['pos']['x'] + self.minimap_bounding_box/2)
        # int(chunk_map['pos']['y'] + self.minimap_bounding_box/2)

        chunk_map, lua_execution_time = self.factorio_client.send('observe_chunk', PLAYER, chunk_x, chunk_y)

        if not chunk_map:
            raise Exception("Anonymous error from the server")

        if index_x >= self.minimap_bounding_box or index_y >= self.minimap_bounding_box or index_x < 0 or index_y < 0:
            return 0, lua_execution_time, timer() - start
        for type, count in chunk_map.items():
            if count == 0:
                continue
            self.minimaps[type][index_x, index_y] = count
            # self.minimaps[type][x, y] = count
        # for key, map in self.minimaps.items():
        #    x = chunk_map['pos']['x']
        #    y = chunk_map['pos']['x']
        #    for type, count in
        end = timer()
        return chunk_map, lua_execution_time, end - start

    def observe_inventory(self):
        """
        At each time t, the agent receives all entities in the agent’s inventory.
        :return:
        """
        return self.factorio_client.send('get_inventory', PLAYER)

    def observe_buildable(self):
        """
        At each time t, the agent receives all entities in the agent’s inventory.

        Menu of items including, those that exist in inventory (with quantity),
        and those that can be built (with zero quantity).
        :return:
        """

    def observe_local(self, trace=True):
        """
        At each time t, the agent receives all entities in a 100 × 100 grid centered on the agent’s position p. Each entity type is
        represented by a unique integer index.
        :return:
        """
        new_field_x, new_field_y = self.movement_vector[0], self.movement_vector[1]

        local_environment_sparse, execution_time = self.factorio_client.send('observe_local', PLAYER, self.bounding_box,
                                                                             new_field_x,
                                                                             new_field_y, lua.encode(trace), trace)
        # local_environment_sparse = response['localEnvironment']

        range_x = math.floor(new_field_x) if new_field_x else self.bounding_box
        range_y = math.floor(abs(new_field_y)) if new_field_y else self.bounding_box

        local_environment_dense, elapsed = self._get_dense_environment(range_x, range_y, local_environment_sparse)

        if new_field_y and not new_field_x:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, range_x))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (0, new_field_y))
        elif new_field_x and not new_field_y:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, range_x))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (new_field_x, 0))
        else:
            self.grid_world = np.reshape(local_environment_dense, (range_x, range_y))

        return local_environment_sparse, execution_time

    def _get_dense_environment(self, range_x, range_y, local_environment_sparse):
        local_environment_dense = []
        start = timer()
        for x in range(0, range_x):
            for y in range(0, range_y):
                index = x * range_y + y
                try:
                    item = local_environment_sparse[index]  # .replace("_", "-")
                    if item not in self.vocabulary.keys():
                        self.vocabulary[item] = self.vocabulary_state["index"]
                        self.vocabulary_state["index"] += 1
                    local_environment_dense.append(self.vocabulary[item])
                except Exception as e:
                    local_environment_dense.append(-1)
        end = timer()
        diff = (end - start)

        return np.array(local_environment_dense), diff

    def move(self, direction: int) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        self.last_location = self.player_location
        if self.trail_state['trail_on']:
            new_position, execution_time = self.factorio_client.send('move',
                                                                     PLAYER,
                                                                     direction,
                                                                     self.trail_state['trail_entity'])
            if new_position is 0:
                self.trail(None)

        else:
            new_position, execution_time = self.factorio_client.send('move',
                                                                     PLAYER,
                                                                     direction,
                                                                     NONE)
        if new_position:
            self.player_location = (new_position['x'], new_position['y'])
            self.last_direction = direction
            self.movement_vector = (
                self.player_location[0] - self.last_location[0], self.player_location[1] - self.last_location[1])
        return new_position
