from __future__ import annotations

import itertools
import re

from chronicle.models.world import WorldState

_counter = itertools.count(1)
_ID_SUFFIX = re.compile(r"_(\d+)$")


def reset_id_counter(start: int = 1) -> None:
    """Reset legacy global counter (generation-only compatibility)."""
    global _counter
    _counter = itertools.count(start)


def new_id(prefix: str) -> str:
    """Legacy global counter; prefer allocate_id(world, prefix) during simulation."""
    return f"{prefix}_{next(_counter)}"


def allocate_id(world: WorldState, prefix: str) -> str:
    entity_id = f"{prefix}_{world.next_entity_id}"
    world.next_entity_id += 1
    return entity_id


def _max_numeric_suffix(entity_id: str) -> int:
    match = _ID_SUFFIX.search(entity_id)
    return int(match.group(1)) if match else 0


def infer_next_entity_id(world: WorldState) -> int:
    """Lowest safe next serial from all entity IDs in the world."""
    max_seen = 0
    for char_id in world.characters:
        max_seen = max(max_seen, _max_numeric_suffix(char_id))
    for house_id in world.houses:
        max_seen = max(max_seen, _max_numeric_suffix(house_id))
    for title_id in world.titles:
        max_seen = max(max_seen, _max_numeric_suffix(title_id))
    for event in world.events:
        max_seen = max(max_seen, _max_numeric_suffix(event.id))
    max_seen = max(max_seen, _max_numeric_suffix(world.realm.id))
    return max(max_seen + 1, world.next_entity_id)


def sync_id_counter_from_world(world: WorldState) -> None:
    world.next_entity_id = infer_next_entity_id(world)
    reset_id_counter(world.next_entity_id)
