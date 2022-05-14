import math
import os
import time
from timeit import default_timer as timer
from typing import List

import numpy as np
from dotenv import load_dotenv
from numpy import ndarray, zeros
from slpp import slpp as lua

from client.factorio_rcon_utils import _load_actions, _load_init, _lua2python
from factorio_rcon import AsyncRCONClient
from client.utils import stitch

load_dotenv()

PLAYER = 1
NONE = 'nil'
CHUNK_SIZE = 32
MAX_SAMPLES = 5000


class FactorioInstance:

    def __init__(self, address, update_vocabulary, get_vocabulary, bounding_box=100, tcp_port=27015):
        self.tcp_port = tcp_port
        try:
            self.rcon_client = AsyncRCONClient(address, tcp_port, 'factorio')
            self.address = address
        except:
            self.rcon_client = AsyncRCONClient('localhost', tcp_port, 'factorio')
            self.address = 'localhost'

        self.script_dict = {**_load_actions(), **_load_init()}

        self.trail_state = {
            "trail_on": False,
            "trail_entity": None
        }
        self.update_vocabulary = update_vocabulary
        self.get_vocabulary = get_vocabulary
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
        fields = ['all', 'enemy', 'pollution', 'factory', 'water', 'iron-ore', 'uranium-ore', 'coal', 'stone',
                  'copper-ore', 'crude-oil', 'trees']
        minimaps = {field: zeros((bounding_box, bounding_box)) for field in fields}
        return minimaps


    async def _get_command(self, command, parameters=[], measured=True):
        prefix = "/c " if not measured else '/command '
        if command in self.script_dict:
            script = prefix + self.script_dict[command]
            for index in range(len(parameters)):
                script = script.replace(f"arg{index + 1}", lua.encode(parameters[index]))
        else:
            script = command

        return script

    async def _send(self, command, *parameters, trace=False) -> List[str]:
        script = await self._get_command(command, parameters=list(parameters), measured=False)
        lua_response = await self.rcon_client.send_command(script)
        return await _lua2python(command, lua_response)

    async def connect(self):
        try:
            await self.rcon_client.connect()
            player_exists, time_elapsed = await self._send('/c rcon.print(game.players[1].position)', PLAYER)
            if not player_exists:
                raise Exception(
                    "Player hasn't been initialised into the game. Please log in once to make this node operational.")

        except Exception as e:
            raise ConnectionError(f"Could not connect to {self.address} at tcp/{self.tcp_port}: \n{e.args[0]}")

        print(f"Connected to {self.address} client at tcp/{self.tcp_port}.")

    async def initialise(self, **kwargs):

        await self._send('initialise', PLAYER)
        # self.factorio_client.send('new_world', PLAYER)
        await self._send('clear_inventory', PLAYER)
        await self._send('reset_position', PLAYER, 0, 0)

        for entity, count in kwargs.items():
            await self._send('give_item', PLAYER, entity, count)

        results = {}
        try:
            await self.observe(results, trace=True)
        except Exception as e:
            print(e)

        return

    async def interact(self, x: int = 0, y: int = 0) -> bool:
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
        time.sleep(0.2)
        return True

    async def fuel(self, amount=5, x: int = 0, y: int = 0) -> int:
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

    async def place(self, entity: str, direction: int, x: int = 0, y: int = 0) -> bool:
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

    async def trail(self, entity: str) -> bool:
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

    async def observe(self, result, callback, trace=False, **kwargs):
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
        response, execution_time = await self._send('observe',
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

        if not response:
            pass

        if 'chunk' in response:
            await self._index_chunk(response['chunk'], index_x, index_y)

        if 'local_environment' in response:
            await self._convert_sparse_local_into_gridworld(response['local_environment'], movement_field_x,
                                                            movement_field_y)

        if 'points_of_interest' in response:
            points_x, points_y, poi_time = await self._convert_sparse_coordinates_into_tensors(response['points_of_interest'])

        if 'distance_to_points_of_interest' in response:
            distance_to_points_of_interest, dpoi_time = await self._convert_sparse_continuous_into_tensor(response['distance_to_points_of_interest'], init=100000)

        if 'buildable' in response:
            buildable, build_time = await self._convert_sparse_continuous_into_tensor(response['buildable'])

        #dense_minimap = np.stack(self.minimaps.values())

        #if 'objective' in response:
        #    objective, obj_time = await self._convert_sparse_continuous_into_tensor(response['objective'])

        #stacked = np.stack([points_x, points_y, distance_to_points_of_interest, buildable], axis=1)
        #result['response'] = {
        #
        #}
        #result['execution_time'] = execution_time
        result['response'] = [self.grid_world, *self.minimaps.values(), points_x, points_y, distance_to_points_of_interest, buildable]
        callback.set()

    async def observe_statistics(self):
        """
        At each time t, statistics on the factory are returned
        :return:
        """
        response, execution_time = self._send('observe_performance', PLAYER)
        return response, execution_time

    async def observe_position(self):
        """
        At each time t, the agent receives the agent’s current absolute position p.
        :return:
        """
        return self._send('observe_position', PLAYER)

    async def observe_nearest_points_of_interest(self):
        """
        At each time t, the agent receives the positions of the nearest points of interest.
        :return:
        """
        return self._send('observe_points_of_interest', PLAYER, 200)


    async def _convert_sparse_continuous_into_tensor(self, local_counts: dict, init=0):
        start = timer()
        one_hot = np.full((256), init) #zeros(256)

        for key, value in local_counts.items():
            index = self.update_vocabulary(key)
            one_hot[index] = value

        return np.reshape(one_hot, one_hot.shape + (1,)), timer() - start


    async def _convert_sparse_coordinates_into_tensors(self, local_counts: dict):
        start = timer()
        one_hot_x = zeros(256)
        one_hot_y = zeros(256)

        for key, value in local_counts.items():
            lua_key = key.replace('_', '-')
            index = self.update_vocabulary(lua_key)
            one_hot_x[index] = value['x']
            one_hot_y[index] = value['y']
        end = timer() - start
        return np.reshape(one_hot_x, one_hot_x.shape + (1,)), np.reshape(one_hot_y, one_hot_y.shape + (1,)), end


    async def _convert_sparse_local_into_gridworld(self, local_environment_sparse, new_field_x, new_field_y):
        range_x = math.floor(new_field_x) if new_field_x else self.bounding_box
        range_y = math.floor(abs(new_field_y)) if new_field_y else self.bounding_box

        local_environment_dense, elapsed = await self._get_dense_environment(range_x, range_y, local_environment_sparse)

        if new_field_y and not new_field_x:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, range_x))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (0, new_field_y))
        elif new_field_x and not new_field_y:
            local_environment_2d: ndarray = np.reshape(local_environment_dense, (-1, range_x))
            self.grid_world = stitch(self.grid_world, local_environment_2d, (new_field_x, 0))
        else:
            self.grid_world = np.reshape(local_environment_dense, (range_x, range_y))

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

    async def _index_chunk(self, chunk_map, index_x, index_y):
        if not chunk_map:
            raise Exception("Anonymous error from the server")

        if index_x >= self.minimap_bounding_box or index_y >= self.minimap_bounding_box or index_x < 0 or index_y < 0:
            return 0
        for type, count in chunk_map.items():
            if count == 0:
                continue
            self.minimaps[type][index_x, index_y] = count
        return chunk_map

    async def _get_dense_environment(self, range_x, range_y, local_environment_sparse):
        local_environment_dense = []
        start = timer()
        for x in range(0, range_x):
            for y in range(0, range_y):
                index = x * range_y + y
                try:
                    item = local_environment_sparse[index]  # .replace("_", "-")
                    item_index = self.update_vocabulary(item)
                    local_environment_dense.append(item_index)
                except Exception as e:
                    local_environment_dense.append(-1)
        end = timer()
        diff = (end - start)

        return np.array(local_environment_dense), diff

    async def _move(self, direction: int):
        return await self._send('move',
                                PLAYER,
                                direction,
                                self.trail_state['trail_entity'])

    async def move(self, results: dict, direction: int) -> bool:
        """
        The agent moves in a cardinal direction.
        :param direction: Index between (0,3) inclusive.
        :return: Whether the movement was carried out.
        """
        self.last_location = self.player_location
        if self.trail_state['trail_on']:
            new_position, execution_time = await self._send('move',
                                                            PLAYER,
                                                            direction,
                                                            self.trail_state['trail_entity'])
            if new_position is 0:
                self.trail(None)

        else:
            new_position, execution_time = await self._send('move',
                                                            PLAYER,
                                                            direction,
                                                            NONE)

        if new_position:
            self.player_location = (new_position['x'], new_position['y'])
            self.last_direction = direction
            self.movement_vector = (self.player_location[0] - self.last_location[0],
                                    self.player_location[1] - self.last_location[1])

        results['new_position'] = new_position
        results['execution_time'] = execution_time
        # return new_position, execution_time
