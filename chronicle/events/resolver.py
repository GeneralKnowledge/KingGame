from __future__ import annotations

from dataclasses import dataclass

from chronicle.character_ai import goals as goal_logic
from chronicle.character_ai.utility import ActionKind
from chronicle.history.log import append_event
from chronicle.models.events import EventKind
from chronicle.models.world import WorldState
from chronicle.social.dynamics import apply_action_deltas


@dataclass(frozen=True)
class ResolveOutcome:
    success: bool
    reason: str
    event_id: str | None = None


def resolve_social_action(
    world: WorldState,
    actor_id: str,
    action: ActionKind,
    target_id: str | None,
    *,
    motive_snapshot: dict[str, float] | None = None,
) -> ResolveOutcome:
    actor = world.characters.get(actor_id)
    if not actor or not actor.alive:
        return ResolveOutcome(False, "actor_invalid")

    if action == ActionKind.WAIT:
        return ResolveOutcome(True, "wait")

    if not target_id:
        return ResolveOutcome(False, "missing_target")
    target = world.characters.get(target_id)
    if not target or not target.alive:
        return ResolveOutcome(False, "target_invalid")
    if target_id == actor_id:
        return ResolveOutcome(False, "self_target")

    deltas = apply_action_deltas(world, actor_id, target_id, action)
    summary = _format_summary(world, actor_id, target_id, action)
    event = append_event(
        world,
        day=world.day,
        kind=EventKind.CUSTOM,
        actor_id=actor_id,
        target_id=target_id,
        effects={
            "action": action.value,
            "relationship_deltas": deltas,
            "motive_snapshot": motive_snapshot or {},
            "outcome_status": "success",
        },
        summary=summary,
    )
    goal_logic.complete_goals_after_action(actor, action.value, target_id)
    return ResolveOutcome(True, "success", event.id)


def _format_summary(
    world: WorldState, actor_id: str, target_id: str, action: ActionKind
) -> str:
    actor = world.characters[actor_id]
    target = world.characters[target_id]
    if action == ActionKind.PUBLIC_INSULT:
        return f"{actor.name} publicly insulted {target.name}."
    if action == ActionKind.PRIVATE_APOLOGY:
        return f"{actor.name} apologised privately to {target.name}."
    return f"{actor.name} acted toward {target.name}."
