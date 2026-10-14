from chronicle.character_ai.traits import CORE_TRAITS, normalize_core_traits
from chronicle.character_ai.utility import ActionKind, score_action
from tests.fixtures.rivalry_world import build_rivalry_world


def _traits(**overrides: float) -> dict[str, float]:
    base = {k: 0.5 for k in CORE_TRAITS}
    base.update(overrides)
    return normalize_core_traits(base)


def test_higher_vengefulness_raises_public_insult_score() -> None:
    world = build_rivalry_world()
    forgiving = world.characters["char_alice"].model_copy(deep=True)
    vengeful = world.characters["char_alice"].model_copy(deep=True)
    forgiving.traits = _traits(vengefulness=0.15)
    vengeful.traits = _traits(vengefulness=0.95)
    target_id = "char_bob"
    low = score_action(world, forgiving, ActionKind.PUBLIC_INSULT, target_id)
    high = score_action(world, vengeful, ActionKind.PUBLIC_INSULT, target_id)
    assert high > low
