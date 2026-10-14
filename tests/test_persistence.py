from pathlib import Path

from chronicle.generation.realm import generate_world
from chronicle.persistence.sqlite_store import load_world, save_world
from chronicle.simulation.engine import SimulationEngine


def _snapshot(world) -> dict:
    return world.model_dump(mode="json")


def test_save_load_round_trip_preserves_state(tmp_path: Path) -> None:
    db_path = tmp_path / "roundtrip.db"
    world = generate_world(seed=11, population_target=160)
    SimulationEngine(world).advance_days(500)
    before = _snapshot(world)

    save_world(world, db_path)
    loaded = load_world(db_path)
    assert loaded is not None
    assert _snapshot(loaded) == before


def test_save_load_continue_matches_uninterrupted_run(tmp_path: Path) -> None:
    db_path = tmp_path / "continue.db"
    total_days = 1000
    midpoint = 500

    uninterrupted = generate_world(seed=22, population_target=160)
    SimulationEngine(uninterrupted).advance_days(total_days)

    with_break = generate_world(seed=22, population_target=160)
    SimulationEngine(with_break).advance_days(midpoint)
    save_world(with_break, db_path)
    loaded = load_world(db_path)
    assert loaded is not None
    SimulationEngine(loaded).advance_days(total_days - midpoint)

    assert loaded.day == uninterrupted.day
    assert loaded.next_entity_id == uninterrupted.next_entity_id
    assert _snapshot(loaded) == _snapshot(uninterrupted)
