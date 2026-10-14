from __future__ import annotations

import random

from chronicle.history.log import append_event
from chronicle.models.character import Character, MaritalStatus, Sex
from chronicle.models.events import EventKind
from chronicle.models.house import TitleKind
from chronicle.models.world import WorldState
from chronicle.simulation.demography_config import DEMOGRAPHY
from chronicle.world.ids import allocate_id


def age_characters(world: WorldState) -> None:
    if world.day % 365 != 0:
        return
    for char in world.living_characters():
        char.age_years += 1


def _population_pressure(world: WorldState) -> float:
    return DEMOGRAPHY.population_pressure(len(world.living_characters()))


def process_deaths(world: WorldState, rng: random.Random) -> None:
    pressure = _population_pressure(world)
    for char in list(world.living_characters()):
        if rng.random() < DEMOGRAPHY.daily_death_probability(
            char.age_years, population_pressure=pressure
        ):
            _apply_death(world, char)


def _apply_death(world: WorldState, char: Character) -> None:
    char.alive = False
    char.death_day = world.day
    char.marital_status = MaritalStatus.WIDOWED

    if char.spouse_id:
        spouse = world.characters.get(char.spouse_id)
        if spouse and spouse.alive:
            spouse.marital_status = MaritalStatus.WIDOWED
            spouse.spouse_id = None
        char.spouse_id = None

    append_event(
        world,
        day=world.day,
        kind=EventKind.DEATH,
        actor_id=char.id,
        effects={"age": char.age_years},
        summary=f"{char.name} died at age {char.age_years}.",
    )
    resolve_inheritance(world, char.id)


def resolve_inheritance(world: WorldState, deceased_id: str) -> None:
    deceased = world.characters[deceased_id]
    house = world.houses.get(deceased.house_id) if deceased.house_id else None

    was_head = bool(house and house.head_character_id == deceased_id)
    held_titles = any(t.holder_id == deceased_id for t in world.titles.values())

    heir: Character | None = None
    if was_head:
        heir = _pick_house_heir(world, deceased_id, house.id)  # type: ignore[union-attr]

    if heir is None and house and (was_head or held_titles):
        heir = _pick_any_house_member(world, house.id, exclude_id=deceased_id)

    if was_head and heir:
        house.head_character_id = heir.id  # type: ignore[union-attr]

    if heir and (held_titles or was_head):
        _transfer_titles_from_deceased(world, deceased_id, heir.id)
        if was_head:
            append_event(
                world,
                day=world.day,
                kind=EventKind.SUCCESSION,
                actor_id=heir.id,
                causes=[deceased_id],
                effects={"house_id": house.id if house else None},
                summary=f"{heir.name} succeeded {deceased.name} as head of {house.name}.",  # type: ignore[union-attr]
            )
    elif was_head and heir is None:
        house.head_character_id = None  # type: ignore[union-attr]
        append_event(
            world,
            day=world.day,
            kind=EventKind.SUCCESSION,
            actor_id=None,
            causes=[deceased_id],
            effects={"house_id": house.id, "vacant": True},  # type: ignore[union-attr]
            summary=f"{house.name} has no living heir after {deceased.name}'s death.",  # type: ignore[union-attr]
        )

    deceased.title_id = None


def _pick_house_heir(world: WorldState, deceased_id: str, house_id: str) -> Character | None:
    candidates = [
        c
        for c in world.living_characters()
        if c.house_id == house_id and deceased_id in c.parent_ids
    ]
    if not candidates:
        candidates = [
            c
            for c in world.living_characters()
            if c.house_id == house_id and c.role in ("noble", "knight", "courtier")
        ]
    if not candidates:
        return None
    males = [c for c in candidates if c.sex == Sex.MALE]
    pool = males if males else candidates
    return max(pool, key=lambda c: c.age_years)


def _pick_any_house_member(
    world: WorldState, house_id: str, *, exclude_id: str
) -> Character | None:
    members = [
        c
        for c in world.living_characters()
        if c.house_id == house_id and c.id != exclude_id
    ]
    if not members:
        return None
    return max(members, key=lambda c: c.age_years)


def _transfer_titles_from_deceased(
    world: WorldState,
    deceased_id: str,
    heir_id: str,
) -> None:
    heir = world.characters[heir_id]
    for title in world.titles.values():
        if title.holder_id != deceased_id:
            continue
        title.holder_id = heir_id
        if title.kind == TitleKind.HOUSE_HEAD:
            heir.title_id = title.id


def process_births(world: WorldState, rng: random.Random) -> None:
    if world.day % 30 != 0:
        return
    pressure = _population_pressure(world)
    for char in world.living_characters():
        if char.sex != Sex.FEMALE or not char.spouse_id or char.age_years < 18 or char.age_years > 42:
            continue
        spouse = world.characters.get(char.spouse_id)
        if not spouse or not spouse.alive or spouse.age_years < 18:
            continue
        since_last: int | None = None
        if char.last_birth_day is not None:
            since_last = world.day - char.last_birth_day
        prob = DEMOGRAPHY.monthly_fertility_probability(
            char.age_years, since_last, population_pressure=pressure
        )
        if prob <= 0 or rng.random() > prob:
            continue
        child_sex = Sex.MALE if rng.random() < 0.5 else Sex.FEMALE
        child = Character(
            id=allocate_id(world, "char"),
            name=_child_name(rng, child_sex),
            age_years=0,
            sex=child_sex,
            house_id=char.house_id,
            role="courtier",
            parent_ids=(char.id, spouse.id),
            birth_day=world.day,
        )
        world.characters[child.id] = child
        char.last_birth_day = world.day
        append_event(
            world,
            day=world.day,
            kind=EventKind.BIRTH,
            actor_id=char.id,
            target_id=child.id,
            participant_ids=[spouse.id],
            summary=f"{char.name} and {spouse.name} welcomed {child.name}.",
        )
        if rng.random() < DEMOGRAPHY.daily_death_probability(
            char.age_years, population_pressure=pressure, childbirth_day=True
        ):
            _apply_death(world, char)


def _child_name(rng: random.Random, sex: Sex) -> str:
    from chronicle.generation.realm import FIRST_NAMES_F, FIRST_NAMES_M

    pool = FIRST_NAMES_M if sex == Sex.MALE else FIRST_NAMES_F
    return rng.choice(pool)


def process_marriages(world: WorldState, rng: random.Random) -> None:
    if world.day % 14 != 0:
        return
    pressure = _population_pressure(world)
    singles = [c for c in world.living_characters() if c.is_marriageable()]
    rng.shuffle(singles)
    paired: set[str] = set()
    for char in singles:
        if char.id in paired:
            continue
        candidates = [
            c
            for c in singles
            if c.id not in paired
            and c.id != char.id
            and c.sex != char.sex
            and c.house_id != char.house_id
        ]
        if not candidates and char.age_years >= 30:
            candidates = [
                c
                for c in singles
                if c.id not in paired
                and c.id != char.id
                and c.sex != char.sex
                and c.house_id == char.house_id
            ]
        if not candidates:
            continue
        partner = rng.choice(candidates)
        if not _marriage_acceptance(world, rng, char, partner, pressure):
            continue
        char.spouse_id = partner.id
        partner.spouse_id = char.id
        char.marital_status = MaritalStatus.MARRIED
        partner.marital_status = MaritalStatus.MARRIED
        paired.add(char.id)
        paired.add(partner.id)
        append_event(
            world,
            day=world.day,
            kind=EventKind.MARRIAGE,
            actor_id=char.id,
            target_id=partner.id,
            effects={
                "houses": [char.house_id, partner.house_id],
            },
            summary=f"{char.name} of { _house_name(world, char.house_id) } married "
            f"{partner.name} of { _house_name(world, partner.house_id) }.",
        )


def _house_name(world: WorldState, house_id: str | None) -> str:
    if not house_id:
        return "no house"
    return world.houses[house_id].name


def _marriage_acceptance(
    world: WorldState,
    rng: random.Random,
    a: Character,
    b: Character,
    population_pressure: float,
) -> bool:
    """Simple Phase 1 negotiation placeholder — families weigh prestige gap."""
    house_a = world.houses.get(a.house_id or "")
    house_b = world.houses.get(b.house_id or "")
    if not house_a or not house_b:
        return rng.random() < 0.3
    gap = abs(house_a.prestige - house_b.prestige)
    base = 0.55 - gap / 200
    base += (a.traits.get("sociable", 0.5) + b.traits.get("sociable", 0.5)) * 0.1
    base -= (a.traits.get("proud", 0.5) + b.traits.get("proud", 0.5)) * 0.05
    base *= DEMOGRAPHY.marriage_acceptance_multiplier(population_pressure)
    return rng.random() < max(0.15, min(0.9, base))
