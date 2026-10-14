from __future__ import annotations

from chronicle.models.world import WorldState
from chronicle.simulation import lifecycle
from chronicle.world.rng import derive_rng


class SimulationEngine:
    """Fixed-seed tick loop. UI and persistence stay outside this module."""

    def __init__(self, world: WorldState) -> None:
        self.world = world

    def tick(self) -> None:
        world = self.world
        seed, day = world.seed, world.day
        world.day += 1
        day = world.day

        lifecycle.age_characters(world)
        lifecycle.process_deaths(
            world, derive_rng(seed, day, "lifecycle.death")
        )
        lifecycle.process_marriages(
            world, derive_rng(seed, day, "lifecycle.marriage")
        )
        lifecycle.process_births(
            world, derive_rng(seed, day, "lifecycle.birth")
        )

    def advance_days(self, days: int) -> None:
        for _ in range(days):
            self.tick()
