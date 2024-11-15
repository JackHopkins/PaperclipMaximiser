import math

import numpy
import numpy as np

from controllers._action import Action
from typing import Tuple, List, Union

from controllers.get_path import GetPath
from controllers.pickup_entity import PickupEntity
from controllers.connect_entities import ConnectEntities
from controllers.inspect_inventory import InspectInventory
from factorio_entities import Entity, Boiler, FluidHandler, Position, Generator, Inserter, MiningDrill, TransportBelt, \
    OffshorePump, PumpJack, BeltGroup, EntityGroup, PipeGroup
from factorio_instance import PLAYER, Direction
from factorio_types import Prototype
from utilities.merge_transport_belts import agglomerate_groupable_entities


class CheckConnection(Action):

    def __init__(self, connection, game_state):
        self.game_state = game_state
        super().__init__(connection, game_state)
        self.connect_entities = ConnectEntities(connection, game_state)
        self.inspect_inventory = InspectInventory(connection, game_state)


    def __call__(self,
                 source: Union[Position, Entity, EntityGroup],
                 target: Union[Position, Entity, EntityGroup],
                 connection_type: Prototype = Prototype.Pipe,
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
        current_inventory = self.inspect_inventory()
        path_output = self.connect_entities(source, target, connection_type, dry_run = True)
        required_entities = path_output['required_entities']
        existing_entities = current_inventory.get(connection_type, 0)
        if existing_entities < required_entities:
            return f"Insufficient {connection_type} entities to connect {source} with {target}. Required: {required_entities}, Existing: {existing_entities}"
        else:
            return f"There are sufficient {connection_type} entities to connect {source} with {target}. Required: {required_entities}, Existing: {existing_entities}"
        