from __future__ import annotations

from chronicle.models.events import WorldEvent
from chronicle.models.world import WorldState
from chronicle.world.ids import new_id


def append_event(
    world: WorldState,
    *,
    day: int,
    kind: WorldEvent.model_fields["kind"].annotation,  # type: ignore[name-defined]
    actor_id: str | None = None,
    target_id: str | None = None,
    participant_ids: list[str] | None = None,
    causes: list[str] | None = None,
    effects: dict | None = None,
    summary: str = "",
) -> WorldEvent:
    event = WorldEvent(
        id=new_id("evt"),
        day=day,
        kind=kind,
        actor_id=actor_id,
        target_id=target_id,
        participant_ids=participant_ids or [],
        causes=causes or [],
        effects=effects or {},
        summary=summary,
    )
    world.events.append(event)
    return event
