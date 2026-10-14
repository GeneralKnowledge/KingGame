from chronicle.simulation.demography_config import DemographyConfig


def test_fertility_age_curve_peaks_mid_twenties_and_has_bounds() -> None:
    cfg = DemographyConfig()
    assert cfg.fertility_age_factor(17) == 0.0
    assert cfg.fertility_age_factor(43) == 0.0
    peak = cfg.fertility_age_factor(cfg.fertility_peak_age)
    assert cfg.fertility_age_factor(20) < peak
    assert cfg.fertility_age_factor(35) < peak
    assert cfg.fertility_age_factor(40) < cfg.fertility_age_factor(28)


def test_birth_spacing_monotonic_and_enforces_minimum() -> None:
    cfg = DemographyConfig()
    assert cfg.birth_spacing_factor(None) == 1.0
    assert cfg.birth_spacing_factor(cfg.min_birth_spacing_days - 1) == 0.0
    mid = (cfg.min_birth_spacing_days + cfg.full_birth_spacing_days) // 2
    assert 0.0 < cfg.birth_spacing_factor(mid) < 1.0
    assert cfg.birth_spacing_factor(cfg.full_birth_spacing_days) == 1.0
    assert cfg.birth_spacing_factor(cfg.full_birth_spacing_days + 100) == 1.0


def test_mortality_increases_with_age_and_childbirth_risk() -> None:
    cfg = DemographyConfig()
    child = cfg.daily_death_probability(3)
    adult = cfg.daily_death_probability(30)
    elder = cfg.daily_death_probability(80)
    assert child > adult
    assert elder > adult
    birth_risk = cfg.daily_death_probability(28, childbirth_day=True)
    assert birth_risk > cfg.daily_death_probability(28)


def test_population_pressure_smooth_and_zero_below_capacity() -> None:
    cfg = DemographyConfig()
    cap = cfg.realm_carrying_capacity
    assert cfg.population_pressure(cap) == 0.0
    assert cfg.population_pressure(cap - 1) == 0.0
    p1 = cfg.population_pressure(cap + 50)
    p2 = cfg.population_pressure(cap + 150)
    assert 0.0 < p1 < p2 < 1.0
    assert cfg.mortality_density_multiplier(p2) > cfg.mortality_density_multiplier(p1)
    assert cfg.fertility_density_multiplier(p2) < cfg.fertility_density_multiplier(p1)
