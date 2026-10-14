from __future__ import annotations

from typing import Any

from chronicle.character_ai.traits import migrate_legacy_traits
from chronicle.models.character import MaritalStatus
from chronicle.models.world import WorldState
from chronicle.world.ids import infer_next_entity_id

CURRENT_SCHEMA_VERSION = 3


def migrate_world_data(data: dict[str, Any]) -> dict[str, Any]:
    version = int(data.get("schema_version", 0))
    if version < 1:
        data = _migrate_to_v1(data)
        version = 1
    if version < 2:
        data = _migrate_to_v2(data)
        version = 2
    if version < 3:
        data = _migrate_to_v3(data)
    return data


def _migrate_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    day = int(data.get("day", 0))
    characters = data.get("characters", {})
    for char in characters.values():
        if "birth_day" not in char or char["birth_day"] is None:
            age = int(char.get("age_years", 0))
            char["birth_day"] = max(0, day - age * 365)
        if "death_day" not in char:
            char["death_day"] = None if char.get("alive", True) else day
        if "marital_status" not in char:
            if char.get("spouse_id"):
                char["marital_status"] = MaritalStatus.MARRIED.value
            else:
                char["marital_status"] = MaritalStatus.SINGLE.value
    data["schema_version"] = 1
    if "next_entity_id" not in data:
        data["next_entity_id"] = 1
    return data


def _migrate_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    for char in data.get("characters", {}).values():
        if "last_birth_day" not in char:
            char["last_birth_day"] = None
    data["schema_version"] = 2
    return data


def _migrate_to_v3(data: dict[str, Any]) -> dict[str, Any]:
    for char in data.get("characters", {}).values():
        if "tags" not in char:
            char["tags"] = []
        if "fertility_pair_multiplier" not in char:
            char["fertility_pair_multiplier"] = 1.0
        char["traits"] = migrate_legacy_traits(char.get("traits") or {})
    if "claims" not in data:
        data["claims"] = {}
    data["schema_version"] = 3
    return data


def apply_post_load_migrations(world: WorldState) -> WorldState:
    if world.schema_version < CURRENT_SCHEMA_VERSION:
        dumped = migrate_world_data(world.model_dump(mode="json"))
        world = WorldState.model_validate(dumped)
    world.next_entity_id = infer_next_entity_id(world)
    world.schema_version = CURRENT_SCHEMA_VERSION
    return world
