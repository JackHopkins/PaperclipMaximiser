import math

from controllers._action import Action
from typing import Tuple, List

from factorio_entities import Entity, Boiler, FluidHandler, Position, Generator
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

            distance = abs(connection_point.x - existing_connection_position.x) + abs(
                connection_point.y - existing_connection_position.y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_connection_point = connection_point

        return nearest_connection_point.x, nearest_connection_point.y

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



    def __call__(self,
                 source_entity: Entity,
                 target_entity: Entity,
                 connection_type: Prototype = Prototype.Pipe, relative=False) -> List[Entity]:
        connection_prototype, metaclass = connection_type

        if isinstance(source_entity, FluidHandler):
            if isinstance(source_entity, Boiler) and isinstance(target_entity, Generator):
                source_x, source_y = source_entity.steam_output_point.x, source_entity.steam_output_point.y
            else:
                source_x, source_y = self._get_nearest_connection_point(source_entity, target_entity.position, target_entity)
        else:
            source_x, source_y = source_entity.position.x, source_entity.position.y

        if isinstance(target_entity, FluidHandler):
            if isinstance(target_entity, Boiler) and isinstance(source_entity, Generator):
                target_x, target_y = target_entity.steam_input_point.x, target_entity.steam_input_point.y
            else:
                target_x, target_y = self._get_nearest_connection_point(target_entity, Position(x=source_x, y=source_y), source_entity)
        else:
            target_x, target_y = target_entity.position.x, target_entity.position.y

        if relative:
            source_x -= self.game_state.last_observed_player_location[0]
            target_x -= self.game_state.last_observed_player_location[0]
            source_y -= self.game_state.last_observed_player_location[1]
            target_y -= self.game_state.last_observed_player_location[1]

        response, elapsed = self.execute(PLAYER,
                                         source_x - 0.5,
                                         source_y - 0.5,
                                         target_x - 0.5,
                                         target_y - 0.5,
                                         connection_prototype)
        if not isinstance(response, dict):
            message = response.split(":")[-1]
            raise Exception(f"Could not connect {connection_prototype} from {(source_x, source_y)} to {(target_x, target_y)}.", message.lstrip())

        path = []
        for key, value in response.items():
            if isinstance(value, dict):
                try:
                    path.append(metaclass(**value))
                except Exception as e:
                    raise Exception(f"Could not create {connection_prototype} object from response: {response}", e)

        return path
