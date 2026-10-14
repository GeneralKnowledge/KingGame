from __future__ import annotations

import hashlib
import random

from chronicle.character_ai import goals as goal_logic
from chronicle.character_ai.utility import ActionKind, choose_action, eligible_social_actors
from chronicle.events.resolver import resolve_social_action
from chronicle.models.world import WorldState


def _cohort_slot(char_id: str) -> int:
    digest = hashlib.md5(char_id.encode(), usedforsecurity=False).hexdigest()
    return int(digest[:8], 16) % 7


def is_agency_day_for(world: WorldState, char_id: str) -> bool:
    return _cohort_slot(char_id) == world.day % 7


def process_daily_agency(world: WorldState, _rng: random.Random) -> None:
    if world.day % 7 == 0:
        for char in eligible_social_actors(world):
            goal_logic.refresh_goals(world, char, world.day)

    for char in eligible_social_actors(world):
        if not is_agency_day_for(world, char.id):
            continue
        char_rng = random.Random(f"{world.seed}:{world.day}:agency:{char.id}")
        action, target_id, snapshot = choose_action(world, char, char_rng)
        if action == ActionKind.WAIT:
            continue
        resolve_social_action(
            world,
            char.id,
            action,
            target_id,
            motive_snapshot=snapshot,
        )
