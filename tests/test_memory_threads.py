from chronicle.character_ai.utility import ActionKind, score_action
from chronicle.events.resolver import resolve_social_action
from chronicle.history.threads import build_causal_thread, recent_story_threads
from tests.fixtures.rivalry_world import build_rivalry_world, _core_traits


def test_insult_creates_target_memory_linked_to_event() -> None:
    world = build_rivalry_world()
    world.day = 6
    resolve_social_action(
        world,
        "char_alice",
        ActionKind.PUBLIC_INSULT,
        "char_bob",
        motive_snapshot={},
    )
    bob = world.characters["char_bob"]
    assert bob.memories
    mem = bob.memories[-1]
    assert mem.actor_id == "char_alice"
    assert mem.source_event_id
    assert "humiliation" in mem.emotional_tags
    assert world.events[0].effects.get("memory_ids")


def test_memory_increases_insult_utility_against_offender() -> None:
    world = build_rivalry_world()
    world.day = 6
    resolve_social_action(
        world,
        "char_alice",
        ActionKind.PUBLIC_INSULT,
        "char_bob",
        motive_snapshot={},
    )
    bob = world.characters["char_bob"]
    bob.traits = _core_traits(vengefulness=0.5)
    before = score_action(world, bob, ActionKind.PUBLIC_INSULT, "char_alice")
    bob.memories.clear()
    after = score_action(world, bob, ActionKind.PUBLIC_INSULT, "char_alice")
    assert before > after


def test_causal_thread_links_response_to_initiative() -> None:
    world = build_rivalry_world()
    world.day = 6
    world.characters["char_bob"].traits = _core_traits(vengefulness=0.95)
    resolve_social_action(
        world,
        "char_alice",
        ActionKind.PUBLIC_INSULT,
        "char_bob",
        motive_snapshot={},
    )
    assert len(world.events) >= 2
    leaf = world.events[-1]
    thread = build_causal_thread(world, leaf.id)
    assert len(thread) >= 2
    assert thread[0].effects.get("phase") == "initiative"
    assert thread[-1].effects.get("phase") == "response"
    assert thread[-1].causes == [thread[0].id]
    threads = recent_story_threads(world, limit=3, min_length=2)
    assert threads
