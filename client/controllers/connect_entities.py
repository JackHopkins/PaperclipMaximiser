import math

import numpy
import numpy as np

from controllers._action import Action
from typing import Tuple, List

from factorio_entities import Entity, Boiler, FluidHandler, Position, Generator, Inserter, MiningDrill
from factorio_instance import PLAYER
from factorio_types import Prototype


class ConnectEntities(Action):

    def __init__(self, *args):
        super().__init__(*args)

    def _get_nearest_connection_point(self,
                                      fluid_handler_source: FluidHandler,
                                      existing_connection_position: Position,
                                      existing_connection_entity: Entity):
        existing_offset_x = existing_connection_position.x - existing_connection_entity.position.x
        existing_offset_y = existing_connection_position.y - existing_connection_entity.position.y

        # By default, select the first connection point
        nearest_connection_point = fluid_handler_source.connection_points[0]
        nearest_distance = 10000000  # Large value

        for connection_point in fluid_handler_source.connection_points:
            possible_offset_x = connection_point.x - fluid_handler_source.position.x
            possible_offset_y = connection_point.y - fluid_handler_source.position.y

            # Calculate directional components
            dir_x = np.sign(possible_offset_x - existing_offset_x)
            dir_y = np.sign(possible_offset_y - existing_offset_y)

            # Check if points are facing each other
            if dir_x == 0 and dir_y == 0:  # They are on top of each other, so just return this point
                return connection_point
            elif dir_x == 0 and possible_offset_y * dir_y < 0:  # They are vertically aligned and facing each other
                continue
            elif dir_y == 0 and possible_offset_x * dir_x < 0:  # They are horizontally aligned and facing each other
                continue
            elif possible_offset_x * dir_x < 0 and possible_offset_y * dir_y < 0:  # They are diagonally aligned and facing each other
                continue

            # Calculate distance
            distance = abs(connection_point.x - existing_connection_position.x) + abs(
                connection_point.y - existing_connection_position.y)

            # Update if this distance is smaller
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_connection_point = connection_point

        return nearest_connection_point

    def _get_nearest_connection_point2(self,
                                      fluid_handler_source: FluidHandler,
                                      existing_connection_position: Position,
                                      existing_connection_entity: Entity):
        #existing_connection_position = existing_connection_entity.position
        existing_offset_x = existing_connection_position.x - existing_connection_entity.position.x
        existing_offset_y = existing_connection_position.y - existing_connection_entity.position.y

        nearest_connection_point = None
        nearest_distance = 10000000

        for connection_point in fluid_handler_source.connection_points:
            possible_offset_x = connection_point.x - fluid_handler_source.position.x
            possible_offset_y = connection_point.y - fluid_handler_source.position.y

            # If X axis is 0, then the Y axis offsets must be different (i.e 'facing' each other)
            if (connection_point.x == existing_connection_position.x):
                # They are facing each other, so continue
                if possible_offset_y / existing_offset_y > 0:
                    continue
            # If Y axis is 0, then the X axis offsets must be different (i.e 'facing' each other)
            elif (connection_point.y == existing_connection_position.y):
                if possible_offset_x / existing_offset_x > 0:
                    continue
            else:
                # continue if the sign of the offsets are not the same
                if (existing_offset_x > 0 and possible_offset_x < 0) or (existing_offset_x < 0 and possible_offset_x > 0):
                    continue
                if (existing_offset_y > 0 and possible_offset_y < 0) or (existing_offset_y < 0 and possible_offset_y > 0):
                    continue
                #pass

            distance = abs(connection_point.x - existing_connection_position.x) + abs(
                connection_point.y - existing_connection_position.y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_connection_point = connection_point

        return nearest_connection_point

    def _get_nearest_connection_point2(self, fluid_handler_source: FluidHandler, fluid_handler_target: FluidHandler, position: Position):
        nearest_distance = 10000000
        nearest_connection_point = None
        for target_connection_point in fluid_handler_target.connection_points:
            #normal_x = (target_connection_point.x - position.x) / abs(target_connection_point.x - position.x)
            #normal_y = (target_connection_point.y - position.y) / abs(target_connection_point.y - position.y)
            target_offset_x = target_connection_point.x - position.x
            target_offset_y = target_connection_point.y - position.y

            for connection_point in fluid_handler_source.connection_points:
                # Only select connection point pairs that are on the same axis
                # Continue
                source_offset_x = connection_point.x - position.x
                source_offset_y = connection_point.y - position.y


                if connection_point.x == target_connection_point.x and connection_point.y == target_connection_point.y:
                    return connection_point.x, connection_point.y
                distance = abs(connection_point.x - target_connection_point.x) + abs(connection_point.y - target_connection_point.y)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_connection_point = connection_point

        return nearest_connection_point.x, nearest_connection_point.y


    def _round_position(self, position: Position):
        return Position(x=math.floor(position.x), y=math.floor(position.y))
        #return Position(x=math.floor(position.x*2)/2, y=math.floor(position.y*2)/2)
        #return position

    def __call__(self,
                 source_entity: Entity,
                 target_entity: Entity,
                 connection_type: Prototype = Prototype.Pipe, relative=False) -> List[Entity]:
        connection_prototype, metaclass = connection_type

        x_sign = numpy.sign(source_entity.position.x - target_entity.position.x)
        y_sign = numpy.sign(source_entity.position.y - target_entity.position.y)

        if isinstance(source_entity, FluidHandler):
            if isinstance(source_entity, Boiler) and isinstance(target_entity, Generator):
                #source_position = self._round_position(source_entity.steam_output_point)
                x_diff_source_position_target_position = source_entity.position.x - source_entity.steam_output_point.x
                y_diff_source_position_target_position = source_entity.position.y - source_entity.steam_output_point.y
                top_source_position = Position(x=source_entity.position.x - source_entity.tile_dimensions.tile_width/2,
                                                  y=source_entity.position.y - source_entity.tile_dimensions.tile_height/2)
                bottom_source_position = Position(x=source_entity.position.x - source_entity.tile_dimensions.tile_width/2,
                                                    y=source_entity.position.y + source_entity.tile_dimensions.tile_height/2)
                left_source_position = Position(x=source_entity.position.x - source_entity.tile_dimensions.tile_width/2,
                                                    y=source_entity.position.y - source_entity.tile_dimensions.tile_height/2)
                right_source_position = Position(x=source_entity.position.x + source_entity.tile_dimensions.tile_width/2,
                                                        y=source_entity.position.y - source_entity.tile_dimensions.tile_height/2)
                # check if steam_output_point is on the top, bottom, left or right of the boiler, if so, add a 0.5 offset to the position in the direction of the generator
                if x_diff_source_position_target_position == 0:
                    if y_diff_source_position_target_position < 0:
                        source_position = Position(x=source_entity.position.x, y=source_entity.position.y + 1.5)
                    else:
                        source_position = Position(x=source_entity.position.x, y=source_entity.position.y - 1.5)
                elif y_diff_source_position_target_position == 0:
                    if x_diff_source_position_target_position < 0:
                        source_position = Position(x=source_entity.position.x + 1.5, y=source_entity.position.y)
                    else:
                        source_position = Position(x=source_entity.position.x - 1.5, y=source_entity.position.y)

                #source_position = source_entity.steam_output_point
            else:
                # self._round_position(
                source_position = self._get_nearest_connection_point(source_entity, target_entity.position, target_entity)
                #source_position = self._get_nearest_connection_point(source_entity, target_entity.position, target_entity)
            #if source_position.x < target_entity.position.x:
            #    source_position.x -= 1
        elif isinstance(source_entity, Inserter):
            source_position = self._round_position(source_entity.drop_position)
        elif isinstance(source_entity, MiningDrill):
            source_position = self._round_position(source_entity.drop_position)
        else:
            source_position = Position(x=source_entity.position.x-x_sign, y=source_entity.position.y-y_sign)

        if isinstance(target_entity, FluidHandler):
            if isinstance(target_entity, Boiler) and isinstance(source_entity, Generator):
                target_position = target_entity.steam_input_point#self._round_position(target_entity.steam_input_point)
            else:
                #target_position = self._round_position(self._get_nearest_connection_point(target_entity, source_position, source_entity))
                target_position = self._get_nearest_connection_point(target_entity, source_position, source_entity)
            #if source_position.x < target_position.x:
            #    target_position.x -= 1
        elif isinstance(target_entity, Inserter):
            target_position = target_entity.pickup_position#self._round_position(target_entity.pickup_position)
        elif isinstance(target_entity, MiningDrill):
            target_position = self._round_position(target_entity.drop_position)
        else:
            #target_position = target_entity.position
            target_position = Position(x=target_entity.position.x + x_sign, y=target_entity.position.y + y_sign)


        response, elapsed = self.execute(PLAYER,
                                         source_position.x,
                                         source_position.y,
                                         target_position.x,
                                         target_position.y,
                                         connection_prototype)
        if not isinstance(response, dict):
            message = response.split(":")[-1]
            raise Exception(f"Could not connect {connection_prototype} from {(source_position)} to {(target_position)}.", message.lstrip())

        path = []
        for key, value in response.items():
            if isinstance(value, dict):
                try:
                    path.append(metaclass(**value))
                except Exception as e:
                    raise Exception(f"Could not create {connection_prototype} object from response: {response}", e)

        return path
