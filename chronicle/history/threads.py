from __future__ import annotations

from chronicle.models.events import WorldEvent
from chronicle.models.world import WorldState


def event_by_id(world: WorldState) -> dict[str, WorldEvent]:
    return {event.id: event for event in world.events}


def walk_causes_backward(
    world: WorldState,
    event_id: str,
    *,
    max_depth: int = 12,
) -> list[WorldEvent]:
    """Root-first chain along causes links (event-id references only)."""
    index = event_by_id(world)
    chain: list[WorldEvent] = []
    current_id: str | None = event_id
    depth = 0
    while current_id and depth < max_depth:
        event = index.get(current_id)
        if not event:
            break
        chain.append(event)
        parent_id = _first_event_cause(event, index)
        current_id = parent_id
        depth += 1
    chain.reverse()
    return chain


def _first_event_cause(event: WorldEvent, index: dict[str, WorldEvent]) -> str | None:
    for cause_id in event.causes:
        if cause_id in index:
            return cause_id
    return None


def collect_descendants(
    world: WorldState,
    root_id: str,
    *,
    max_nodes: int = 16,
) -> list[WorldEvent]:
    """Events that cite root_id (directly or transitively) in causes, day order."""
    index = event_by_id(world)
    if root_id not in index:
        return []

    frontier = [root_id]
    seen: set[str] = {root_id}
    ordered: list[WorldEvent] = [index[root_id]]

    while frontier and len(ordered) < max_nodes:
        parent = frontier.pop(0)
        children = [
            e
            for e in world.events
            if parent in e.causes and e.id not in seen
        ]
        children.sort(key=lambda e: (e.day, e.id))
        for child in children:
            seen.add(child.id)
            ordered.append(child)
            frontier.append(child.id)
    return ordered


def build_causal_thread(
    world: WorldState,
    event_id: str,
    *,
    max_nodes: int = 12,
) -> list[WorldEvent]:
    """Full thread: walk to root, then include downstream responses."""
    backward = walk_causes_backward(world, event_id)
    if not backward:
        return []
    root = backward[0]
    thread = collect_descendants(world, root.id, max_nodes=max_nodes)
    if not thread:
        return backward
    return thread[:max_nodes]


def format_thread_line(world: WorldState, event: WorldEvent) -> str:
    phase = event.effects.get("phase")
    prefix = ""
    if phase == "response":
        prefix = "↳ "
    elif event.causes:
        prefix = "↳ "
    actor = world.characters.get(event.actor_id or "")
    target = world.characters.get(event.target_id or "")
    names = event.summary or ""
    if not names and actor and target:
        names = f"{actor.name} → {target.name}"
    return f"{prefix}Day {event.day}: {names}"


def recent_story_threads(
    world: WorldState,
    *,
    limit: int = 5,
    min_length: int = 2,
) -> list[list[WorldEvent]]:
    """Threads worth showing: at least min_length linked CUSTOM/social events."""
    index = event_by_id(world)
    candidates: list[WorldEvent] = [
        e
        for e in reversed(world.events)
        if e.kind.value == "custom" and (e.causes or _has_child(e.id, world))
    ]
    threads: list[list[WorldEvent]] = []
    used_roots: set[str] = set()

    for event in candidates:
        chain = walk_causes_backward(world, event.id)
        if not chain:
            continue
        root_id = chain[0].id
        if root_id in used_roots:
            continue
        full = build_causal_thread(world, event.id)
        if len(full) < min_length:
            continue
        used_roots.add(root_id)
        threads.append(full)
        if len(threads) >= limit:
            break
    return threads


def _has_child(event_id: str, world: WorldState) -> bool:
    return any(event_id in e.causes for e in world.events)
