from __future__ import annotations

import random

from chronicle.models.world import WorldState
from chronicle.simulation import lifecycle


class SimulationEngine:
    """Fixed-seed tick loop. UI and persistence stay outside this module."""

    def __init__(self, world: WorldState) -> None:
        self.world = world
        self._rng = random.Random(world.seed + world.day)

    def _refresh_rng(self) -> None:
        self._rng = random.Random(self.world.seed + self.world.day)

    def tick(self) -> None:
        self._refresh_rng()
        self.world.day += 1
        lifecycle.age_characters(self.world, self._rng)
        lifecycle.process_deaths(self.world, self._rng)
        lifecycle.process_marriages(self.world, self._rng)
        lifecycle.process_births(self.world, self._rng)

    def advance_days(self, days: int) -> None:
        for _ in range(days):
            self.tick()
