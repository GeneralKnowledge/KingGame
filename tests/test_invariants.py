import copy

import pytest
from hypothesis import given, strategies as st

from chronicle.generation.realm import generate_world
from chronicle.models.character import MaritalStatus
from chronicle.simulation.invariants import validate_world


def test_fresh_world_has_no_duplicate_ids():
    world = generate_world(seed=3, population_target=150)
    codes = [v.code for v in validate_world(world)]
    assert "duplicate_id" not in codes


@pytest.mark.parametrize(
    "mutator,expected_code",
    [
        (
            lambda w: setattr(
                w.characters[next(iter(w.characters))], "spouse_id", "char_missing"
            ),
            "spouse_missing",
        ),
        (
            lambda w: (
                setattr(w.characters[cid := next(iter(w.characters))], "spouse_id", None),
                setattr(w.characters[cid], "marital_status", MaritalStatus.MARRIED),
            ),
            "married_without_spouse",
        ),
        (
            lambda w: setattr(w.titles[next(iter(w.titles))], "holder_id", None),
            "title_holder_missing",
        ),
    ],
)
def test_invariants_flag_corrupted_world(mutator, expected_code):
    world = generate_world(seed=1, population_target=80)
    mutator(world)
    codes = {v.code for v in validate_world(world)}
    assert expected_code in codes


@given(st.integers(min_value=0, max_value=50))
def test_asymmetric_spouse_detected(seed_offset: int):
    world = generate_world(seed=10 + seed_offset, population_target=60)
    ids = list(world.characters.keys())
    if len(ids) < 2:
        return
    a, b = ids[0], ids[1]
    world.characters[a].spouse_id = b
    world.characters[a].marital_status = MaritalStatus.MARRIED
    world.characters[b].spouse_id = None
    codes = {v.code for v in validate_world(world)}
    assert "spouse_asymmetric" in codes


def test_ancestor_cycle_detected():
    world = generate_world(seed=2, population_target=40)
    ids = list(world.characters.keys())[:3]
    if len(ids) < 3:
        pytest.skip("need at least 3 characters")
    a, b, c = ids
    world.characters[a].parent_ids = (c,)
    world.characters[b].parent_ids = (a,)
    world.characters[c].parent_ids = (b,)
    codes = {v.code for v in validate_world(copy.deepcopy(world))}
    assert "ancestor_cycle" in codes
