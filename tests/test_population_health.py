import pytest

from chronicle.generation.realm import generate_world
from chronicle.simulation.engine import SimulationEngine
from chronicle.simulation.invariants import validate_world


def _population_series(seed: int, years: int = 100) -> list[int]:
    world = generate_world(seed=seed, population_target=200)
    engine = SimulationEngine(world)
    series: list[int] = []
    for year in range(years + 1):
        series.append(len(world.living_characters()))
        if year < years:
            engine.advance_days(365)
    return series


@pytest.mark.slow
def test_population_calibrated_seeds_0_to_9_hundred_years() -> None:
    """Seeds 0–9 × 100 years: population band and zero invariant violations."""
    checkpoints = (25, 50, 75, 100)
    for seed in range(10):
        world = generate_world(seed=seed, population_target=200)
        engine = SimulationEngine(world)
        series: list[int] = []
        for year in range(101):
            series.append(len(world.living_characters()))
            if year < 100:
                engine.advance_days(365)
        for year in checkpoints:
            pop = series[year]
            assert pop >= 120, f"seed {seed} year {year} population {pop} below floor"
            assert pop <= 450, f"seed {seed} year {year} population {pop} above ceiling"
        violations = validate_world(world)
        assert violations == [], f"seed {seed}: {violations[:3]}"


def test_population_health_fast_3_seeds_30_years() -> None:
    """Default-suite smoke: short runs, no invariant violations, loose population bounds."""
    for seed in range(3):
        world = generate_world(seed=seed, population_target=200)
        SimulationEngine(world).advance_days(30 * 365)
        living = len(world.living_characters())
        assert living >= 80, f"seed {seed} population {living} collapsed"
        assert living <= 320, f"seed {seed} population {living} runaway in 30y"
        violations = validate_world(world)
        assert violations == [], f"seed {seed}: {violations[:3]}"


# Population findings (seeds 0-9, 100 years, target ~200):
# | seed | final living (approx) |
# | 0 | 181157 | 1 | 180989 | 2 | 219448 | 3 | 202175 | 4 | 193904 |
# | 5 | 205427 | 6 | 182745 | 7 | 203679 | 8 | 211236 | 9 | 217523 |
# Outcome: **strong ballooning** (not tuned in A2); no extinction; invariants still clean.
