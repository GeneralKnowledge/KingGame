from chronicle.generation.realm import generate_world
from chronicle.simulation.engine import SimulationEngine


def _population_series(seed: int, years: int = 100) -> list[int]:
    world = generate_world(seed=seed, population_target=200)
    engine = SimulationEngine(world)
    series: list[int] = []
    for year in range(years + 1):
        series.append(len(world.living_characters()))
        if year < years:
            engine.advance_days(365)
    return series


def test_population_health_loose_bounds_seeds_0_to_9() -> None:
    """Detect collapse or numeric runaway without tuning birth/death rates in A2."""
    for seed in range(10):
        series = _population_series(seed)
        final = series[-1]
        assert min(series) >= 5, f"seed {seed} population collapsed"
        assert final <= 1_000_000, f"seed {seed} final population {final} exceeds sanity cap"
        assert max(series) <= 2_000_000, f"seed {seed} peak population too high"


# Population findings (seeds 0-9, 100 years, target ~200):
# | seed | final living (approx) |
# | 0 | 181157 | 1 | 180989 | 2 | 219448 | 3 | 202175 | 4 | 193904 |
# | 5 | 205427 | 6 | 182745 | 7 | 203679 | 8 | 211236 | 9 | 217523 |
# Outcome: **strong ballooning** (not tuned in A2); no extinction; invariants still clean.
