from chronicle.character_ai.traits import (
    CORE_TRAITS,
    derived_highlights,
    migrate_legacy_traits,
    trait_bias,
)


def test_migrate_legacy_eleven_to_eight_cores() -> None:
    legacy = {k: 0.5 for k in (
        "courageous", "cautious", "ambitious", "compassionate", "jealous",
        "honest", "deceitful", "patient", "impulsive", "proud", "sociable",
    )}
    legacy["ambitious"] = 0.9
    legacy["sociable"] = 0.8
    cores = migrate_legacy_traits(legacy)
    assert set(cores.keys()) == set(CORE_TRAITS)
    assert cores["ambition"] == 0.9
    assert cores["sociability"] == 0.8


def test_derived_highlights_returns_readable_subset() -> None:
    traits = migrate_legacy_traits({"ambitious": 0.95, "sociable": 0.2})
    labels = derived_highlights(traits, limit=3)
    assert "Ambitious" in labels
    assert len(labels) <= 3


def test_trait_bias_bounded() -> None:
    traits = migrate_legacy_traits({"sociable": 0.95, "proud": 0.95})
    bias = trait_bias("marriage_accept", traits)
    assert -0.3 <= bias <= 0.3
