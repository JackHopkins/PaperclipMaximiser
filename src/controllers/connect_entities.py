import math

import numpy
import numpy as np

from controllers.__action import Action
from typing import Tuple, List, Union

from controllers.get_path import GetPath
from controllers.pickup_entity import PickupEntity
from controllers.request_path import RequestPath
from controllers.rotate_entity import RotateEntity
from controllers.inspect_inventory import InspectInventory
from factorio_entities import Entity, Boiler, FluidHandler, Position, Generator, Inserter, MiningDrill, TransportBelt, \
    OffshorePump, PumpJack, BeltGroup, EntityGroup, PipeGroup
from factorio_instance import PLAYER, Direction
from factorio_types import Prototype
from utilities.merge_transport_belts import agglomerate_groupable_entities


class ConnectEntities(Action):

    def __init__(self, connection, game_state):
        self.game_state = game_state
        super().__init__(connection, game_state)
        self.request_path = RequestPath(connection, game_state)
        self.get_path = GetPath(connection, game_state)
        self.rotate_entity = RotateEntity(connection, game_state)
        self.pickup_entity = PickupEntity(connection, game_state)
        self.inspect_inventory = InspectInventory(connection, game_state)


    def _get_nearest_connection_point(self,
                                      fluid_handler_source: FluidHandler,
                                      existing_connection_position: Position,
                                      existing_connection_entity: Entity = None):

        if existing_connection_entity is not None:
            existing_offset_x = existing_connection_position.x - existing_connection_entity.position.x
            existing_offset_y = existing_connection_position.y - existing_connection_entity.position.y
        else:
            existing_offset_x = 0
            existing_offset_y = 0

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
            # if dir_x == 0 and dir_y == 0:  # They are on top of each other, so just return this point
            #     return connection_point
            # elif dir_x == 0 and possible_offset_y * dir_y < 0:  # They are vertically aligned and facing each other
            #     continue
            # elif dir_y == 0 and possible_offset_x * dir_x < 0:  # They are horizontally aligned and facing each other
            #     continue
            # elif possible_offset_x * dir_x < 0 and possible_offset_y * dir_y < 0:  # They are diagonally aligned and facing each other
            #     continue

            # Calculate distance
            distance = abs(connection_point.x - existing_connection_position.x) + abs(
                connection_point.y - existing_connection_position.y)

            # Update if this distance is smaller
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_connection_point = connection_point

        # The connection points need to be at the center of a tile. If either coordinate is an integer, it needs
        # to be rounded to the half-tile furthest away from the source position.
        # If the connection point is to the left of the source position, and a 0.5 x offset
        nearest_connection_point_x = nearest_connection_point.x
        nearest_connection_point_y = nearest_connection_point.y

        # This ensures that the connection point is always outside of the entity (no longer just bordering it)
        if nearest_connection_point_x % 1 == 0:
            if nearest_connection_point_x < fluid_handler_source.position.x:
                nearest_connection_point_x = nearest_connection_point_x - 0.5
            elif nearest_connection_point_x > fluid_handler_source.position.x:
                nearest_connection_point_x = nearest_connection_point_x + 0.5
        if nearest_connection_point_y % 1 == 0:
            if nearest_connection_point_y < fluid_handler_source.position.y:
                nearest_connection_point_y = nearest_connection_point_y - 0.5
            elif nearest_connection_point_y > fluid_handler_source.position.y:
                nearest_connection_point_y = nearest_connection_point_y + 0.5

        nearest_connection_point = Position(x=nearest_connection_point_x, y=nearest_connection_point_y)


        # # If the connection point is to the left of the source position, and a 0.5 x offset
        # if nearest_connection_point.x < fluid_handler_source.position.x:
        #     nearest_connection_point = Position(x=nearest_connection_point.x + 0.5, y=nearest_connection_point.y)
        # # If the connection point is to the right of the source position, and a -0.5 x offset
        # elif nearest_connection_point.x > fluid_handler_source.position.x:
        #     nearest_connection_point = Position(x=nearest_connection_point.x - 0.5, y=nearest_connection_point.y)
        #
        # # If the connection point is above the source position, and a 0.5 y offset
        # if nearest_connection_point.y < fluid_handler_source.position.y:
        #     nearest_connection_point = Position(x=nearest_connection_point.x, y=nearest_connection_point.y - 0.5)
        # # If the connection point is below the source position, and a -0.5 y offset
        # elif nearest_connection_point.y > fluid_handler_source.position.y:
        #     nearest_connection_point = Position(x=nearest_connection_point.x, y=nearest_connection_point.y + 0.5)

        return nearest_connection_point

    def _round_position(self, position: Position):
        return Position(x=math.floor(position.x), y=math.floor(position.y))

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Remove duplicate entities while maintaining the original order.
        Later entities with the same position override earlier ones.
        """
        unique_entities = []
        seen = set()
        for entity in reversed(entities):
            position = (entity.position.x, entity.position.y)
            if position not in seen:
                unique_entities.append(entity)
                seen.add(position)
        return list(reversed(unique_entities))

    def __call__(self,
                 source: Union[Position, Entity, EntityGroup],
                 target: Union[Position, Entity, EntityGroup],
                 connection_type: Prototype = Prototype.Pipe,
                 dry_run: bool = False
                 ) -> List[Union[Entity, EntityGroup]]:
        """
        Connect two entities or positions.
        :param source: First entity or position
        :param target: Second entity or position
        :param connection_type: a Pipe, TransportBelt or ElectricPole
        :example connect_entities(source=boiler, target=generator, connection_type=Prototype.Pipe)
        :example connect_entities(source=miner, target=stone_furnace, connection_type=Prototype.TransportBelt)
        :return: List of entities that were created
        """
        try:
            connection_prototype, metaclass = connection_type.value
            source_entity = None
            target_entity = None

            # get the inventory
            inventory = self.inspect_inventory()
            # get the number of the connection_prototype in the inventory
            number_of_connection_prototype = inventory.get(connection_prototype, 0)

            if isinstance(source, Entity) or isinstance(source, EntityGroup):
                source_entity = source
                source_position = Position(x=source_entity.position.x, y=source_entity.position.y)
            elif isinstance(source, Position):
                source_position = source
            else:
                raise TypeError("Source must be either an Entity, Position or EntityGroup")

            if isinstance(target, Entity) or isinstance(target, EntityGroup):
                target_entity = target
                target_position = Position(x=target_entity.position.x, y=target_entity.position.y)
            elif isinstance(target, Position):
                target_position = target
            else:
                raise TypeError("Target must be either an Entity or Position.")

            if source_entity:
                x_sign = numpy.sign(source_entity.position.x - target_position.x)
                y_sign = numpy.sign(source_entity.position.y - target_position.y)
            else:
                x_sign = numpy.sign(source_position.x - target_position.x)
                y_sign = numpy.sign(source_position.y - target_position.y)

            if isinstance(source_entity, BeltGroup):
                source_position = source_entity.output_positions[0]
            elif source_entity and isinstance(source, Entity) and (connection_type.name == Prototype.Pipe.name or connection_type.name == Prototype.TransportBelt.name):
                if isinstance(source_entity, PumpJack) and connection_type.name == Prototype.Pipe.name:
                    source_position = source_entity.connection_points[0]
                    pass
                elif isinstance(source_entity, FluidHandler) and connection_type.name == Prototype.Pipe.name:
                    if isinstance(source_entity, OffshorePump):
                        source_position = Position(x=source_entity.connection_points[0].x,
                                                   y=source_entity.connection_points[0].y)
                    elif isinstance(source_entity, Boiler):
                        if target_entity and isinstance(target_entity, Generator):
                            #source_position = self._round_position(source_entity.steam_output_point)
                            x_diff_source_position_target_position = source_entity.position.x - source_entity.steam_output_point.x
                            y_diff_source_position_target_position = source_entity.position.y - source_entity.steam_output_point.y
                            BOILER_WIDTH = 3
                            OFFSET = 0
                            # check if steam_output_point is on the top, bottom, left or right of the boiler, if so, add a 0.5 offset to the position in the direction of the generator
                            if x_diff_source_position_target_position == 0:
                                if y_diff_source_position_target_position < 0:
                                    source_position = Position(x=source_entity.position.x, y=source_entity.position.y + BOILER_WIDTH/2 + OFFSET)
                                else:
                                    source_position = Position(x=source_entity.position.x, y=source_entity.position.y - BOILER_WIDTH/2 - OFFSET)
                            elif y_diff_source_position_target_position == 0:
                                if x_diff_source_position_target_position < 0:
                                    source_position = Position(x=source_entity.position.x + BOILER_WIDTH/2 + OFFSET, y=source_entity.position.y)
                                else:
                                    source_position = Position(x=source_entity.position.x - BOILER_WIDTH/2 - OFFSET, y=source_entity.position.y)

                        elif target_entity and isinstance(target_entity, OffshorePump):
                            source_position = self._get_nearest_connection_point(source_entity,
                                                                                 source_position,
                                                                                 existing_connection_entity=target_entity)

                    else:
                        source_position = self._get_nearest_connection_point(source_entity,
                                                                             target_position,
                                                                             existing_connection_entity=target_entity)

                elif isinstance(source_entity, Inserter):
                    source_position = source_entity.drop_position
                elif isinstance(source_entity, MiningDrill):
                    source_position = source_entity.drop_position
                elif isinstance(source_entity, TransportBelt):
                    source_position = source_entity.position
                else:
                    source_position = Position(x=source_entity.position.x-x_sign*source_entity.tile_dimensions.tile_width/2,
                                               y=source_entity.position.y-y_sign*source_entity.tile_dimensions.tile_height/2)
            elif connection_type.name == Prototype.TransportBelt.name:
                # If we are connecting a position with a transport belt, we need to add 0.5 to the position to prevent
                # Weird behaviour from the pathfinding
                source_position = Position(x=math.floor(source_position.x)+0.5, y=math.floor(source_position.y)+0.5)
                pass

            if isinstance(target_entity, BeltGroup):
                target_position = target_entity.input_positions[0]
            elif isinstance(target, Entity) and (connection_type.name == Prototype.Pipe.name or connection_type.name == Prototype.TransportBelt.name):
                if isinstance(target_entity, FluidHandler) and connection_type.name == Prototype.Pipe.name:
                    if isinstance(target_entity, Boiler):
                        if isinstance(source_entity, OffshorePump):
                            target_position = self._get_nearest_connection_point(target_entity,
                                                                                 source_position,
                                                                                 existing_connection_entity=source_entity)
                        else:
                            target_position = target_entity.steam_input_point
                    elif isinstance(target_entity, Boiler) and isinstance(source_entity, Generator):
                        target_position = target_entity.steam_input_point
                        pass
                    else:
                        target_position = self._get_nearest_connection_point(target_entity,
                                                                             source_position,
                                                                             existing_connection_entity=source_entity)
                        #target_position = Position(x=target_position.x+0.5, y=target_position.y+0.5)
                        target_position = Position(x=target_position.x, y=target_position.y)

                elif isinstance(target_entity, Inserter):
                    target_position = target_entity.pickup_position
                elif isinstance(target_entity, MiningDrill):
                    target_position = target_entity.drop_position
                elif isinstance(target_entity, TransportBelt):
                    target_position = target_entity.position
                else:
                    target_position = Position(x=target_entity.position.x + x_sign*source_entity.tile_dimensions.tile_width/2,
                                               y=target_entity.position.y + y_sign*source_entity.tile_dimensions.tile_height/2)
            elif connection_type.name == Prototype.TransportBelt.name:# or connection_type.name == Prototype.Pipe.name:
                # If we are connecting a position with a transport belt / pipe, we need to add 0.5 to the position to prevent
                # Weird behaviour from the pathfinding
                target_position = Position(x=math.floor(target_position.x) + 0.5, y=math.floor(target_position.y) + 0.5)
                pass

            if isinstance(source_entity, PipeGroup) and isinstance(target_entity, PipeGroup):
                # If the source_entity and the target_entity is the same object, ensure there are only 2 input_positions
                # And set them.
                if source_entity.pipes[0].position == target_entity.pipes[0].position:
                    if len(source_entity.input_positions) == 2:
                        source_position = source_entity.input_positions[0]
                        target_position = target_entity.input_positions[1]
                    else:
                        raise Exception("PipeGroup must have only 2 input_position if connecting to itself.")
                else:
                    # check each input_position from the source_entity, and each output_position from the target_entity
                    # determine which pair is the closest, and connect them
                    shortest_distance = 1000000
                    for source_input_position in source_entity.input_positions:
                        for target_output_position in target_entity.input_positions:
                            distance = abs(source_input_position.x - target_output_position.x) + abs(source_input_position.y - target_output_position.y)
                            if distance < shortest_distance:
                                shortest_distance = distance
                                source_position = source_input_position
                                target_position = target_output_position


            # Move the source and target positions to the center of the tile
            target_position = Position(x=round(target_position.x*2)/2, y=round(target_position.y*2)/2)
            source_position = Position(x=round(source_position.x*2)/2, y=round(source_position.y*2)/2)
            if connection_type == Prototype.Pipe or connection_type == Prototype.TransportBelt:
                try:
                    # Attempt to avoid entities
                    path_handle = self.request_path(finish=Position(x=target_position.x, y=target_position.y),
                                                    start=source_position, allow_paths_through_own_entities=False)
                    response, elapsed = self.execute(PLAYER,
                                                     source_position.x,
                                                     source_position.y,
                                                     target_position.x,
                                                     target_position.y,
                                                     path_handle,
                                                     connection_prototype,
                                                     dry_run,
                                                     number_of_connection_prototype)
                    if not isinstance(response, dict) and response != "Passed":
                        raise Exception(
                            f"Could not connect {connection_prototype} from {(source_position)} to {(target_position)}.",
                            response.lstrip())

                except Exception as e:
                    # But accept allowing paths through own entities if it fails
                    path_handle = self.request_path(finish=Position(x=target_position.x, y=target_position.y),
                                                    start=source_position, allow_paths_through_own_entities=True)
                    response, elapsed = self.execute(PLAYER,
                                                     source_position.x,
                                                     source_position.y,
                                                     target_position.x,
                                                     target_position.y,
                                                     path_handle,
                                                     connection_prototype,
                                                     dry_run,
                                                     number_of_connection_prototype)
            else:
                path_handle = self.request_path(finish=target_position, start=source_position, allow_paths_through_own_entities=True)

                response, elapsed = self.execute(PLAYER,
                                                 source_position.x,
                                                 source_position.y,
                                                 target_position.x,
                                                 target_position.y,
                                                 path_handle,
                                                 connection_prototype,
                                                 dry_run,
                                                 number_of_connection_prototype)
            if not isinstance(response, dict) and response != "Passed":
                raise Exception(f"Could not connect {connection_prototype} from {(source_position)} to {(target_position)}.", response.lstrip())

            if dry_run:
                return {"number_of_entities_required": response["number_of_entities"],
                        "number_of_entities_available": number_of_connection_prototype}

            success = response.get('connected', False)
            entities_list = response.get('entities', {}).values()
            path = []
            groupable_entities = []
            for value in entities_list:
                if isinstance(value, dict):
                    try:
                        if not value['warnings']:
                            del value['warnings']
                            value['warnings'] = []
                        entity = metaclass(prototype=connection_type, **value)

                        if entity.prototype == Prototype.TransportBelt or entity.prototype == Prototype.Pipe:
                            groupable_entities.append(entity)
                        else:
                            path.append(entity)
                    except Exception as e:
                        if not value:
                            continue
                        raise Exception(f"Could not create {connection_prototype} object from response: {response}", e)

            # If the source and target entities are both BeltGroups, we need to make sure that the final belt is rotated
            # to face the first belt of the source entity group.
            if isinstance(source_entity, BeltGroup) and isinstance(target_entity, BeltGroup):
                self.rotate_final_belt_when_connecting_groups(groupable_entities, source_entity)

            deduplicated_path = self._deduplicate_entities(path)

            entity_groups = []
            # If we are connecting to an existing belt group, we need to agglomerate them all together
            if connection_type == Prototype.TransportBelt:
                if isinstance(source_entity, BeltGroup):
                    entity_groups = agglomerate_groupable_entities(source_entity.belts + groupable_entities)
                    entity_groups[0].input_positions = source_entity.input_positions
                elif isinstance(target_entity, BeltGroup):
                    entity_groups = agglomerate_groupable_entities(groupable_entities + target_entity.belts)
                    entity_groups[0].output_positions = target_entity.output_positions
                else:
                    entity_groups = agglomerate_groupable_entities(groupable_entities)

                for entity_group in entity_groups:
                    entity_group.belts = self._deduplicate_entities(entity_group.belts)
            elif connection_type == Prototype.Pipe:
                if isinstance(source_entity, PipeGroup):
                    entity_groups = agglomerate_groupable_entities(source_entity.pipes + groupable_entities)
                    #entity_groups[0].input_positions = source_entity.input_positions
                elif isinstance(target_entity, PipeGroup):
                    entity_groups = agglomerate_groupable_entities(groupable_entities + target_entity.pipes)
                    #entity_groups[0].output_positions = target_entity.output_positions
                else:
                    entity_groups = agglomerate_groupable_entities(groupable_entities)

                for entity_group in entity_groups:
                    entity_group.pipes = self._deduplicate_entities(entity_group.pipes)

            # if we have more than one entity group - but one of them only has one entity (i.e it is dangling) we
            # should pick it up back into the inventory, as the connect entities routine should not have created it
            if len(entity_groups) > 1:
                for entity_group in entity_groups:
                    if connection_type == Prototype.TransportBelt:
                        if len(entity_group.belts) == 1:
                            #self.pickup_entity(connection_type, entity_group.belts[0].position)
                            entity_groups.remove(entity_group)
                    elif connection_type == Prototype.Pipe:
                        if len(entity_group.pipes) == 1:
                            self.pickup_entity(connection_type, entity_group.pipes[0].position)
                            entity_groups.remove(entity_group)

            # Use the new deduplication function
            return deduplicated_path + entity_groups
        except Exception as e:
            raise e

    def rotate_final_belt_when_connecting_groups(self, new_belt: BeltGroup, target: BeltGroup) -> BeltGroup:
        source_belt = new_belt[-1]
        target_belt = target.belts[0]
        if source_belt.position.x < target_belt.position.x:
            # It is necessary to use the direction enums from the game state
            source_belt = self.rotate_entity(source_belt, Direction.RIGHT)
        elif source_belt.position.x > target_belt.position.x:
            source_belt = self.rotate_entity(source_belt, Direction.LEFT)
        elif source_belt.position.y < target_belt.position.y:
            source_belt = self.rotate_entity(source_belt, Direction.DOWN)
        elif source_belt.position.y > target_belt.position.y:
            source_belt = self.rotate_entity(source_belt, Direction.UP)

        new_belt[-1] = source_belt
        return new_belt