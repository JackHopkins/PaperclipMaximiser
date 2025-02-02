import math
from typing import Optional

from controllers.__action import Action
from factorio_entities import Position, BuildingBox, BoundingBox
from factorio_instance import PLAYER
from factorio_types import Prototype


class NearestBuildable(Action):

    def __init__(self, lua_script_manager, game_state):
        super().__init__(lua_script_manager, game_state)
        #self.connection = connection
        self.game_state = game_state

    def __call__(self,
                 entity: Prototype,
                 building_box: BuildingBox,
                 center_position: Position,
                 **kwargs
                 ) -> BoundingBox:
        """
        Find the nearest buildable area for an entity.

        :param entity: Prototype of the entity to build.
        :param building_box: The building box denoting the area of location that must be placeable.
        :param center_position: The position to find the nearest area where building box fits
        :return: BoundingBox of the nearest buildable area or None if no such area exists.
        """
        if not isinstance(entity, Prototype):
            raise Exception("'nearest_buildable' requires the Prototype of the desired entity as the first argument")

        MARGIN = 0
        dx = building_box.width
        dy = building_box.height  
        dx = dx + MARGIN
        dy = dy + MARGIN
        bb_data = {
                "left_top": {"x": 0, "y": 0},
                "right_bottom": {"x": dx, "y": dy}
            }
        # make all the values integers
        center_position = {"x": math.ceil(center_position.x + 0.5), "y": math.ceil(center_position.y + 0.5)}


        response, time_elapsed = self.execute(PLAYER, entity.value[0], bb_data, center_position)

        if isinstance(response, str):
            raise Exception(f"No viable place to put {str(entity)} near the centre position {center_position} with this BuildingBox size found on the map. Either decrease the size of the BuildingBox or use multiple smaller BuildingBoxes")

        response_x = response['x']
        response_y = response['y']

        # return {"left_top": Position(x=response_x, y=response_y),
        #         "right_bottom": Position(x=response_x+dx-1,
        #                                   y=response_y+dy-1),
        #         "left_bottom": Position(x=response_x, y=response_y+dy-1),
        #         "right_top": Position(x=response_x + dx-1, y=response_y)}
        #
        return BoundingBox(
            left_top=Position(x=response_x, y=response_y),
            right_bottom=Position(x=response_x+dx-1, y=response_y+dy-1),
            left_bottom=Position(x=response_x, y=response_y+dy-1),
            right_top=Position(x=response_x + dx-1, y=response_y)
        )