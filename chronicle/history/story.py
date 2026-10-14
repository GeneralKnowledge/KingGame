from __future__ import annotations

from chronicle.models.events import EventKind, WorldEvent
from chronicle.models.house import TitleKind
from chronicle.models.world import WorldState


def _county_holder_id(world: WorldState) -> str | None:
    county_id = world.realm.county_title_id
    title = world.titles.get(county_id)
    return title.holder_id if title else None


def _title_rank(world: WorldState, char_id: str) -> int:
    """Higher = closer to county holder (story focus)."""
    rank = 0
    for title in world.titles.values():
        if title.holder_id != char_id:
            continue
        if title.kind == TitleKind.COUNTY:
            rank = max(rank, 100)
        elif title.kind == TitleKind.LORDSHIP:
            rank = max(rank, 70)
        elif title.kind == TitleKind.HOUSE_HEAD:
            rank = max(rank, 50)
    char = world.characters.get(char_id)
    if char:
        if char.role == "noble":
            rank = max(rank, 40)
        elif char.role == "knight":
            rank = max(rank, 30)
        elif char.role == "courtier":
            rank = max(rank, 20)
        elif char.role in ("peasant", "servant"):
            rank = max(rank, 5)
    return rank


def story_importance(world: WorldState, char_id: str) -> float:
    """Derived 0–1 score for chronicle/UI focus (not simulation authority)."""
    char = world.characters.get(char_id)
    if not char or not char.alive:
        return 0.0
    score = _title_rank(world, char_id) / 100.0
    holder = _county_holder_id(world)
    if holder and char_id == holder:
        score = max(score, 1.0)
    if char.spouse_id == holder:
        score = max(score, 0.75)
    if holder and char.house_id and holder in world.characters:
        liege = world.characters[holder]
        if liege.house_id == char.house_id:
            score = max(score, 0.55)
    event_hits = sum(
        1
        for e in world.events[-500:]
        if e.actor_id == char_id or e.target_id == char_id or char_id in e.participant_ids
    )
    score += min(0.25, event_hits * 0.01)
    if world.claims and any(c.character_id == char_id for c in world.claims.values()):
        score = max(score, 0.6)
    return min(1.0, score)


def is_named_cast(world: WorldState, char_id: str, *, threshold: float = 0.35) -> bool:
    return story_importance(world, char_id) >= threshold


def event_significance(world: WorldState, event: WorldEvent) -> float:
    """Rank chronicle lines; succession crises and claims rank highest."""
    base = 0.2
    if event.kind == EventKind.SUCCESSION:
        base = 0.85
        if event.effects.get("disputed") or event.effects.get("vacant"):
            base = 0.95
        if event.effects.get("childless"):
            base = 1.0
    elif event.kind == EventKind.DEATH:
        actor = world.characters.get(event.actor_id) if event.actor_id else None
        if actor and story_importance(world, actor.id) >= 0.35:
            base = 0.55
    elif event.kind == EventKind.MARRIAGE:
        if story_importance(world, event.actor_id or "") >= 0.35:
            base = 0.45
    elif event.kind == EventKind.BIRTH:
        base = 0.15
        if event.effects.get("heir_relevant"):
            base = 0.5
    elif event.kind in (EventKind.SCHEME, EventKind.PROMISE, EventKind.RUMOUR):
        base = 0.6
    if event.effects.get("disputed"):
        base = max(base, 0.9)
    return base
