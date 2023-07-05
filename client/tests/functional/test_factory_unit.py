import time

import pytest

from factorio_instance import FactorioInstance
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance


def test_iron_smelting(game: FactorioInstance):
    """
    Create an auto driller for coal.
    Create a miner for iron ore and a nearby furnace. Connect the miner to the furnace.

    :return:
    """

    burner_mining_drill = game.place_entity(Prototype.BurnerMiningDrill, position=game.nearest(Resource.Coal))
    burner_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                reference_position=burner_mining_drill.position,
                                                direction_from=game.DOWN,
                                                spacing=1)
    assert burner_inserter

    belts = game.connect_entities(burner_mining_drill, burner_inserter, connection_type=Prototype.TransportBelt)

    assert belts

    game.insert_item(Prototype.Coal, burner_mining_drill, 5)
    nearest_iron_ore = game.nearest(Resource.IronOre)

    game.move_to(nearest_iron_ore)
    try:
        iron_mining_drill = game.place_entity(Prototype.BurnerMiningDrill, position=nearest_iron_ore)

        stone_furnace = game.place_entity(Prototype.StoneFurnace, position=iron_mining_drill.drop_position)

        coal_to_iron_drill_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                    reference_position=iron_mining_drill.position,
                                                    direction_from=game.DOWN,
                                                    spacing=1)
        coal_to_iron_drill_inserter
        burner_inserter
        game.connect_entities(coal_to_iron_drill_inserter, burner_inserter, connection_type=Prototype.TransportBelt)
    except Exception as e:
        print(e)
        assert False
    assert burner_inserter

def test_auto_driller(game: FactorioInstance):
    burner_mining_drill = game.place_entity(Prototype.BurnerMiningDrill, position=game.nearest(Resource.Coal))
    burner_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                reference_position=burner_mining_drill.position,
                                                direction_from=game.DOWN,
                                                spacing=1)
    assert burner_inserter

    belts = game.connect_entities(burner_mining_drill, burner_inserter, connection_type=Prototype.TransportBelt)

    assert belts

    game.insert_item(Prototype.Coal, burner_mining_drill, 5)

    start_score = game.score()
    time.sleep(5)
    end_score = game.score()

    assert end_score > start_score
