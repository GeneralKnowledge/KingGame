from chronicle.generation.realm import generate_world
from chronicle.simulation.engine import SimulationEngine


def test_generate_world_population_in_range():
    world = generate_world(seed=7, population_target=200)
    assert 150 <= len(world.characters) <= 260
    assert len(world.houses) == 8
    assert sum(1 for t in world.titles.values() if t.kind.value == "lordship") == 3


def test_simulation_is_deterministic_for_fixed_seed():
    w1 = generate_world(seed=99, population_target=180)
    w2 = generate_world(seed=99, population_target=180)
    e1 = SimulationEngine(w1)
    e2 = SimulationEngine(w2)
    e1.advance_days(500)
    e2.advance_days(500)
    assert w1.day == w2.day
    assert len(w1.events) == len(w2.events)
    assert w1.events[-1].kind == w2.events[-1].kind


def test_long_run_produces_lifecycle_events():
    world = generate_world(seed=123, population_target=200)
    engine = SimulationEngine(world)
    engine.advance_days(365 * 30)
    kinds = {e.kind.value for e in world.events}
    assert "birth" in kinds
    assert "death" in kinds
    assert world.day == 365 * 30


def test_random_character_has_family_context():
    world = generate_world(seed=1, population_target=200)
    engine = SimulationEngine(world)
    engine.advance_days(365 * 10)
    sample = next(iter(world.living_characters()))
    has_relationship_or_kin = bool(sample.parent_ids or sample.spouse_id or sample.house_id)
    assert has_relationship_or_kin
