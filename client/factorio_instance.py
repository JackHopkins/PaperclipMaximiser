import math
import os
import time
from timeit import default_timer as timer
from typing import List, Tuple

from matplotlib import pyplot as plt
from scipy import ndimage
from sklearn.cluster import DBSCAN
from collections import Counter

import numpy as np
import scipy
from dotenv import load_dotenv
from numpy import ndarray, zeros, sign, array
from skimage.measure import label
from sklearn.cluster import DBSCAN
from slpp import slpp as lua
from skimage import measure as sm
from client.factorio_rcon_utils import _load_actions, _load_init, _lua2python
from factorio_rcon import AsyncRCONClient

from client.rcon.factorio_rcon import RCONClient
from client.utils import stitch
from utilities.pathfinding import get_path
from vocabulary import Vocabulary

load_dotenv()

PLAYER = 1
NONE = 'nil'
CHUNK_SIZE = 32
MAX_SAMPLES = 5000
FIELDS = ['all', 'enemy', 'pollution', 'factory', 'water', 'iron-ore', 'uranium-ore', 'coal', 'stone',
          'copper-ore', 'crude-oil', 'trees']


class FactorioInstance:

    def __init__(self, address=None, vocabulary: Vocabulary = None, bounding_box=20, tcp_port=27015, inventory={}):
        self.tcp_port = tcp_port
        try:
            self.rcon_client = RCONClient(address, tcp_port, 'factorio')
            self.address = address
        except:
            self.rcon_client = RCONClient('localhost', tcp_port, 'factorio')
            self.address = 'localhost'

        self.script_dict = {**_load_actions(), **_load_init()}
        self.vocabulary = vocabulary
        self.trail_state = {
            "trail_on": False,
            "trail_entity": None
        }
        self.tasks = []
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

        self.connect()
        self.initialise(**inventory)

    def run_tasks(self):
        for task in self.tasks:
            try:
                next(task)()
            except StopIteration:
                self.observe()

    def nearest(self, type: str = 'coal'):
        response, time_elapsed = self._send('find', PLAYER, type)
        return -math.floor(response['x']), -math.floor(response['y'])

    def goto(self, relative_position: Tuple[int, int] = (0,0)):
        relative_end_x, relative_end_y = relative_position
        start_x, start_y = self.player_location
        offset = self.bounding_box // 2

        end = (offset+relative_end_x, offset+relative_end_y)
        #end = (offset-relative_end_x, offset-relative_end_y)
        path = get_path(end, self.collision_mask, start=(offset, offset))

        def direction_from_step(step):
            offset = self.bounding_box // 2
            return self.move(*((step - [offset, offset]) - self.player_location))

        task_queue = [(lambda s: direction_from_step(s + (start_x, start_y)))(s) for s in path]
        task_queue.append((lambda: self.observe())())

        self.tasks.append(iter(task_queue))

    def _initialise_minimaps(self):
        bounding_box = self.minimap_bounding_box
        # minimaps = {field: zeros((bounding_box, bounding_box)) for field in fields}

        return np.zeros((len(FIELDS), bounding_box, bounding_box))

    def reset(self, seed=None):
        pass

    def close(self):
        pass

    def _get_command(self, command, parameters=[], measured=True):
        prefix = "/c " if not measured else '/command '
        if command in self.script_dict:
            script = prefix + self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command
        return script

    def _send(self, command, *parameters, trace=False) -> List[str]:
        start = timer()
        script = self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = self.rcon_client.send_command(script)
        return _lua2python(command, lua_response, start=start)

    def connect(self):
        try:
            self.rcon_client.connect()
            player_exists, time_elapsed = self._send('/c rcon.print(game.players[1].position)', PLAYER)
            if not player_exists:
                raise Exception(
                    "Player hasn't been initialised into the game. Please log in once to make this node operational.")

        except Exception as e:
            raise ConnectionError(f"Could not connect to {self.address} at tcp/{self.tcp_port}: \n{e.args[0]}")

        print(f"Connected to {self.address} client at tcp/{self.tcp_port}.")

    def initialise(self, **kwargs):

        self._send('initialise', PLAYER)
        # self.factorio_client.send('new_world', PLAYER)
        self._send('clear_inventory', PLAYER)
        self._send('reset_position', PLAYER, 0, 0)

        for entity, count in kwargs.items():
            self._send('give_item', PLAYER, entity, count)

        try:
            results = self.observe(trace=True)
        except Exception as e:
            print(e)
            raise Exception(f"Could not initialise server at port {self.tcp_port}")

        return results

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
        self._send('interact', PLAYER)
        # time.sleep(0.2)
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
        self._send('fuel', PLAYER, 'coal', amount)

        return True

    def craft(self, entity: str, count: int = 1) -> bool:
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
        success = self._send('craft', PLAYER, entity, count)

        return success

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
        print(self._send('place', PLAYER, entity, cardinals[direction]))

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

    def _create_label_to_integer_mapping(self, labeled_matrix, original_matrix):
        label_to_integer = {}
        unique_labels = np.unique(labeled_matrix)

        for label in unique_labels:
            # Find the mask where the labeled_matrix has the current label
            label_mask = (labeled_matrix == label)

            # Get the unique integer values from the original matrix corresponding to the current label
            unique_values = np.unique(original_matrix[label_mask])

            # Assuming that there's only one unique integer value in the group
            original_integer = unique_values[0]
            label_to_integer[label] = original_integer

        return label_to_integer

    def _get_min_offsets(self, matrix, point):
        labeled_groups = np.unique(matrix)
        min_offsets = {}
        min_location = {}
        for label in labeled_groups:
            if label == 0:
                continue  # Skip background label

            # Get the coordinates of all points in the current labeled group
            group_points = np.argwhere(matrix == label)

            # Calculate the x and y offsets between the given point and all points in the group
            offsets = group_points - point

            # Get the smallest x and y offsets for the current group
            min_offsets[label] = np.min(np.abs(offsets), axis=0)
            min_location[label] = np.min(offsets, axis=0)

        return min_offsets

    import numpy as np

    def describe(self):
        unique_objects = np.unique(self.grid_world)

        groups = []
        for obj in unique_objects:
            if obj == 0:
                continue

            # Create a binary array for the current object type
            binary_array = (self.grid_world == obj).astype(int)

            # Get connected components for the current object type
            connected_components, num_labels = ndimage.measurements.label(binary_array)

            # Count object occurrences in each group
            for label in range(1, num_labels + 1):
                # Convert group data to a natural language description
                if obj == -1:
                    continue
                item = self.vocabulary.i_vocabulary[obj]

                group_indices = np.where(connected_components == label)
                group_size = len(group_indices[0])

                # Calculate group offset
                y_offset = int(np.mean(group_indices[0])) - (self.bounding_box//2)
                x_offset = int(np.mean(group_indices[1])) - (self.bounding_box//2)


                direction = f"{abs(y_offset)} metres {'north' if y_offset < 0 else 'south'}, and {abs(x_offset)} metres {'west' if x_offset < 0 else 'east'}"
                group_description = f"{direction} there is a patch of {item} of size {group_size}"

                groups.append((group_size, group_description))

        # Sort groups by size and return the result
        groups.sort(reverse=True, key=lambda x: x[0])
        return [group[1] for group in groups]

    def see(self, *args, width=10, height=10):
        """
        Convert the local environment into a small bitmap for orienting the controller.
        :return:
        """
        markers = ["+", "*", "%", "~"]
        to_see = list(args)

        if len(to_see) > len(markers):
            raise Exception("Trying to see too many items is not going to work.")

        important_indices = []
        for item, marker in zip(to_see, markers[:len(to_see)]):
            important_indices.append(self.vocabulary._update_vocabulary(item))

        def important(a, axis=None, out=None, keepdims=np._NoValue, initial=np._NoValue,
         where=np._NoValue):
           # counted, uniques = np.unique(a, return_counts=True)
            aa = np.unique(a, axis=axis)#, return_counts=True)
            modal = scipy.stats.mode(a)
            return 1

        labelled = label(self.grid_world, connectivity=1)
        reduced_arr = sm.block_reduce(self.grid_world, block_size=(10, 10), func=important)

        self.grid_world


    def observe(self, trace=False, **kwargs):
        """

        -Chunks: At each time t, the agent receives details of a chunks of 32 x 32 tiles sampled from the environment.
        Each chunk contains a density map of resources, enemies, water, player factory.

        -Local Environment: At each time t, the agent receives all entities in a 100 × 100 grid centered on the agent’s position p. Each entity type is
        represented by a unique integer index.

        -Position: At each time t, the agent receives the agent’s current absolute position p.

        -Points of interest: At each time t, the agent receives the relative positions of the nearest points of interest.

        :param trace:
        :param kwargs:
        :return:
        """
        chunk_x, chunk_y, index_x, index_y = self._sample_chunk()
        movement_field_x, movement_field_y = self.movement_vector[0], self.movement_vector[1]
        omit = kwargs
        response, execution_time = self._send('observe',
                                              PLAYER,
                                              chunk_x,
                                              chunk_y,
                                              self.bounding_box,
                                              movement_field_x,
                                              movement_field_y,
                                              200,
                                              trace,
                                              omit
                                              )

        if response['local_environment']:
            pass

        if not response:
            return

        if 'chunk' in response:
            self._index_chunk(response['chunk'], index_x, index_y)

        if 'local_environment' in response:
            self._convert_sparse_local_into_gridworld(response['local_environment'],
                                                      movement_field_x,
                                                      movement_field_y)

        if 'points_of_interest' in response:
            points_x, points_y, poi_time = self._convert_sparse_coordinates_into_tensors(response['points_of_interest'])

        if 'distance_to_points_of_interest' in response:
            distance_to_points_of_interest, dpoi_time = self._convert_sparse_continuous_into_tensor(
                response['distance_to_points_of_interest'], init=100000)

        if 'buildable' in response:
            buildable, build_time = self._convert_sparse_continuous_into_tensor(response['buildable'])

        if "collision" in response:
            collision_mask = self._collision_mask(response['collision'])

        # if 'objective' in response:
        #    objective, obj_time = await self._convert_sparse_continuous_into_tensor(response['objective'])

        return {
            "local": self.grid_world,
            "minimap": self.minimaps,  # Do not do this during observation - it is expensive!
            "compass": np.stack([points_x, points_y], axis=1),
            "buildable": buildable,
            "collision_mask": collision_mask
        }

    def observe_statistics(self):
        """
        At each time t, statistics on the factory are returned
        :return:
        """
        response, execution_time = self._send('observe_performance', PLAYER)
        return response, execution_time

    def observe_position(self):
        """
        At each time t, the agent receives the agent’s current absolute position p.
        :return:
        """
        return self._send('observe_position', PLAYER)

    def observe_nearest_points_of_interest(self):
        """
        At each time t, the agent receives the positions of the nearest points of interest.
        :return:
        """
        return self._send('observe_points_of_interest', PLAYER, 200)

    def _convert_sparse_continuous_into_tensor(self, local_counts: dict, init=0):
        start = timer()
        one_hot = np.full((256), init)  # zeros(256)

        for key, value in local_counts.items():
            index = self.vocabulary._update_vocabulary(key)
            one_hot[index] = value

        return np.reshape(one_hot, one_hot.shape + (1,)), timer() - start

    def _convert_sparse_coordinates_into_tensors(self, local_counts: dict):
        start = timer()
        one_hot_x = zeros(256)
        one_hot_y = zeros(256)

        for key, value in local_counts.items():
            lua_key = key.replace('_', '-')
            index = self.vocabulary._update_vocabulary(lua_key)
            one_hot_x[index] = value['x']
            one_hot_y[index] = value['y']
        end = timer() - start
        return np.reshape(one_hot_x, one_hot_x.shape + (1,)), np.reshape(one_hot_y, one_hot_y.shape + (1,)), end

    def _convert_sparse_local_into_gridworld(self, local_environment_sparse, new_field_x, new_field_y):
        print(new_field_x, new_field_y)
        new_field_x = new_field_y = False
        range_x = math.floor(new_field_x) if new_field_x else self.bounding_box
        range_y = math.floor(abs(new_field_y)) if new_field_y else self.bounding_box

        local_environment_dense, elapsed = self._get_dense_environment(range_x, range_y, local_environment_sparse)



        y, x = np.where(local_environment_dense == -2)

        new_field_y = new_field_y = False
        # If moving vertically
        if new_field_y and not new_field_x:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, self.bounding_box))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (0, new_field_y))
        # If moving horizontally
        elif new_field_x and not new_field_y:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, self.bounding_box))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (new_field_x, 0))
        else:
            self.grid_world = np.reshape(local_environment_dense, (range_x, range_y))

        #self.grid_world = np.fliplr(self.grid_world)

        plt.imshow(np.array(self.grid_world, dtype="float"), cmap='gray', interpolation='nearest')
        plt.show()

        v = 1
        #dense_array[::-1, :]
        #y, x = np.where(self.grid_world == -2)

        #self.grid_world = self.grid_world[
        #    90: 100,
        #    90: 100
        #]
        #y, x = np.where(self.grid_world == -2)


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

    def _index_chunk(self, chunk_map, index_x, index_y):
        if not chunk_map:
            raise Exception("Anonymous error from the server")

        if index_x >= self.minimap_bounding_box or index_y >= self.minimap_bounding_box or index_x < 0 or index_y < 0:
            return 0
        for type, count in chunk_map.items():
            if count == 0:
                continue
            self.minimaps[self._get_type_index(type)][index_x, index_y] = count
        return chunk_map

    def _get_type_index(self, type):
        return FIELDS.index(type)

    def _get_dense_environment(self, range_x, range_y, local_environment_sparse):
        local_environment_dense = []
        start = timer()

        dense_array = np.full((range_y, range_x), -1, dtype=object)

        # Populate the dense array using the sparse dictionary
        for key, value in local_environment_sparse.items():
            if key > range_y*range_x:
                break

            row = key // range_y
            col = key % range_y
            dense_array[math.floor(row), math.floor(col)] = self.vocabulary._update_vocabulary(value)
        end = timer()
        diff = (end - start)

        return dense_array, diff

    def _move(self, direction: int):
        return self._send('move',
                          PLAYER,
                          direction,
                          self.trail_state['trail_entity'])

    def _collision_mask(self, sparse_collision_mask):

        dense_array = np.full((self.bounding_box, self.bounding_box), 1, dtype=object)

        # Populate the dense array using the sparse dictionary
        for key, value in sparse_collision_mask.items():
            #key = key - (self.bounding_box)*(self.bounding_box/2)
            col = math.floor((key // self.bounding_box)) - self.player_location[1]
            row = math.floor((key % self.bounding_box)) - self.player_location[0]
            d = self.player_location
            if row >= self.bounding_box or col >= self.bounding_box or col <= 0 or row <= 0:
                pass
            try:
                dense_array[col, row] = value
            except Exception as e:
                pass

        plt.imshow(np.array(dense_array, dtype="float"), cmap='gray', interpolation='nearest')
        plt.show()
        #dense_array = np.flipud(dense_array)
        self.collision_mask = dense_array
        return dense_array

    def move(self, x: int, y: int) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        self.last_location = self.player_location
        if self.trail_state['trail_on']:
            new_position, execution_time = self._send('move',
                                                      PLAYER,
                                                      x,
                                                      y,
                                                      self.trail_state['trail_entity'])
            if new_position is 0:
                self.trail(None)

        else:
            new_position, execution_time = self._send('move',
                                                      PLAYER,
                                                      x,
                                                      y,
                                                      NONE)

        if new_position:
            self.player_location = (new_position['x'], new_position['y'])
            #self.last_direction = direction
            self.movement_vector = (self.player_location[0] - self.last_location[0],
                                    self.player_location[1] - self.last_location[1])

        return new_position, execution_time
        # results['new_position'] = new_position
    # results['execution_time'] = execution_time
    # return new_position, execution_time
