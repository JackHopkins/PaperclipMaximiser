import pytest

from factorio_types import Prototype

@pytest.fixture()
def game(instance):
    instance.reset()
    yield instance

def test_set_entity_recipe(game):
    # Place an assembling machine
    assembling_machine = game.place_entity(Prototype.AssemblingMachine, position=(0, 0))

    # Set a recipe for the assembling machine
    assembling_machine = game.set_entity_recipe(assembling_machine, Prototype.IronGearWheel)

    # Assert that the recipe of the assembling machine has been updated
    prototype_name, _ = Prototype.IronGearWheel

    assert assembling_machine.recipe == prototype_name

    game.reset()