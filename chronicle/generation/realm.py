from __future__ import annotations

import random

from chronicle.models.character import DEFAULT_TRAITS, Character, Sex
from chronicle.models.house import House, Title, TitleKind
from chronicle.models.world import Realm, WorldState
from chronicle.world.ids import new_id, reset_id_counter


FIRST_NAMES_M = [
    "Robert",
    "William",
    "Henry",
    "Geoffrey",
    "Hugh",
    "Ralph",
    "Thomas",
    "Edmund",
    "Richard",
    "Alaric",
    "Baldwin",
    "Conrad",
]
FIRST_NAMES_F = [
    "Eleanor",
    "Matilda",
    "Isabel",
    "Margaret",
    "Adelaide",
    "Beatrice",
    "Cecily",
    "Joan",
    "Rosamund",
    "Sybil",
    "Helena",
    "Clara",
]
HOUSE_NAMES = [
    "Ashford",
    "Blackmere",
    "Corwyn",
    "Dunwald",
    "Estmere",
    "Falken",
    "Greymont",
    "Hartwell",
]
LORDSHIP_NAMES = ["Northmarch", "Riverford", "Stonevale"]
COUNTY_NAME = "Haldenmere"


def _random_traits(rng: random.Random) -> dict[str, float]:
    return {trait: rng.uniform(0.15, 0.85) for trait in DEFAULT_TRAITS}


def _pick_name(rng: random.Random, sex: Sex) -> str:
    pool = FIRST_NAMES_M if sex == Sex.MALE else FIRST_NAMES_F
    return rng.choice(pool)


def _create_character(
    rng: random.Random,
    *,
    house_id: str | None,
    role: Character.model_fields["role"].annotation,  # type: ignore[name-defined]
    age: int,
    sex: Sex | None = None,
) -> Character:
    if sex is None:
        sex = Sex.MALE if rng.random() < 0.52 else Sex.FEMALE
    return Character(
        id=new_id("char"),
        name=_pick_name(rng, sex),
        age_years=age,
        sex=sex,
        house_id=house_id,
        role=role,
        traits=_random_traits(rng),
    )


def _seed_kinship(
    rng: random.Random,
    world: WorldState,
    house: House,
    count: int,
) -> list[Character]:
    """Create a noble family tree fragment for one house."""
    members: list[Character] = []
    head_age = rng.randint(38, 58)
    head_sex = Sex.MALE if rng.random() < 0.75 else Sex.FEMALE
    head = _create_character(
        rng, house_id=house.id, role="noble", age=head_age, sex=head_sex
    )
    members.append(head)
    house.head_character_id = head.id

    spouse_sex = Sex.FEMALE if head.sex == Sex.MALE else Sex.MALE
    spouse = _create_character(
        rng, house_id=house.id, role="noble", age=head_age - rng.randint(0, 8), sex=spouse_sex
    )
    head.spouse_id = spouse.id
    spouse.spouse_id = head.id
    members.append(spouse)

    for _ in range(rng.randint(1, 4)):
        child_age = rng.randint(2, min(28, head_age - 18))
        child = _create_character(
            rng,
            house_id=house.id,
            role="noble" if child_age >= 18 else "courtier",
            age=child_age,
        )
        child.parent_ids = (head.id, spouse.id)
        members.extend([child])

    remaining = max(0, count - len(members))
    for _ in range(remaining):
        role = rng.choice(["courtier", "knight", "servant", "clergy"])
        age = rng.randint(16, 55)
        members.append(_create_character(rng, house_id=house.id, role=role, age=age))

    return members


def generate_world(seed: int, population_target: int = 200) -> WorldState:
    reset_id_counter()
    rng = random.Random(seed)

    county_title = Title(
        id=new_id("title"),
        name=COUNTY_NAME,
        kind=TitleKind.COUNTY,
    )
    lordships: list[Title] = []
    for name in LORDSHIP_NAMES:
        lordships.append(
            Title(
                id=new_id("title"),
                name=name,
                kind=TitleKind.LORDSHIP,
                parent_title_id=county_title.id,
            )
        )

    houses: list[House] = []
    for i, house_name in enumerate(HOUSE_NAMES):
        houses.append(
            House(
                id=new_id("house"),
                name=f"House {house_name}",
                motto=rng.choice(
                    [
                        "Hold the line",
                        "By wit and blade",
                        "We endure",
                        "None shall pass",
                    ]
                ),
                lordship_id=lordships[i % len(lordships)].id,
                prestige=rng.uniform(35, 75),
            )
        )

    realm = Realm(id=new_id("realm"), name=COUNTY_NAME, county_title_id=county_title.id)

    world = WorldState(
        seed=seed,
        day=0,
        realm=realm,
        titles={county_title.id: county_title, **{t.id: t for t in lordships}},
        houses={h.id: h for h in houses},
    )

    per_house = max(12, population_target // len(houses))
    all_chars: list[Character] = []
    for house in houses:
        all_chars.extend(_seed_kinship(rng, world, house, per_house))

    peasants_needed = population_target - len(all_chars)
    for _ in range(max(0, peasants_needed)):
        house = rng.choice(houses)
        all_chars.append(
            _create_character(
                rng,
                house_id=house.id,
                role="peasant",
                age=rng.randint(4, 70),
            )
        )

    for c in all_chars:
        world.characters[c.id] = c

    # Assign house head titles and one lord per lordship from house heads.
    for i, house in enumerate(houses):
        if house.head_character_id:
            head = world.characters[house.head_character_id]
            title = Title(
                id=new_id("title"),
                name=f"{house.name} Head",
                kind=TitleKind.HOUSE_HEAD,
                holder_id=head.id,
                house_id=house.id,
            )
            world.titles[title.id] = title
            head.title_id = title.id
        if i < len(lordships) and house.head_character_id:
            lordships[i].holder_id = house.head_character_id
            world.characters[house.head_character_id].role = "noble"

    county_title.holder_id = houses[0].head_character_id

    # Initial sibling relationships for inheritance drama hooks.
    for house in houses:
        if not house.head_character_id:
            continue
        head = world.characters[house.head_character_id]
        for cid, other in world.characters.items():
            if other.house_id != house.id or cid == head.id:
                continue
            if head.id in other.parent_ids:
                rel = world.get_relationship(head.id, other.id)
                rel.affection = rng.uniform(55, 85)
                rel.trust = rng.uniform(40, 70)
                if other.sex == head.sex and other.age_years >= head.age_years - 3:
                    rel.envy = rng.uniform(20, 60)
                    rel.resentment = rng.uniform(10, 45)

    return world
