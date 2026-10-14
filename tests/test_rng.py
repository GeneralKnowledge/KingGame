from chronicle.world.rng import derive_rng


def test_additive_seed_day_collision_is_resolved():
    """(seed=5, day=10) and (seed=10, day=5) must not share the same stream."""
    a = derive_rng(5, 10, "lifecycle.death")
    b = derive_rng(10, 5, "lifecycle.death")
    assert a.random() != b.random()


def test_derive_rng_is_reproducible():
    a = derive_rng(42, 100, "lifecycle.marriage")
    b = derive_rng(42, 100, "lifecycle.marriage")
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]


def test_different_modules_differ_on_same_day():
    death = derive_rng(1, 50, "lifecycle.death")
    marriage = derive_rng(1, 50, "lifecycle.marriage")
    assert death.random() != marriage.random()
