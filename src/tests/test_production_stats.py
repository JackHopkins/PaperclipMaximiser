import unittest

from factorio_instance import FactorioInstance
from factorio_rcon_utils import _lua2python
from factorio_types import Resource

class TestProductionStats(unittest.TestCase):
    def test_production_stats(self):
        inventory = {
                'iron-plate': 50,
                'coal': 50,
                'copper-plate': 50,
                'iron-chest': 2,
                'burner-mining-drill': 3,
                'electric-mining-drill': 1,
                'assembling-machine-1': 1,
                'stone-furnace': 9,
                'transport-belt': 50,
                'boiler': 1,
                'burner-inserter': 32,
                'pipe': 15,
                'steam-engine': 1,
                'small-electric-pole': 10
            }
        instance = FactorioInstance(address='localhost',
                            bounding_box=200,
                            tcp_port=27000,
                            fast=True,
                            inventory=inventory)
        instance.move_to(instance.nearest(Resource.IronOre))
        instance.harvest_resource(instance.nearest(Resource.IronOre), quantity=10)

        result = instance._production_stats()

        assert result['input']['iron-ore'] == 10

        result = instance._production_stats()

        assert result['input']['iron-ore'] == 0

    def test_lua2python(self):
        result = _lua2python("pcall(global.actions.production_stats, 1)",  '{ ["a"] = true,["b"] = {\n ["iron-ore"] = 10\n},}')
        assert result

if __name__ == '__main__':
    unittest.main()
