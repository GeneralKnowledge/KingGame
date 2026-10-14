from __future__ import annotations

from chronicle.models.events import EventKind, WorldEvent
from chronicle.models.world import WorldState


def _name(world: WorldState, char_id: str | None) -> str:
    if not char_id:
        return "someone"
    c = world.characters.get(char_id)
    return c.name if c else char_id


def render_chronicle_entry(world: WorldState, event: WorldEvent) -> str:
    if event.summary:
        return f"Day {event.day}: {event.summary}"

    actor = _name(world, event.actor_id)
    target = _name(world, event.target_id)

    if event.kind == EventKind.BIRTH:
        return f"Day {event.day}: {target} was born."
    if event.kind == EventKind.DEATH:
        return f"Day {event.day}: {actor} died at age {event.effects.get('age', '?')}."
    if event.kind == EventKind.MARRIAGE:
        return f"Day {event.day}: {actor} and {target} were wed."
    if event.kind == EventKind.INHERITANCE:
        title = event.effects.get("title_name", "a title")
        return f"Day {event.day}: {actor} inherited {title}."
    if event.kind == EventKind.SUCCESSION:
        return f"Day {event.day}: {actor} became head of their house."

    return f"Day {event.day}: {event.kind.value} involving {actor}."


def render_recent_chronicle(
    world: WorldState,
    limit: int = 40,
    *,
    named_cast_only: bool = False,
) -> list[str]:
    from chronicle.history.story import event_significance, is_named_cast

    pool = world.events[- max(limit * 3, 120) :]
    scored: list[tuple[float, int, WorldEvent]] = []
    for idx, event in enumerate(pool):
        if named_cast_only:
            ids = [
                event.actor_id,
                event.target_id,
                *event.participant_ids,
            ]
            if not any(i and is_named_cast(world, i) for i in ids):
                continue
        scored.append((event_significance(world, event), idx, event))
    scored.sort(key=lambda x: (-x[0], -x[2].day, -x[1]))
    top = scored[:limit]
    return [render_chronicle_entry(world, e) for _, _, e in top]
