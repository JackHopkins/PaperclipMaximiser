import pytest

from factorio_entities import Position
from factorio_instance import Direction
from factorio_types import Prototype, Resource


@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance.namespace
    instance.reset()

def test_print_tuple(game):
    """
    Print a tuple
    """
    r = game.print("Hello", "World", (1, 2, 3))

    assert r == "Hello\tWorld\t(1, 2, 3)"