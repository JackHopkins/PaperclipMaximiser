import math
from typing import Optional

from controllers.__action import Action
from factorio_entities import Position, BuildingBox
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
                 ) -> dict:
        """
        Find the nearest buildable area for an entity.
        Inputs
        :param entity: Prototype of the entity to build.
        :param building_box: The bounding box of the entity to build.
        :param center_position: The position to find the nearest area where building box fits
        
        Outputs
        :return: A dictionary containing the center position of the buildable area, width and height margins
            centre - Position of the center of the buildable area
            width_margin - Distance from centre to the right and left edges of the buildable area
            height_margin - Distance from centre to the top and bottom edges of the buildable area
        """
        if not isinstance(entity, Prototype):
            raise Exception("'nearest_buildable' requires the Prototype of the desired entity as the first argument")

        # Convert bounding box to relative coordinates if provided
        #bb_data = None
        #dx, dy = 0, 0
        #if bounding_box:
        #    dx = bounding_box.left_top.x# if bounding_box.left_top.x < 0 else 0
        #    dy = bounding_box.left_top.y# if bounding_box.left_top.y < 0 else 0
        #    MARGIN = 1
#
        #    bb_data = {
        #        "left_top": {"x": bounding_box.left_top.x-dx, "y": bounding_box.left_top.y-dy},
        #        "right_bottom": {"x": bounding_box.right_bottom.x-dx+MARGIN*2, "y": bounding_box.right_bottom.y-dy+MARGIN*2},
        #        "center": {"x": bounding_box.center.x-dx, "y": bounding_box.center.y-dy}
        #    }


        MARGIN = 1
        dx = building_box.width if building_box.width % 2 == 1 else building_box.width +1
        dy = building_box.height if building_box.height % 2 == 1 else building_box.height +1
        dx = dx + MARGIN
        dy = dy + MARGIN
        dx_offset = dx//2
        dy_offset = dy//2
        bb_data = {
                "left_top": {"x": 0, "y": 0},
                "right_bottom": {"x": dx, "y": dy},
                "center": {"x": dx_offset, "y": dy_offset}
            }
        center_position = {"x": center_position.x, "y": center_position.y}


        response, time_elapsed = self.execute(PLAYER, entity.value[0], bb_data, center_position)

        if isinstance(response, str):
            raise Exception(f"No viable place to put {str(entity)} near the centre position {center_position} with this BuildingBox size found on the map. Either decrease the size of the BuildingBox or use multiple smaller BuildingBoxes")

        # if not self.game_state.last_observed_player_location:
        #     self.game_state.last_observed_player_location = self.game_state.player_location
        #
        # else:
        # return (math.floor(response['x']), math.floor(response['y']))
        #if not bounding_box:
        #    return Position(x=response['x'], y=response['y'])
        #else:
        #    return Position(x=response['x']-dx, y=response['y']-dy)
        return {"centre": Position(x=response['x']+dx_offset, y=response['y']+dx_offset),
                "width_margin": dx_offset,
                "height_margin": dy_offset}