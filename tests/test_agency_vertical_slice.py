from chronicle.character_ai.utility import ActionKind
from chronicle.models.events import EventKind
from chronicle.simulation.agency import is_agency_day_for, process_daily_agency
from chronicle.simulation.engine import SimulationEngine
from chronicle.simulation.invariants import validate_world
from chronicle.world.rng import derive_rng
from chronicle.events.resolver import resolve_social_action
from tests.fixtures.rivalry_world import build_rivalry_world, _core_traits


def _first_agency_day(world, char_id: str, start: int = 1) -> int:
    for day in range(start, start + 14):
        world.day = day
        if is_agency_day_for(world, char_id):
            return day
    raise AssertionError("no agency day found")


def test_insult_loop_produces_event_and_relationship_delta() -> None:
    world = build_rivalry_world()
    actor_id = "char_alice"
    target_id = "char_bob"
    world.characters["char_cara"].role = "peasant"
    world.characters["char_dan"].role = "peasant"
    day = _first_agency_day(world, actor_id)
    before = world.get_relationship(target_id, actor_id).resentment

    process_daily_agency(world, derive_rng(world.seed, day, "agency"))

    insult_events = [
        e
        for e in world.events
        if e.kind == EventKind.CUSTOM
        and e.effects.get("action") == ActionKind.PUBLIC_INSULT.value
        and e.actor_id == actor_id
        and e.target_id == target_id
    ]
    assert insult_events, "expected a public insult event from agency pass"
    event = insult_events[0]
    assert event.effects.get("motive_snapshot")
    deltas = event.effects.get("relationship_deltas", {})
    assert deltas.get("target_to_actor", {}).get("resentment", 0) > 0
    after = world.get_relationship(target_id, actor_id).resentment
    assert after > before
    bob = world.characters[target_id]
    assert any(m.actor_id == actor_id and "humiliation" in m.emotional_tags for m in bob.memories)
    assert not validate_world(world)


def test_agency_fixture_deterministic_same_seed() -> None:
    w1 = build_rivalry_world(seed=99)
    w2 = build_rivalry_world(seed=99)
    day = _first_agency_day(w1, "char_alice")
    w2.day = day
    process_daily_agency(w1, derive_rng(99, day, "agency"))
    process_daily_agency(w2, derive_rng(99, day, "agency"))
    assert len(w1.events) == len(w2.events)
    if w1.events:
        assert w1.events[-1].effects == w2.events[-1].effects


def test_engine_tick_includes_agency_without_invariants() -> None:
    world = build_rivalry_world()
    engine = SimulationEngine(world)
    engine.advance_days(14)
    custom = [e for e in world.events if e.kind == EventKind.CUSTOM]
    assert custom or world.day == 14
    assert not validate_world(world)


def test_target_responds_to_insult_with_event_id_cause() -> None:
    world = build_rivalry_world()
    world.day = 6
    world.characters["char_bob"].traits = _core_traits(vengefulness=0.95)
    resolve_social_action(
        world,
        "char_alice",
        ActionKind.PUBLIC_INSULT,
        "char_bob",
        motive_snapshot={"public_insult:char_bob": 1.0},
    )
    initiative = [e for e in world.events if e.effects.get("phase") == "initiative"]
    response = [e for e in world.events if e.effects.get("phase") == "response"]
    assert len(initiative) == 1
    assert len(response) == 1
    assert response[0].actor_id == "char_bob"
    assert response[0].target_id == "char_alice"
    assert response[0].causes == [initiative[0].id]
    assert response[0].effects.get("motive_snapshot")


def test_motive_snapshot_affects_next_score() -> None:
    world = build_rivalry_world()
    actor = world.characters["char_alice"]
    from chronicle.character_ai.utility import score_action

    score_before = score_action(world, actor, ActionKind.PUBLIC_INSULT, "char_bob")
    rel = world.get_relationship("char_alice", "char_bob")
    rel.resentment = min(100.0, rel.resentment + 12.0)
    score_after = score_action(world, actor, ActionKind.PUBLIC_INSULT, "char_bob")
    assert score_after > score_before
