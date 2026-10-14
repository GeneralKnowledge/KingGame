from __future__ import annotations

from chronicle.models.character import Character, Goal
from chronicle.models.world import WorldState

MAX_ACTIVE_GOALS = 5
RESENTMENT_SETTLE_THRESHOLD = 55.0

GOAL_KINDS = frozenset(
    {"press_claim", "settle_score", "seek_alliance", "protect_house", "wait"}
)


def _clamp_priority(value: float) -> float:
    return max(0.05, min(0.95, value))


def prune_obsolete_goals(world: WorldState, char: Character) -> None:
    kept: list[Goal] = []
    for goal in char.goals:
        if goal.target_id and goal.target_id not in world.characters:
            continue
        target = world.characters.get(goal.target_id) if goal.target_id else None
        if target is not None and not target.alive:
            continue
        if goal.kind == "press_claim" and goal.target_id:
            title_id = goal.target_id
            title = world.titles.get(title_id)
            if title and title.holder_id == char.id:
                continue
        kept.append(goal)
    char.goals = kept[:MAX_ACTIVE_GOALS]


def _maybe_add_settle_score(world: WorldState, char: Character) -> None:
    for other in world.living_characters():
        if other.id == char.id:
            continue
        rel = world.get_relationship(char.id, other.id)
        if rel.resentment < RESENTMENT_SETTLE_THRESHOLD:
            continue
        if any(g.kind == "settle_score" and g.target_id == other.id for g in char.goals):
            continue
        priority = _clamp_priority(0.35 + rel.resentment / 200.0)
        char.goals.append(Goal(kind="settle_score", priority=priority, target_id=other.id))
        if len(char.goals) >= MAX_ACTIVE_GOALS:
            return


def _maybe_add_seek_alliance(world: WorldState, char: Character) -> None:
    if char.spouse_id or char.role not in ("noble", "knight"):
        return
    if any(g.kind == "seek_alliance" for g in char.goals):
        return
    if char.age_years < 18 or char.age_years > 40:
        return
    char.goals.append(Goal(kind="seek_alliance", priority=0.45, target_id=None))


def _maybe_add_protect_house(world: WorldState, char: Character) -> None:
    if not char.house_id:
        return
    house = world.houses.get(char.house_id)
    if not house or house.head_character_id != char.id:
        return
    if any(g.kind == "protect_house" and g.target_id == char.house_id for g in char.goals):
        return
    char.goals.append(
        Goal(kind="protect_house", priority=0.5, target_id=char.house_id)
    )


def refresh_goals(world: WorldState, char: Character, day: int) -> None:
    prune_obsolete_goals(world, char)
    _maybe_add_settle_score(world, char)
    _maybe_add_seek_alliance(world, char)
    _maybe_add_protect_house(world, char)
    if day % 7 == 0:
        for goal in char.goals:
            goal.priority = _clamp_priority(goal.priority * 0.98 + 0.02)


def goal_utility_contribution(
    goal: Goal,
    action: str,
    *,
    target_id: str | None,
) -> float:
    if goal.kind == "settle_score" and action == "public_insult":
        if target_id and goal.target_id == target_id:
            return 0.55 * goal.priority
    if goal.kind == "press_claim" and action == "public_insult":
        if target_id and goal.target_id != target_id:
            return 0.0
        return 0.15 * goal.priority
    if goal.kind == "seek_alliance" and action == "private_apology":
        return 0.2 * goal.priority
    if goal.kind == "protect_house" and action == "wait":
        return 0.1 * goal.priority
    return 0.0


def complete_goals_after_action(
    char: Character,
    action: str,
    target_id: str | None,
) -> None:
    if action != "public_insult" or not target_id:
        return
    remaining: list[Goal] = []
    for goal in char.goals:
        if goal.kind == "settle_score" and goal.target_id == target_id:
            continue
        remaining.append(goal)
    char.goals = remaining
