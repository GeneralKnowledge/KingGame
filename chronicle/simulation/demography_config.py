from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DemographyConfig:
    """Single source of truth for A2b population regulation parameters."""

    # --- Fertility (monthly probability scale) ---
    fertility_peak_monthly: float = 0.082
    fertility_peak_age: int = 26
    fertility_min_age: int = 18
    fertility_max_age: int = 42
    fertility_age_sigma: float = 7.0
    min_birth_spacing_days: int = 540  # ~18 months
    full_birth_spacing_days: int = 900  # ~30 months until spacing penalty fully gone

    # --- Mortality (daily probabilities) ---
    adult_death_floor: float = 0.00003
    adult_death_age_scale: float = 0.0000012
    infant_daily_year0: float = 0.00092
    infant_daily_year1: float = 0.00024
    child_daily_under5: float = 0.000062
    childbirth_extra_daily: float = 0.012

    # --- Soft carrying capacity (whole county) ---
    realm_carrying_capacity: int = 212
    pressure_mortality_strength: float = 1.22
    pressure_fertility_strength: float = 0.82
    pressure_marriage_strength: float = 0.58

    def fertility_age_factor(self, age_years: int) -> float:
        if age_years < self.fertility_min_age or age_years > self.fertility_max_age:
            return 0.0
        z = (age_years - self.fertility_peak_age) / self.fertility_age_sigma
        return math.exp(-0.5 * z * z)

    def birth_spacing_factor(self, days_since_last_birth: int | None) -> float:
        if days_since_last_birth is None:
            return 1.0
        if days_since_last_birth < self.min_birth_spacing_days:
            return 0.0
        if days_since_last_birth >= self.full_birth_spacing_days:
            return 1.0
        t = (days_since_last_birth - self.min_birth_spacing_days) / (
            self.full_birth_spacing_days - self.min_birth_spacing_days
        )
        return max(0.0, min(1.0, t))

    def population_pressure(self, living_count: int) -> float:
        cap = self.realm_carrying_capacity
        if living_count <= cap:
            return 0.0
        excess = (living_count - cap) / cap
        return excess / (1.0 + excess)

    def fertility_density_multiplier(self, pressure: float) -> float:
        return 1.0 / (1.0 + self.pressure_fertility_strength * pressure)

    def mortality_density_multiplier(self, pressure: float) -> float:
        return 1.0 + self.pressure_mortality_strength * pressure

    def marriage_acceptance_multiplier(self, pressure: float) -> float:
        return 1.0 / (1.0 + self.pressure_marriage_strength * pressure)

    def monthly_fertility_probability(
        self,
        age_years: int,
        days_since_last_birth: int | None,
        population_pressure: float = 0.0,
    ) -> float:
        age_f = self.fertility_age_factor(age_years)
        if age_f <= 0:
            return 0.0
        spacing = self.birth_spacing_factor(days_since_last_birth)
        density = self.fertility_density_multiplier(population_pressure)
        return self.fertility_peak_monthly * age_f * spacing * density

    def daily_death_probability(
        self,
        age_years: int,
        *,
        population_pressure: float = 0.0,
        childbirth_day: bool = False,
    ) -> float:
        if age_years == 0:
            p = self.infant_daily_year0
        elif age_years == 1:
            p = self.infant_daily_year1
        elif age_years < 5:
            p = self.child_daily_under5
        else:
            p = self.adult_death_floor
            if age_years > 25:
                p += (age_years - 25) * self.adult_death_age_scale
            if age_years >= 70:
                p += 0.004
            if age_years >= 85:
                p += 0.008
        if childbirth_day:
            p += self.childbirth_extra_daily
        p *= self.mortality_density_multiplier(population_pressure)
        return min(0.5, max(0.0, p))


DEMOGRAPHY = DemographyConfig()
