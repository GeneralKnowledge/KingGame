from __future__ import annotations

from chronicle.character_ai.utility import ActionKind
from chronicle.models.world import WorldState


def _clamp_axis(value: float) -> float:
    return max(0.0, min(100.0, value))


def apply_action_deltas(
    world: WorldState,
    actor_id: str,
    target_id: str,
    action: ActionKind,
) -> dict[str, dict[str, float]]:
    """Directional relationship changes; returns summary for event effects."""
    rel = world.get_relationship(target_id, actor_id)
    before = {
        "affection": rel.affection,
        "trust": rel.trust,
        "respect": rel.respect,
        "fear": rel.fear,
        "resentment": rel.resentment,
        "envy": rel.envy,
    }

    if action == ActionKind.PUBLIC_INSULT:
        rel.resentment = _clamp_axis(rel.resentment + 12.0)
        rel.respect = _clamp_axis(rel.respect - 8.0)
        rel.affection = _clamp_axis(rel.affection - 5.0)
        actor_to_target = world.get_relationship(actor_id, target_id)
        actor_to_target.fear = _clamp_axis(actor_to_target.fear + 2.0)
    elif action == ActionKind.PRIVATE_APOLOGY:
        rel.affection = _clamp_axis(rel.affection + 10.0)
        rel.trust = _clamp_axis(rel.trust + 8.0)
        rel.resentment = _clamp_axis(rel.resentment - 15.0)
        rel.respect = _clamp_axis(rel.respect + 4.0)

    after = {
        "affection": rel.affection,
        "trust": rel.trust,
        "respect": rel.respect,
        "fear": rel.fear,
        "resentment": rel.resentment,
        "envy": rel.envy,
    }
    return {
        "target_to_actor": {
            k: after[k] - before[k] for k in before
        }
    }
