from chronicle.generation.realm import generate_world
from chronicle.simulation.demography_stats import analyze_demography
from chronicle.simulation.engine import SimulationEngine


def test_demography_stats_smoke() -> None:
    world = generate_world(seed=0, population_target=200)
    SimulationEngine(world).advance_days(365 * 5)
    report = analyze_demography(world)
    assert report.total_births >= 0
    assert report.living >= 1
    assert "0-4" in report.death_age_counts or report.total_deaths == 0
