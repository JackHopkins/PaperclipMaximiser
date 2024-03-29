
from controllers._action import Action
from factorio_entities import Position
from factorio_instance import PLAYER
from models.zero_dict import ZeroDict


class InspectEntities(Action):

    def __init__(self, connection, game_state):
        super().__init__(connection, game_state)
        self.connection = connection
        self.game_state = game_state

    def __call__(self,
                 radius=10,
                 position: Position = None,
                 relative: bool = False):
        response, time_elapsed = self.execute(PLAYER, radius)
        entities = []
        try:
            if isinstance(response, dict):
                entity_list = list(response.values())
                for entity in entity_list:
                    position = tuple(entity["position"].values())

                    if relative:
                        position = (position[0] - self.game_state.last_observed_player_location[0],
                                    position[1] - self.game_state.last_observed_player_location[1])

                    entity_dict = {
                        "name": entity["name"],
                        #"direction": entity["direction"],
                        "position": position
                    }

                    if "path_ends" in entity:
                        if len(entity["path_ends"]) > 1:
                            start = position
                            end = None
                            for _, path_end in entity["path_ends"].items():
                                if path_end["unit_number"] == min(
                                        [e["unit_number"] for e in entity["path_ends"].values()]):
                                    end = tuple(path_end["position"].values())
                                    break

                            entity_dict["start_position"] = start
                            entity_dict["end_position"] = end
                            entity_dict["quantity"] = len(entity["path_ends"])

                    if "warnings" in entity and entity['warnings']:
                        entity_dict["warning"] = ". ".join(entity['warnings'].values()).replace("_", " ")

                    if "contents" in entity and entity['contents']:
                        entity_dict["contents"] = {k: v for k, v in entity['contents'].items()}

                    elif "crafted_items" in entity:
                        contains = {}
                        if entity['crafted_items']:
                            contains.update({k: v for k, v in entity['crafted_items'].items()})
                        if entity['ingredients']:
                            contains.update({k: v for k, v in entity['ingredients'].items()})
                        if contains:
                            entity_dict["contents"] = contains

                    if "status" not in entity_dict:
                        entity_dict["status"] = "empty" if "contents" not in entity_dict else "not empty"

                    entities.append(entity_dict)

            self.last_observed_player_location = (0, 0)
            return entities
        except Exception as e:
            print(e)
            return {}
