from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DemographyConfig:
    """Single source of truth for A2b population regulation parameters."""

    # --- Fertility (monthly probability scale) ---
    fertility_peak_monthly: float = 0.14
    fertility_peak_age: int = 26
    fertility_min_age: int = 18
    fertility_max_age: int = 42
    fertility_age_sigma: float = 7.0
    min_birth_spacing_days: int = 540  # ~18 months
    full_birth_spacing_days: int = 900  # ~30 months until spacing penalty fully gone

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

    def monthly_fertility_probability(
        self,
        age_years: int,
        days_since_last_birth: int | None,
    ) -> float:
        age_f = self.fertility_age_factor(age_years)
        if age_f <= 0:
            return 0.0
        spacing = self.birth_spacing_factor(days_since_last_birth)
        return self.fertility_peak_monthly * age_f * spacing


DEMOGRAPHY = DemographyConfig()
