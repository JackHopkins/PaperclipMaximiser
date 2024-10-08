import enum

from factorio_entities import *


class PrototypeName(enum.Enum):
    AssemblingMachine = "assembling-machine-1"
    BurnerInserter = "burner-inserter"
    BurnerMiningDrill = "burner-mining-drill"
    ElectricMiningDrill = "electric-mining-drill"
    StoneFurnace = "stone-furnace"
    TransportBelt = "transport-belt"
    OffshorePump = "offshore-pump"
    Boiler = "boiler"
    SteamEngine = "steam-engine"
    Pipe = "pipe"
    SmallElectricPole = "small-electric-pole"
    IronChest = "iron-chest"

class ResourceName(enum.Enum):
    Coal = "coal"
    IronOre = "iron-ore"
    CopperOre = "copper-ore"
    Stone = "stone"
    Water = "water"
    CrudeOil = "crude-oil"
    UraniumOre = "uranium-ore"

    @classmethod
    def get_list_of_names(cls):
        output_list = [x.value for x in cls]
        return output_list


class Prototype(enum.Enum):
    AssemblingMachine1 = "assembling-machine-1", AssemblingMachine1
    BurnerInserter = "burner-inserter", BurnerInserter
    BurnerMiningDrill = "burner-mining-drill", BurnerMiningDrill # Crafting requires 3 iron gear wheels, 3 iron plates, 1 stone furnace
    ElectricMiningDrill = "electric-mining-drill", MiningDrill
    StoneFurnace = "stone-furnace", Furnace # Crafting requires 5 stone
    TransportBelt = "transport-belt", TransportBelt
    OffshorePump = "offshore-pump", OffshorePump
    Boiler = "boiler", Boiler
    #Generator = "generator", Generator
    SteamEngine = "steam-engine", Generator
    Pipe = "pipe", Entity
    IronChest = "iron-chest", Entity
    WoodenChest = "wooden-chest", Entity
    IronGearWheel = "iron-gear-wheel", Entity # Crafting requires 2 iron plate
    Coal = "coal", None
    IronPlate = "iron-plate", None # Crafting requires smelting 1 iron ore using a stone furnace
    CopperPlate = "copper-plate", None # Crafting requires smelting 1 copper ore using a stone furnace
    SmallElectricPole = "small-electric-pole", Entity
    IronOre = "iron-ore", None
    CopperOre = "copper-ore", None
    Stone = "stone", None
    CopperCable = "copper-cable", None

    @classmethod
    def from_string(cls, value):
        for member in cls:
            if member.value[0] == value:
                return member
        raise ValueError(f"{value} is not a valid Prototype")
        


class Resource:
    Coal = "coal", ResourcePatch
    IronOre = "iron-ore", ResourcePatch
    CopperOre = "copper-ore", ResourcePatch
    Stone = "stone", ResourcePatch
    Water = "water", ResourcePatch
    CrudeOil = "crude-oil", ResourcePatch
    UraniumOre = "uranium-ore", ResourcePatch
    Wood = "tree-01", ResourcePatch
