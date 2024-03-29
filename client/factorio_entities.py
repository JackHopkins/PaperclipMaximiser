from typing import Tuple, Any
from typing import List, Optional

from pydantic import BaseModel


class Inventory:
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs

    def __getitem__(self, key):
        try:
            name, _entity = key
        except Exception as e:
            pass
        return self.__dict__[name] if name in self.__dict__ else 0

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class BoundingBox(BaseModel):
    left_top: Tuple[float, float]
    right_bottom: Tuple[float, float]


class ResourcePatch(BaseModel):
    name: str
    size: int
    bounding_box: BoundingBox


class Position(BaseModel):
    x: float
    y: float


class Dimensions(BaseModel):
    width: float
    height: float


class TileDimensions(BaseModel):
    tile_width: float
    tile_height: float


class Ingredient(BaseModel):
    name: str
    count: int


class Recipe(BaseModel):
    name: str
    ingredients: List[Ingredient]


class BurnerType(BaseModel):
    fuel: Optional[str]
    remaining_burning_fuel: Optional[float] = 0


class Entity(BaseModel):
    name: str
    position: Position
    direction: int
    energy: float
    type: str
    dimensions: Dimensions
    tile_dimensions: TileDimensions
    prototype: Any #Prototype
    health: float


class TransportBelt(Entity):
    input_position: Position
    output_position: Position


class Inserter(Entity):
    pickup_position: Position
    drop_position: Position


class MiningDrill(Entity):
    drop_position: Position


class BurnerInserter(Inserter, BurnerType):
    pass


class BurnerMiningDrill(MiningDrill, BurnerType):
    pass


class AssemblingMachine(Entity):
    recipe: Optional[Any] # Prototype


class FluidHandler(Entity):
    connection_points: List[Position]


class Boiler(FluidHandler):
    steam_output_point: Position


class Generator(FluidHandler):
    pass


class OffshorePump(FluidHandler):
    fluid_box: List[dict]


class Furnace(Entity, BurnerType):
    input_ingredients: Optional[List[Ingredient]] = []





###

class FactorioEntity(BaseModel):
    position: Tuple[int, int] = (0, 0)
    top_left: Tuple[int, int] = (0, 0)
    bottom_right: Tuple[int, int] = (0, 0)


class FactorioEntityPrototype:
    class OffshorePump(FactorioEntity):
        fluid: str = "water"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class SmallElectricPole(FactorioEntity):
        wire_reach: int = 7
        supply_area_distance: int = 5

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class StoneFurnace(FactorioEntity):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class BurnerMiningDrill(FactorioEntity):
        drop_position: Tuple[int, int] = (0, 0)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class TransportBelt(FactorioEntity):
        direction: str = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class OffshorePump(FactorioEntity):
        fluid: str = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class Lab(FactorioEntity):
        research_speed: float = 1.0

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class Radar(FactorioEntity):
        scanning_radius: int = 14

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class Pipe(FactorioEntity):
        fluid_box: dict = {}

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class Boiler(FactorioEntity):
        energy_source: str = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class SteamEngine(FactorioEntity):
        fluid_input: dict = {}

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class ElectricMiningDrill(FactorioEntity):
        resource_categories: list = []

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class AssemblingMachine(FactorioEntity):
        crafting_categories: list = []

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)

    class BurnerInserter(FactorioEntity):
        pickup_position: Tuple[int, int] = (0, 0)
        drop_position: Tuple[int, int] = (0, 0)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __call__(self, **kwargs):
            return self.__class__(**kwargs)