import pytest

from factorio_entities import Position
from factorio_types import Resource

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

def test_nearest_resource(game):
    """
    Test distance to the nearest coal resource.
    :param game:
    :return:
    """
    coal: Position = game.nearest(Resource.Coal)
    assert coal.y == -4.5
    assert coal.x == -7.5