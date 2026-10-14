from pathlib import Path

from chronicle.generation.realm import generate_world
from chronicle.persistence.sqlite_store import load_world, save_world
from chronicle.simulation.engine import SimulationEngine


def _collect_all_ids(world) -> list[str]:
    ids: list[str] = []
    ids.extend(world.characters.keys())
    ids.extend(world.houses.keys())
    ids.extend(world.titles.keys())
    ids.extend(e.id for e in world.events)
    ids.append(world.realm.id)
    return ids


def test_ids_unique_across_save_load_and_continue(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    world = generate_world(seed=7, population_target=180)
    engine = SimulationEngine(world)
    engine.advance_days(100)

    save_world(world, db_path)
    loaded = load_world(db_path)
    assert loaded is not None

    engine2 = SimulationEngine(loaded)
    engine2.advance_days(100)

    all_ids = _collect_all_ids(loaded)
    assert len(all_ids) == len(set(all_ids))
    assert loaded.next_entity_id > 1
