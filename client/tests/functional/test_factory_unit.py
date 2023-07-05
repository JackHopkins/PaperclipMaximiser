import pytest

from factorio_instance import FactorioInstance
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

def test_smelt(game: FactorioInstance):
    burner_mining_drill = game.place_entity(Prototype.BurnerMiningDrill, position=game.nearest(Resource.Coal))
    burner_inserter = game.place_entity_next_to(Prototype.BurnerInserter,
                                                reference_position=burner_mining_drill.position,
                                                direction_from=game.DOWN,
                                                spacing=1)
    assert burner_inserter

    game.connect_entities(burner_mining_drill, burner_inserter, connection_type=Prototype.TransportBelt)
