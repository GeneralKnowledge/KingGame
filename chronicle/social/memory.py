from __future__ import annotations

from chronicle.models.character import Character, Memory
from chronicle.models.events import WorldEvent
from chronicle.models.world import WorldState
from chronicle.world.ids import allocate_id

MAX_MEMORIES_PER_CHARACTER = 24

MEMORY_UTILITY_CAP = 0.35


def _prune_memories(char: Character) -> None:
    if len(char.memories) <= MAX_MEMORIES_PER_CHARACTER:
        return
    char.memories.sort(key=lambda m: (m.severity, m.day))
    char.memories = char.memories[-MAX_MEMORIES_PER_CHARACTER:]


def record_social_memories(
    world: WorldState,
    *,
    event: WorldEvent,
    actor_id: str,
    target_id: str,
    action: str,
    relationship_deltas: dict[str, dict[str, float]],
) -> list[str]:
    """Witness memories for the target; returns created memory ids."""
    target = world.characters.get(target_id)
    if not target or not target.alive:
        return []

    actor = world.characters.get(actor_id)
    actor_name = actor.name if actor else "someone"
    created: list[str] = []

    if action == "public_insult":
        delta = relationship_deltas.get("target_to_actor", {})
        resentment_gain = float(delta.get("resentment", 12.0))
        severity = min(0.95, 0.45 + resentment_gain / 25.0)
        mem = Memory(
            id=allocate_id(world, "mem"),
            day=world.day,
            actor_id=actor_id,
            source_event_id=event.id,
            summary=f"{actor_name} publicly humiliated me.",
            believed_summary=event.summary or None,
            severity=severity,
            emotional_tags=["humiliation", "resentment"],
        )
        target.memories.append(mem)
        created.append(mem.id)
    elif action == "private_apology":
        delta = relationship_deltas.get("target_to_actor", {})
        trust_gain = float(delta.get("trust", 8.0))
        severity = min(0.85, 0.35 + trust_gain / 30.0)
        mem = Memory(
            id=allocate_id(world, "mem"),
            day=world.day,
            actor_id=actor_id,
            source_event_id=event.id,
            summary=f"{actor_name} apologised to me in private.",
            believed_summary=event.summary or None,
            severity=severity,
            emotional_tags=["reconciliation", "trust"],
        )
        target.memories.append(mem)
        created.append(mem.id)

    _prune_memories(target)
    return created


def memory_utility_contribution(
    char: Character,
    action: str,
    *,
    target_id: str | None,
) -> float:
    if not target_id:
        return 0.0
    total = 0.0
    for mem in char.memories:
        if mem.forgiven or mem.disproved:
            continue
        if mem.actor_id != target_id:
            continue
        tags = set(mem.emotional_tags)
        if action == "public_insult" and "humiliation" in tags:
            total += 0.25 * mem.severity
        if action == "public_insult" and "reconciliation" in tags:
            total -= 0.08 * mem.severity
        if action == "private_apology" and "humiliation" in tags:
            total -= 0.12 * mem.severity
        if action == "private_apology" and "reconciliation" in tags:
            total += 0.06 * mem.severity
    return max(-MEMORY_UTILITY_CAP, min(MEMORY_UTILITY_CAP, total))
