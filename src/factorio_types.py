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


class Prototype(enum.Enum):
    AssemblingMachine1 = "assembling-machine-1", AssemblingMachine
    AssemblingMachine2 = "assembling-machine-2", AssemblingMachine
    AssemblingMachine3 = "assembling-machine-3", AssemblingMachine
    BurnerInserter = "burner-inserter", BurnerInserter
    FastInserter = "fast-inserter", Inserter
    ExpressInserter = "express-inserter", Inserter
    Inserter = "inserter", Inserter
    BurnerMiningDrill = "burner-mining-drill", BurnerMiningDrill
    ElectricMiningDrill = "electric-mining-drill", MiningDrill
    StoneFurnace = "stone-furnace", Furnace
    FastTransportBelt = "fast-transport-belt", TransportBelt
    ExpressTransportBelt = "express-transport-belt", TransportBelt
    Splitter = "splitter", Splitter
    FastSplitter = "fast-splitter", Splitter
    ExpressSplitter = "express-splitter", Splitter
    TransportBelt = "transport-belt", TransportBelt
    ExpressUndergroundBelt = "express-underground-belt", UndergroundBelt
    FastUndergroundBelt = "fast-underground-belt", UndergroundBelt
    UndergroundBelt = "underground-belt", UndergroundBelt

    OffshorePump = "offshore-pump", OffshorePump
    PumpJack = "pumpjack", PumpJack
    Boiler = "boiler", Boiler
    SteamEngine = "steam-engine", Generator
    Pipe = "pipe", Pipe
    IronChest = "iron-chest", Chest
    WoodenChest = "wooden-chest", Chest
    IronGearWheel = "iron-gear-wheel", Entity
    Coal = "coal", None
    Wood = "wood", None
    IronPlate = "iron-plate", None
    SteelPlate = "steel-plate", None
    CopperPlate = "copper-plate", None
    SmallElectricPole = "small-electric-pole", Entity
    MediumElectricPole = "medium-electric-pole", Entity
    BigElectricPole = "big-electric-pole", Entity
    IronOre = "iron-ore", None
    CopperOre = "copper-ore", None
    Stone = "stone", None
    CopperCable = "copper-cable", None
    ElectronicCircuit = "electronic-circuit", None
    AdvancedCircuit = "advanced-circuit", None
    Lab = "lab", Lab
    AutomationSciencePack = "automation-science-pack", None
    Accumulator = "accumulator", Accumulator
    GunTurret = "gun-turret", GunTurret
    FirearmMagazine = "firearm-magazine", Ammo
    StoneBrick = "stone-brick", None 
    Radar = "radar", Entity 
    StoneWall = "stone-wall", Entity
    SmallLamp = "small-lamp", Entity
    SciencePack1 = "science-pack-1", None
    SciencePack2 = "science-pack-2", None
    SciencePack3 = "science-pack-3", None
    MilitarySciencePack = "military-science-pack", None
    EngineUnit = "engine-unit", None

prototype_by_name = {prototype.value[0]: prototype for prototype in Prototype}

class Resource:
    Coal = "coal", ResourcePatch
    IronOre = "iron-ore", ResourcePatch
    CopperOre = "copper-ore", ResourcePatch
    Stone = "stone", ResourcePatch
    Water = "water", ResourcePatch
    CrudeOil = "crude-oil", ResourcePatch
    UraniumOre = "uranium-ore", ResourcePatch
    Wood = "wood", ResourcePatch