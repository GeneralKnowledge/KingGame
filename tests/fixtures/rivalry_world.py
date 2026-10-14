from __future__ import annotations

from chronicle.character_ai.traits import CORE_TRAITS, normalize_core_traits
from chronicle.models.character import Character, Goal, MaritalStatus, Sex
from chronicle.models.house import House
from chronicle.models.world import Realm, WorldState


def _core_traits(**overrides: float) -> dict[str, float]:
    base = {k: 0.5 for k in CORE_TRAITS}
    base.update(overrides)
    return normalize_core_traits(base)


def build_rivalry_world(seed: int = 42) -> WorldState:
    """Minimal 4-character, 2-house graph for agency integration tests."""
    world = WorldState(
        seed=seed,
        day=0,
        next_entity_id=100,
        realm=Realm(id="realm_test", name="Test Vale", county_title_id="title_county"),
    )
    world.houses["house_red"] = House(
        id="house_red",
        name="House Red",
        head_character_id="char_alice",
        prestige=55.0,
    )
    world.houses["house_blue"] = House(
        id="house_blue",
        name="House Blue",
        head_character_id="char_bob",
        prestige=50.0,
    )
    chars = [
        Character(
            id="char_alice",
            name="Alice Red",
            age_years=28,
            sex=Sex.FEMALE,
            house_id="house_red",
            role="noble",
            traits=_core_traits(vengefulness=0.85, ambition=0.7),
            goals=[
                Goal(kind="settle_score", priority=0.85, target_id="char_bob"),
            ],
        ),
        Character(
            id="char_bob",
            name="Bob Blue",
            age_years=30,
            sex=Sex.MALE,
            house_id="house_blue",
            role="noble",
            traits=_core_traits(),
        ),
        Character(
            id="char_cara",
            name="Cara Red",
            age_years=26,
            sex=Sex.FEMALE,
            house_id="house_red",
            role="courtier",
            traits=_core_traits(sociability=0.8),
            marital_status=MaritalStatus.SINGLE,
        ),
        Character(
            id="char_dan",
            name="Dan Blue",
            age_years=24,
            sex=Sex.MALE,
            house_id="house_blue",
            role="knight",
            traits=_core_traits(),
        ),
    ]
    for char in chars:
        world.characters[char.id] = char

    rel = world.get_relationship("char_alice", "char_bob")
    rel.resentment = 62.0
    rel.envy = 20.0
    world.relationships[world.relationship_key("char_alice", "char_bob")] = rel
    return world
