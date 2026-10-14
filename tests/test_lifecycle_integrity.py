import pytest

from chronicle.generation.realm import generate_world
from chronicle.simulation.engine import SimulationEngine
from chronicle.simulation.invariants import validate_world


@pytest.mark.parametrize("seed", list(range(10)))
def test_hundred_year_runs_satisfy_invariants(seed: int) -> None:
    world = generate_world(seed=seed, population_target=200)
    SimulationEngine(world).advance_days(365 * 100)
    violations = validate_world(world)
    assert violations == [], (
        f"seed={seed} violations: "
        + ", ".join(f"{v.code}: {v.message}" for v in violations[:5])
    )
