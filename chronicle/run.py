from __future__ import annotations

import argparse
import sys

from chronicle.generation.realm import generate_world
from chronicle.simulation.demography_stats import analyze_demography
from chronicle.simulation.engine import SimulationEngine
from chronicle.simulation.invariants import validate_world


def _parse_seeds(spec: str) -> list[int]:
    if "-" in spec:
        start_s, end_s = spec.split("-", 1)
        return list(range(int(start_s), int(end_s) + 1))
    return [int(s) for s in spec.split(",") if s.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run KingGame simulation batches")
    parser.add_argument("--seeds", default="0-9", help="Seed or range, e.g. 0-9")
    parser.add_argument("--years", type=int, default=100)
    parser.add_argument("--population", type=int, default=200)
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print demography diagnosis (births, deaths, marriage, mortality shares)",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for seed in _parse_seeds(args.seeds):
        world = generate_world(seed=seed, population_target=args.population)
        engine = SimulationEngine(world)
        engine.advance_days(args.years * 365)
        violations = validate_world(world)
        living = len(world.living_characters())
        if args.stats:
            print(analyze_demography(world).format_text())
            print()
        print(f"seed={seed} day={world.day} living={living} violations={len(violations)}")
        for v in violations[:5]:
            print(f"  {v.code}: {v.message}")
        if violations:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
