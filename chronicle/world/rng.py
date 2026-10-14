from __future__ import annotations

import random


def derive_rng(seed: int, day: int, module: str) -> random.Random:
    """Deterministic RNG stream for one simulation module on one day."""
    return random.Random(f"{seed}:{day}:{module}")
