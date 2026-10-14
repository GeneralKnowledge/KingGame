from chronicle.character_ai import goals as goal_logic
from chronicle.character_ai.goals import MAX_ACTIVE_GOALS, RESENTMENT_SETTLE_THRESHOLD
from chronicle.models.character import Goal
from tests.fixtures.rivalry_world import build_rivalry_world


def test_refresh_adds_settle_score_when_resentment_high() -> None:
    world = build_rivalry_world()
    alice = world.characters["char_alice"]
    alice.goals.clear()
    goal_logic.refresh_goals(world, alice, day=7)
    kinds = {g.kind for g in alice.goals}
    assert "settle_score" in kinds
    assert any(g.target_id == "char_bob" for g in alice.goals)


def test_prune_removes_goal_when_target_dead() -> None:
    world = build_rivalry_world()
    alice = world.characters["char_alice"]
    alice.goals = [Goal(kind="settle_score", priority=0.7, target_id="char_bob")]
    world.characters["char_bob"].alive = False
    goal_logic.prune_obsolete_goals(world, alice)
    assert not any(g.kind == "settle_score" for g in alice.goals)


def test_goal_cap_enforced_on_prune() -> None:
    world = build_rivalry_world()
    alice = world.characters["char_alice"]
    alice.goals = [
        Goal(kind="wait", priority=0.5, target_id=None)
        for _ in range(MAX_ACTIVE_GOALS + 3)
    ]
    goal_logic.prune_obsolete_goals(world, alice)
    assert len(alice.goals) <= MAX_ACTIVE_GOALS


def test_resentment_threshold_constant_matches_fixture() -> None:
    world = build_rivalry_world()
    rel = world.get_relationship("char_alice", "char_bob")
    assert rel.resentment >= RESENTMENT_SETTLE_THRESHOLD - 10
