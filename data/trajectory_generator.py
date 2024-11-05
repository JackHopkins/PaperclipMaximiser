import math
import os

from factorio_entities import Position, BoundingBox
from factorio_instance import FactorioInstance, Direction
from factorio_types import Resource, prototype_by_name

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, NamedTuple
from dataclasses import dataclass
import json


@dataclass
class BlueprintEntity:
    entity_number: int
    name: str
    position: dict
    direction: int = 0
    recipe: Optional[str] = None
    neighbours: Optional[dict] = None
    type: Optional[str] = None
    items: Optional[dict] = None


class EntityPriority(Enum):
    MINER = 1
    ASSEMBLER = 2
    FURNACE = 3
    INSERTER = 4
    POWER = 5
    CHEST = 6
    BELT = 7

instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast = True,
                                cache_scripts=False,
                                inventory={
                                    'coal': 50,
                                    'copper-plate': 50,
                                    'burner-mining-drill': 10,
                                    'electric-mining-drill': 15,
                                    'transport-belt': 50,
                                    'stone-furnace': 10,
                                    'small-electric-pole': 15,
                                    'small-lamp': 10
                                })

def determine_resource_type(entities: List[BlueprintEntity]) -> Resource:
    """
    Determine which resource type the miners are likely targeting based on their positions.
    """
    miners = [e for e in entities if "mining-drill" in e.name]
    if not miners:
        return None

    # Use the first miner's position to guess the resource type
    first_miner = miners[0]
    if first_miner.position["x"] < 0:
        return Resource.CopperOre
    elif first_miner.position["x"] > 0:
        return Resource.IronOre
    else:
        return Resource.Coal

def find_valid_origin(entities: List[BlueprintEntity], resource: Resource, game: FactorioInstance) -> Position:
    """
    Find a valid origin position using nearest_buildable with bounding box.
    """
    miners = [e for e in entities if "mining-drill" in e.name]
    if not miners:
        return Position(x=0, y=0)

    # Calculate bounding box dimensions based on miner positions
    min_x = min(e.position["x"] for e in miners)
    max_x = max(e.position["x"] for e in miners)
    min_y = min(e.position["y"] for e in miners)
    max_y = max(e.position["y"] for e in miners)

    # Create bounding box relative to first miner
    base_miner = miners[0]
    left_top = Position(
        x=min_x - base_miner.position["x"],
        y=min_y - base_miner.position["y"]
    )
    right_bottom = Position(
        x=max_x - base_miner.position["x"],
        y=max_y - base_miner.position["y"]
    )
    center = Position(
        x=(left_top.x + right_bottom.x) / 2,
        y=(left_top.y + right_bottom.y) / 2
    )

    bounding_box = BoundingBox(
        left_top=left_top,
        right_bottom=right_bottom,
        center=center
    )

    # Use nearest_buildable to find valid position
    return game.nearest_buildable(
        prototype_by_name[base_miner.name],
        bounding_box=bounding_box
    )

def create_origin_finding_code_trace(entities, resource):
    """
    Generate code trace for finding origin using nearest_buildable.
    """
    miners = [e for e in entities if "mining-drill" in e.name]
    if not miners:
        return []

    # Calculate bounding box dimensions
    min_x = min(e.position["x"] for e in miners)
    max_x = max(e.position["x"] for e in miners)
    min_y = min(e.position["y"] for e in miners)
    max_y = max(e.position["y"] for e in miners)

    # Create relative bounding box calculations
    base_miner = miners[0]
    trace = [
        f"# Find suitable origin position for miners on {resource[0]}",
        "",
        "# Calculate bounding box for miners",
        f"left_top = Position(",
        f"    x={min_x - base_miner.position['x']},",
        f"    y={min_y - base_miner.position['y']}",
        ")",
        f"right_bottom = Position(",
        f"    x={max_x - base_miner.position['x']},",
        f"    y={max_y - base_miner.position['y']}",
        ")",
        "center = Position(",
        "    x=(left_top.x + right_bottom.x) / 2,",
        "    y=(left_top.y + right_bottom.y) / 2",
        ")",
        "",
        "miner_box = BoundingBox(",
        "    left_top=left_top,",
        "    right_bottom=right_bottom,",
        "    center=center",
        ")",
        "",
        f"# Find valid position for miners using nearest_buildable",
        f"origin = game.nearest_buildable(",
        f"    Prototype.{prototype_by_name[base_miner.name].name},",
        f"    bounding_box=miner_box",
        ")",
        "",
        "assert origin, 'Could not find valid position for miners'",
        "",
        "# Move to origin position",
        "game.move_to(origin)",
        ""
    ]

    return trace

def find_belt_segments(entities: List[BlueprintEntity]) -> List[List[BlueprintEntity]]:
    """
    Find contiguous segments of transport belts.
    Returns list of lists, where each inner list is a contiguous belt segment.
    """
    # Get all belt entities
    belt_entities = [e for e in entities if is_transport_belt(e.name)]
    if not belt_entities:
        return []

    # Create a position map for quick lookup
    pos_map = {(e.position["x"], e.position["y"]): e for e in belt_entities}

    def get_neighbors(entity: BlueprintEntity) -> List[BlueprintEntity]:
        """Get adjacent belt entities."""
        x, y = entity.position["x"], entity.position["y"]
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_pos = (x + dx, y + dy)
            if neighbor_pos in pos_map:
                neighbors.append(pos_map[neighbor_pos])
        return neighbors

    # Find connected segments using DFS
    segments = []
    visited = set()

    def dfs(entity: BlueprintEntity, current_segment: List[BlueprintEntity]):
        visited.add((entity.position["x"], entity.position["y"]))
        current_segment.append(entity)
        for neighbor in get_neighbors(entity):
            pos = (neighbor.position["x"], neighbor.position["y"])
            if pos not in visited:
                dfs(neighbor, current_segment)

    for belt in belt_entities:
        pos = (belt.position["x"], belt.position["y"])
        if pos not in visited:
            current_segment = []
            dfs(belt, current_segment)
            segments.append(current_segment)

    return segments


def find_segment_endpoints(segment: List[BlueprintEntity]) -> Tuple[BlueprintEntity, BlueprintEntity]:
    """
    Find the start and end points of a belt segment.
    Returns (start_entity, end_entity).
    """
    if len(segment) == 1:
        return segment[0], segment[0]

    # Create a position map
    pos_map = {(e.position["x"], e.position["y"]): e for e in segment}

    # Find entities with only one neighbor
    endpoints = []
    for entity in segment:
        x, y = entity.position["x"], entity.position["y"]
        neighbor_count = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                             if (x + dx, y + dy) in pos_map)
        if neighbor_count == 1:
            endpoints.append(entity)

    # If we have exactly two endpoints, use them
    if len(endpoints) == 2:
        # Sort endpoints to maintain consistent ordering
        endpoints.sort(key=lambda e: (e.position["x"], e.position["y"]))
        return endpoints[0], endpoints[1]

    # If no clear endpoints (loop) or single belt, use first and last placed
    segment.sort(key=lambda e: e.entity_number)
    return segment[0], segment[-1]

def get_entity_priority(entity_name: str) -> EntityPriority:
    """Determine placement priority for different entity types."""
    if "mining-drill" in entity_name:
        return EntityPriority.MINER
    elif "assembling-machine" in entity_name:
        return EntityPriority.ASSEMBLER
    elif "furnace" in entity_name:
        return EntityPriority.FURNACE
    elif "inserter" in entity_name:
        return EntityPriority.INSERTER
    elif "electric-pole" in entity_name or "substation" in entity_name:
        return EntityPriority.POWER
    elif "chest" in entity_name:
        return EntityPriority.CHEST
    elif "belt" in entity_name or "splitter" in entity_name:
        return EntityPriority.BELT
    return EntityPriority.CHEST  # Default priority

def is_transport_belt(entity_name: str) -> bool:
    """Check if an entity is a transport belt."""
    return "transport-belt" in entity_name or "splitter" in entity_name or "underground-belt" in entity_name

def direction_to_enum(direction: int) -> str:
    """Convert numeric direction to Direction enum name."""
    direction_map = {
        0: "UP",
        2: "RIGHT",
        4: "DOWN",
        6: "LEFT"
    }
    return direction_map.get(direction, "UP")


class EntityPlacement(NamedTuple):
    entity: BlueprintEntity
    reference_entity: Optional[int]  # entity_number of reference entity
    relative_position: Optional[tuple]  # (x_offset, y_offset) from reference


def find_placement_references(entities: List[BlueprintEntity]) -> List[EntityPlacement]:
    """
    Determine relative positioning between entities.
    Returns list of EntityPlacement objects with reference entities and offsets.
    """
    placements = []
    placed_entities = {}  # Map of positions to entity numbers

    # Sort entities by priority
    sorted_entities = sorted(
        entities,
        key=lambda e: (get_entity_priority(e.name).value, e.entity_number)
    )

    for entity in sorted_entities:
        current_pos = (entity.position["x"], entity.position["y"])

        # Find closest already-placed entity
        closest_reference = None
        min_distance = float('inf')
        relative_pos = None

        for placed_pos, placed_num in placed_entities.items():
            dx = current_pos[0] - placed_pos[0]
            dy = current_pos[1] - placed_pos[1]
            distance = abs(dx) + abs(dy)  # Manhattan distance

            if distance < min_distance and (dx == 0 or dy == 0):
                min_distance = distance
                closest_reference = placed_num
                relative_pos = (dx, dy)

        placements.append(EntityPlacement(entity, closest_reference, relative_pos))
        placed_entities[current_pos] = entity.entity_number

    return placements

def get_tile_dimensions_of_all_entities(entities: List[BlueprintEntity]) -> Dict[str, Tuple[int, int]]:
    tile_dimensions = {}
    # Get counts of entitiies
    entity_counts = {}
    for entity in entities:
        entity_counts[entity.name] = entity_counts.get(entity.name, 0) + 1
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                cache_scripts=False,
                                inventory=entity_counts)
    # get set of entities by name
    entity_names = set([entity.name for entity in entities])
    position = instance.nearest(Resource.IronOre)
    instance.move_to(position)
    # get tile dimensions of all entities
    for entity_name in entity_names:
        entity = instance.place_entity(prototype_by_name[entity_name], Direction.UP, position)
        tile_dimensions[entity_name] = (entity.tile_dimensions.tile_width, entity.tile_dimensions.tile_height)
        instance.pickup_entity(entity)

    return tile_dimensions


def generate_entity_variable_name(entity_name: str, entities: List[BlueprintEntity], entity_number: int) -> str:
    """
    Generate a variable name for an entity based on naming conventions:
    - Single entities use just the entity name
    - Multiple instances use name with index
    """
    # Convert entity name to snake case
    name = entity_name.replace("-", "_")

    # Count how many entities of this type exist
    count = sum(1 for e in entities if e.name == entity_name)

    if count == 1:
        return name
    else:
        # Find the index of this entity among entities of the same type
        index = sum(1 for e in entities
                    if e.name == entity_name and e.entity_number < entity_number)
        return f"{name}_{index + 1}"


def convert_blueprint_to_trace(blueprint_json: str) -> List[str]:
    """Convert a Factorio blueprint JSON to a sequence of game commands."""
    blueprint = json.loads(blueprint_json)
    entities = [BlueprintEntity(**e) for e in blueprint["entities"]]

    # Determine resource type
    resource = determine_resource_type(entities)

    miners = [p for p in entities if "mining-drill" in p.name]

    origin = find_valid_origin(entities, resource, instance)

    trace = []
    if resource and miners:
        trace.extend(create_origin_finding_code_trace(entities, resource))
    else:
        trace.append("origin = Position(x=0, y=0)")
        trace.append("")

    # Split entities into belts and non-belts
    belt_entities = [e for e in entities if is_transport_belt(e.name)]
    non_belt_entities = [e for e in entities if not is_transport_belt(e.name)]

    # Process non-belt entities first
    placements = find_placement_references(non_belt_entities)

    # Find belt segments
    belt_segments = find_belt_segments(belt_entities)

    tile_dimensions = get_tile_dimensions_of_all_entities(entities)

    placed_entity_vars = {}  # Map of entity numbers to their variable names
    placed_entity = {}

    # Place entities
    for placement in placements:
        entity = placement.entity
        entity_var = generate_entity_variable_name(entity.name, entities, entity.entity_number)
        placed_entity_vars[entity.entity_number] = entity_var
        placed_entity[entity.entity_number] = entity

        trace.append(f"# Place {entity.name}")

        if placement.reference_entity is None:
            trace.append(f"game.move_to(origin+Position(x={entity.position['x']},y={entity.position['y']})))")
            if "mining-drill" in entity.name:
                trace.append(
                    f"{entity_var} = game.place_entity("
                    f"Prototype.{prototype_by_name[entity.name].name}, "
                    f"direction=Direction.{direction_to_enum(entity.direction)}, "
                    f"position=origin+Position(x={entity.position['x']},y={entity.position['y']}))"
                )
            else:
                trace.append(
                    f"{entity_var} = game.place_entity("
                    f"Prototype.{prototype_by_name[entity.name].name}, "
                    f"direction=Direction.{direction_to_enum(entity.direction)})"
                )
        else:
            ref_var = placed_entity_vars[placement.reference_entity]
            ref = placed_entity[placement.reference_entity]
            dx, dy = placement.relative_position

            direction_words = []
            position_ref_modifier = [""]
            spacing = 0
            if abs(dx) != 0 and abs(dy) != 0:
                raise ValueError("Diagonal placement not supported")
            if abs(dx) > abs(dy):
                direction_words = ["RIGHT" if dx > 0 else "LEFT"]
                spacing = abs(dx)
                spacing -= tile_dimensions[entity.name][0]

                if 0 < abs(dy) < 1:
                    if dy > 0 and ref.name != 'burner-mining-drill': # We should generalise this to all entities larger than 1x1
                        position_ref_modifier = [".above()"]*abs(dy)
                    if dy < 0:
                        position_ref_modifier = [".below()"]*abs(dy)
                elif abs(dy) > 1:
                    position_ref_modifier = [f" + Position(x=0, y={dy})"]

            else:
                direction_words = ["DOWN" if dy > 0 else "UP"]
                spacing = abs(dy)
                spacing -= tile_dimensions[entity.name][1]
                if 0 < abs(dx) < 1:
                    if dx > 0 and ref.name != 'burner-mining-drill': # We should generalise this to all entities larger than 1x1
                        position_ref_modifier = [".right()"]*abs(dx)
                    if dx < 0:
                        position_ref_modifier = [".left()"]*abs(dx)
                elif abs(dx) > 1:
                    position_ref_modifier = [f" + Position(x={dx}, y=0)"]


            placement_cmd = (
                f"{entity_var} = game.place_entity_next_to("
                f"Prototype.{prototype_by_name[entity.name].name}, "
                f"reference_position={ref_var}.position{''.join(position_ref_modifier)}, "
                f"direction=Direction.{direction_words[0]}"
            )

            if math.floor(spacing) != 0:
                placement_cmd += f", spacing={math.floor(spacing)})"
            else:
                placement_cmd += ")"

            trace.append(placement_cmd)

            # Rotate entity if necessary
            trace.append(
                f"{entity_var} = game.rotate_entity({entity_var}, Direction.{direction_to_enum(entity.direction)})"
            )

        trace.append(
            f"assert {entity_var}, "
            f"'Failed to place {entity.name}'"
        )

        if entity.recipe:
            trace.append(
                f"game.set_entity_recipe({entity_var}, "
                f"Prototype.{prototype_by_name[entity.recipe].name})"
            )

        trace.append("")

    # Place belt segments
    # Place belt segments
    for segment_idx, segment in enumerate(belt_segments):
        start, end = find_segment_endpoints(segment)

        # If the start needs to connect to a non-belt entity, reference that
        trace.append(f"# Place transport belt segment {segment_idx + 1}")

        # Generate variable names for the segment endpoints
        start_var = generate_entity_variable_name(start.name, entities, start.entity_number)
        end_var = generate_entity_variable_name(end.name, entities, end.entity_number)

        # Find reference points for the belt segment
        start_ref = None
        end_ref = None

        # Look for non-belt entities near the start/end points to connect to
        start_closest_entity, end_closest_entity = None, None
        start_closest_var, end_closest_var = None, None
        start_closest_distance, end_closest_distance = float('inf'), float('inf')
        for entity in non_belt_entities:
            start_distance = abs(entity.position["x"] - start.position["x"]) + abs(entity.position["y"] - start.position["y"])
            end_distance = abs(entity.position["x"] - end.position["x"]) + abs(entity.position["y"] - end.position["y"])
            if start_distance < start_closest_distance:
                start_closest_entity = entity
                start_closest_distance = start_distance
                start_closest_var = placed_entity_vars[entity.entity_number]
            if end_distance < end_closest_distance:
                end_closest_entity = entity
                end_closest_distance = end_distance
                end_closest_var = placed_entity_vars[entity.entity_number]

            if abs(entity.position["x"] - start.position["x"]) <= 1 and \
                    abs(entity.position["y"] - start.position["y"]) <= 1:
                start_ref = f"{placed_entity_vars[entity.entity_number]}.position"
            if abs(entity.position["x"] - end.position["x"]) <= 1 and \
                    abs(entity.position["y"] - end.position["y"]) <= 1:
                end_ref = f"{placed_entity_vars[entity.entity_number]}.position"

        if not start_ref:
            dx = start.position["x"] - start_closest_entity.position["x"]
            dy = start.position["y"] - start_closest_entity.position["y"]
            start_ref = f"Position(x={start_closest_var}.position.x+{dx}, y={start_closest_var}.position.y+{dy})"
            #start_ref = f"Position(x={start.position['x']}, y={start.position['y']})"
        if not end_ref:
            dx = end.position["x"] - end_closest_entity.position["x"]
            dy = end.position["y"] - end_closest_entity.position["y"]
            end_ref = f"Position(x={end_closest_var}.position.x+{dx}, y={end_closest_var}.position.y+{dy})"

        # Connect the belt segment
        trace.append(
            f"belt_segment_{segment_idx + 1} = game.connect_entities("
            f"{start_ref}, {end_ref}, "
            f"connection_type=Prototype.TransportBelt)"
        )

        # Store references to placed belts
        trace.append(
            f"assert belt_segment_{segment_idx + 1}, "
            f"'Failed to place belt segment {segment_idx + 1}'"
        )
        trace.append("")


    # Add final verification
    # trace.append("# Verify setup")
    # trace.append("entities = game.inspect_entities(resource_patch.bounding_box.center, radius=10)")
    #
    # # Use consistent entity naming in verification
    # for entity in entities:
    #     entity_var = generate_entity_variable_name(entity.name, entities, entity.entity_number)
    #     trace.append(
    #         f"assert entities.get_entity(Prototype.{prototype_by_name[entity.name].name}), "
    #         f"'{entity_var} not found in setup'"
    #     )

    trace.append("\nprint('Successfully placed all blueprint entities')")

    return trace


def generate_trace(blueprint_json: str) -> str:
    """Generate the complete trace as a string."""
    trace_lines = convert_blueprint_to_trace(blueprint_json)
    return "\n".join(trace_lines)

# get execution dir dynamically
execution_dir = os.path.dirname(os.path.realpath(__file__)) + "/blueprints/mining/"
filename = "Early Mining"

# generate if python file doesn't exist

if not os.path.exists(execution_dir+filename+".py"):
    with open(execution_dir+filename+".json", "r") as f:
        blueprint_json = f.read()
        trace = generate_trace(blueprint_json)
        # write to python file in same directory
        with open(execution_dir+filename+".py", "w") as f1:
            f1.write(trace.replace("game.", ""))

try:
   result = instance.run_snippet_file_in_factorio_env(execution_dir+filename+".py", clean=True)
   pass
except Exception as e:
    print(e)
    print("Error running snippet in Factorio environment")
    exit(1)