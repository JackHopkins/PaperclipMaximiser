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
    ElectronicCircuit = "electronic-circuit"
    Lab = "lab"
    GunTurret = "gun-turret"

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
    AssemblingMachine1 = "assembling-machine-1", AssemblingMachine1 # Crafting requires 3 electronic circuits, 5 iron gear wheels, 9 iron plates
    BurnerInserter = "burner-inserter", BurnerInserter # Crafting requires 1 iron gear wheel, 1 iron plate,
    BurnerMiningDrill = "burner-mining-drill", BurnerMiningDrill # Crafting requires 3 iron gear wheels, 3 iron plates, 1 stone furnace
    ElectricMiningDrill = "electric-mining-drill", MiningDrill # Crafting requires 3 electronic circuits, 5 iron gear wheels, 10 iron plates
    StoneFurnace = "stone-furnace", Furnace # Crafting requires 5 stone
    TransportBelt = "transport-belt", TransportBelt # Crafting 2 transport belts requires 1 iron gear wheel, 1 iron plate
    OffshorePump = "offshore-pump", OffshorePump # Crafting requires 2 electronic circuits, 1 iron gear wheels, 1 pipe
    Boiler = "boiler", Boiler # Crafting requires 4 pipes, 1 stone furnace
    #Generator = "generator", Generator
    SteamEngine = "steam-engine", Generator # Crafting requires 8 iron gear wheels, 10 iron plates, 5 pipes
    Pipe = "pipe", Entity # Crafting requires 1 iron plate
    IronChest = "iron-chest", Entity # Crafting requires 8 iron plates
    WoodenChest = "wooden-chest", Entity # Crafting requires 2 wood
    IronGearWheel = "iron-gear-wheel", Entity # Crafting requires 2 iron plate
    Coal = "coal", None
    IronPlate = "iron-plate", None # Crafting requires smelting 1 iron ore, smelts for 0.5 seconds per ore
    SteelPlate = "steel-plate", None # Crafting requires smelting 5 iron plates, smelts for 4 seconds per ore
    CopperPlate = "copper-plate", None # Crafting requires smelting 1 copper ore, smelts for 0.5 seconds per ore
    SmallElectricPole = "small-electric-pole", Entity
    IronOre = "iron-ore", None
    CopperOre = "copper-ore", None
    Stone = "stone", None
    CopperCable = "copper-cable", None # Crafting 2 copper cables requires 1 copper plate
    ElectronicCircuit = "electronic-circuit", None # Crafting requires 3 copper cables, 1 iron plate
    Lab = "lab", Entity # Crafting requires 10 electronic circuits, 10 iron gear wheels, 4 transport belts
    AutomationSciencePack = "automation-science-pack", None
    Accumulator = "accumulator", Accumulator
    GunTurret = "gun-turret", GunTurret
    FirearmMagazine = "firearm-magazine", Ammo
    StoneBrick = "stone-brick", None
    Radar = "radar", Entity

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
    Wood = "wood", ResourcePatch
