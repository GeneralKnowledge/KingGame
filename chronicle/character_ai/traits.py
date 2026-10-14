from __future__ import annotations

from typing import Literal

CORE_TRAITS: tuple[str, ...] = (
    "ambition",
    "courage",
    "compassion",
    "honesty",
    "pride",
    "patience",
    "sociability",
    "vengefulness",
)

LegacyTraitKey = Literal[
    "courageous",
    "cautious",
    "ambitious",
    "compassionate",
    "jealous",
    "honest",
    "deceitful",
    "patient",
    "impulsive",
    "proud",
    "sociable",
]

HIGHLIGHT_RULES: tuple[tuple[str, str, float], ...] = (
    ("ambition", "Ambitious", 0.72),
    ("ambition", "Content", 0.28),
    ("courage", "Bold", 0.72),
    ("courage", "Timid", 0.28),
    ("compassion", "Kind", 0.72),
    ("compassion", "Hard-hearted", 0.28),
    ("honesty", "Honorable", 0.72),
    ("honesty", "Deceitful", 0.28),
    ("pride", "Proud", 0.72),
    ("patience", "Patient", 0.72),
    ("patience", "Impulsive", 0.28),
    ("sociability", "Gregarious", 0.72),
    ("sociability", "Withdrawn", 0.28),
    ("vengefulness", "Vengeful", 0.72),
    ("vengefulness", "Forgiving", 0.28),
)

ACTION_BIAS_WEIGHTS: dict[str, dict[str, float]] = {
    "marriage_accept": {
        "sociability": 0.35,
        "pride": -0.15,
        "compassion": 0.1,
    },
    "scheme_claim": {
        "ambition": 0.4,
        "vengefulness": 0.25,
        "honesty": -0.1,
    },
    "reconcile": {
        "compassion": 0.35,
        "patience": 0.2,
        "vengefulness": -0.3,
    },
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _legacy_get(traits: dict[str, float], key: str, default: float = 0.5) -> float:
    return float(traits.get(key, default))


def migrate_legacy_traits(traits: dict[str, float]) -> dict[str, float]:
    """Map prototype 11-trait dict to 8 core dimensions (DECISIONS D4)."""
    if traits and all(k in traits for k in CORE_TRAITS):
        return {k: _clamp(float(traits[k])) for k in CORE_TRAITS}

    courageous = _legacy_get(traits, "courageous")
    cautious = _legacy_get(traits, "cautious")
    honest = _legacy_get(traits, "honest")
    deceitful = _legacy_get(traits, "deceitful")
    patient = _legacy_get(traits, "patient")
    impulsive = _legacy_get(traits, "impulsive")

    return {
        "ambition": _clamp(_legacy_get(traits, "ambitious")),
        "courage": _clamp((courageous + (1.0 - cautious)) / 2.0),
        "compassion": _clamp(_legacy_get(traits, "compassionate")),
        "honesty": _clamp((honest + (1.0 - deceitful)) / 2.0),
        "pride": _clamp(_legacy_get(traits, "proud")),
        "patience": _clamp((patient + (1.0 - impulsive)) / 2.0),
        "sociability": _clamp(_legacy_get(traits, "sociable")),
        "vengefulness": _clamp(
            (_legacy_get(traits, "jealous") + impulsive * 0.25) / 1.25
        ),
    }


def normalize_core_traits(traits: dict[str, float]) -> dict[str, float]:
    migrated = migrate_legacy_traits(traits)
    return {name: _clamp(migrated.get(name, 0.5)) for name in CORE_TRAITS}


def core_trait(traits: dict[str, float], name: str) -> float:
    return normalize_core_traits(traits).get(name, 0.5)


def derived_highlights(traits: dict[str, float], *, limit: int = 4) -> list[str]:
    cores = normalize_core_traits(traits)
    labels: list[tuple[float, str]] = []
    for dim, label, threshold in HIGHLIGHT_RULES:
        value = cores[dim]
        if label in ("Content", "Timid", "Hard-hearted", "Deceitful", "Impulsive", "Withdrawn", "Forgiving"):
            if value <= threshold:
                labels.append((threshold - value, label))
        elif value >= threshold:
            labels.append((value, label))
    labels.sort(key=lambda x: -x[0])
    seen: set[str] = set()
    out: list[str] = []
    for _, label in labels:
        if label in seen:
            continue
        seen.add(label)
        out.append(label)
        if len(out) >= limit:
            break
    return out


def trait_bias(action: str, traits: dict[str, float]) -> float:
    """Utility modifier in roughly [-0.3, +0.3] for staged actions."""
    weights = ACTION_BIAS_WEIGHTS.get(action)
    if not weights:
        return 0.0
    cores = normalize_core_traits(traits)
    total = 0.0
    for dim, weight in weights.items():
        total += (cores[dim] - 0.5) * weight
    return max(-0.3, min(0.3, total))
