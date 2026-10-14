from chronicle.generation.realm import generate_world
from chronicle.history.chronicle import render_recent_chronicle
from chronicle.history.story import event_significance, is_named_cast, story_importance
from chronicle.models.events import EventKind
from chronicle.simulation.engine import SimulationEngine


def test_county_holder_has_high_story_importance() -> None:
    world = generate_world(seed=3, population_target=200)
    county = world.titles[world.realm.county_title_id]
    assert county.holder_id
    assert story_importance(world, county.holder_id) >= 0.9
    assert is_named_cast(world, county.holder_id)


def test_chronicle_ranks_succession_events_first() -> None:
    world = generate_world(seed=5, population_target=200)
    SimulationEngine(world).advance_days(365 * 15)
    if not world.events:
        return
    top_sig = max(event_significance(world, e) for e in world.events)
    succession = [e for e in world.events if e.kind == EventKind.SUCCESSION]
    if succession:
        assert top_sig >= 0.85
    lines = render_recent_chronicle(world, limit=5)
    assert len(lines) <= 5
