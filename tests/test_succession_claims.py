from chronicle.generation.realm import generate_world
from chronicle.simulation.engine import SimulationEngine
from chronicle.simulation.invariants import validate_world
from chronicle.simulation.succession import had_childless_succession


def test_long_run_may_create_claims_without_violations() -> None:
    world = generate_world(seed=7, population_target=200)
    SimulationEngine(world).advance_days(365 * 40)
    violations = validate_world(world)
    assert violations == []
    # Claims are optional but structurally valid when present
    for claim in world.claims.values():
        assert claim.character_id in world.characters
        assert claim.title_id in world.titles


def test_had_childless_succession_detects_no_living_children() -> None:
    world = generate_world(seed=1, population_target=120)
    parent_id = next(
        pid
        for c in world.living_characters()
        for pid in c.parent_ids
        if pid in world.characters
    )
    assert had_childless_succession(world, parent_id) is False
