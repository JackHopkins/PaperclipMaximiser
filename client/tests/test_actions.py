import pytest

from client.factorio_instance import FactorioInstance
from client.factorio_types import Prototype


@pytest.fixture
def game():
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27016,
                                inventory={
                                    'coal': 50,
                                    'copper-plate': 50,
                                    'iron-plate': 50,
                                    'iron-chest': 1,
                                    'burner-mining-drill': 1,
                                    'electric-mining-drill': 1,
                                    'assembling-machine-1': 1,
                                    'stone-furnace': 1,
                                    'transport-belt': 50,
                                    'boiler': 1,
                                    'burner-inserter': 1,
                                    'pipe': 1,
                                    'steam-engine': 1,
                                })
    instance.reset()
    yield instance

def test_place(game):
    boilers_in_inventory = game.inspect_inventory()[Prototype.Boiler]
    game.place_entity(Prototype.Boiler, position=(0,0))
    assert boilers_in_inventory - 1 == game.inspect_inventory()[Prototype.Boiler]

