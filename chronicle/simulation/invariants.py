from __future__ import annotations

from dataclasses import dataclass

from chronicle.models.character import MaritalStatus
from chronicle.models.house import TitleKind
from chronicle.models.world import WorldState

MIN_PARENT_AGE_AT_BIRTH_DAYS = 16 * 365


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    entity_ids: tuple[str, ...] = ()


def validate_world(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    violations.extend(_check_duplicate_ids(world))
    violations.extend(_check_spouse_symmetry(world))
    violations.extend(_check_marital_status(world))
    violations.extend(_check_parent_child(world))
    violations.extend(_check_titles(world))
    violations.extend(_check_house_heads(world))
    violations.extend(_check_ancestor_cycles(world))
    violations.extend(_check_temporal(world))
    violations.extend(_check_dead_characters(world))
    return violations


def _check_duplicate_ids(world: WorldState) -> list[Violation]:
    seen: dict[str, str] = {}
    violations: list[Violation] = []

    def register(entity_id: str, kind: str) -> None:
        if entity_id in seen:
            violations.append(
                Violation(
                    "duplicate_id",
                    f"Duplicate id {entity_id} ({kind} vs {seen[entity_id]})",
                    (entity_id,),
                )
            )
        else:
            seen[entity_id] = kind

    for cid in world.characters:
        register(cid, "character")
    for hid in world.houses:
        register(hid, "house")
    for tid in world.titles:
        register(tid, "title")
    for event in world.events:
        register(event.id, "event")
    register(world.realm.id, "realm")
    return violations


def _check_spouse_symmetry(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for char in world.characters.values():
        if char.spouse_id is None:
            continue
        spouse = world.characters.get(char.spouse_id)
        if spouse is None:
            violations.append(
                Violation(
                    "spouse_missing",
                    f"{char.id} spouse_id points to missing character",
                    (char.id, char.spouse_id),
                )
            )
            continue
        if spouse.spouse_id != char.id:
            violations.append(
                Violation(
                    "spouse_asymmetric",
                    f"Spouse link asymmetric between {char.id} and {spouse.id}",
                    (char.id, spouse.id),
                )
            )
    return violations


def _check_marital_status(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for char in world.characters.values():
        if not char.alive:
            continue
        if char.marital_status == MaritalStatus.MARRIED:
            if char.spouse_id is None:
                violations.append(
                    Violation(
                        "married_without_spouse",
                        f"{char.id} is married but has no spouse_id",
                        (char.id,),
                    )
                )
                continue
            spouse = world.characters.get(char.spouse_id)
            if spouse is None or not spouse.alive:
                violations.append(
                    Violation(
                        "spouse_dead_married",
                        f"{char.id} is married but spouse is missing or dead",
                        (char.id, char.spouse_id or ""),
                    )
                )
        if char.spouse_id is not None and char.marital_status == MaritalStatus.SINGLE:
            violations.append(
                Violation(
                    "spouse_but_single",
                    f"{char.id} has spouse_id but marital_status single",
                    (char.id,),
                )
            )
    return violations


def _check_parent_child(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for char in world.characters.values():
        for parent_id in char.parent_ids:
            if parent_id not in world.characters:
                violations.append(
                    Violation(
                        "parent_missing",
                        f"{char.id} references missing parent {parent_id}",
                        (char.id, parent_id),
                    )
                )
    return violations


def _check_titles(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for title in world.titles.values():
        if title.holder_id is None:
            violations.append(
                Violation(
                    "title_holder_missing",
                    f"Title {title.id} has no holder",
                    (title.id,),
                )
            )
            continue
        holder = world.characters.get(title.holder_id)
        if holder is None:
            violations.append(
                Violation(
                    "title_holder_missing",
                    f"Title {title.id} holder {title.holder_id} not found",
                    (title.id, title.holder_id),
                )
            )
            continue
        if not holder.alive:
            violations.append(
                Violation(
                    "title_holder_dead",
                    f"Title {title.id} held by dead character {holder.id}",
                    (title.id, holder.id),
                )
            )
        if title.kind == TitleKind.HOUSE_HEAD and holder.title_id != title.id:
            violations.append(
                Violation(
                    "title_holder_mismatch",
                    f"House head title {title.id} not reflected on holder",
                    (title.id, holder.id),
                )
            )
    return violations


def _check_house_heads(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for house in world.houses.values():
        if house.head_character_id is None:
            violations.append(
                Violation(
                    "house_head_missing",
                    f"House {house.id} has no head",
                    (house.id,),
                )
            )
            continue
        head = world.characters.get(house.head_character_id)
        if head is None:
            violations.append(
                Violation(
                    "house_head_missing",
                    f"House {house.id} head {house.head_character_id} not found",
                    (house.id, house.head_character_id),
                )
            )
            continue
        if not head.alive:
            violations.append(
                Violation(
                    "house_head_dead",
                    f"House {house.id} head {head.id} is dead",
                    (house.id, head.id),
                )
            )
        if head.house_id != house.id:
            violations.append(
                Violation(
                    "house_head_wrong_house",
                    f"Head {head.id} not in house {house.id}",
                    (house.id, head.id),
                )
            )
    return violations


def _check_ancestor_cycles(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []

    def ancestors(char_id: str) -> set[str]:
        visited: set[str] = set()
        stack = list(world.characters[char_id].parent_ids)
        while stack:
            pid = stack.pop()
            if pid == char_id:
                return {char_id}
            if pid in visited or pid not in world.characters:
                continue
            visited.add(pid)
            stack.extend(world.characters[pid].parent_ids)
        return visited

    for char_id in world.characters:
        if char_id in ancestors(char_id):
            violations.append(
                Violation(
                    "ancestor_cycle",
                    f"{char_id} is their own ancestor",
                    (char_id,),
                )
            )
    return violations


def _check_temporal(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for char in world.characters.values():
        if char.alive and char.death_day is not None:
            violations.append(
                Violation(
                    "temporal_death",
                    f"Living character {char.id} has death_day set",
                    (char.id,),
                )
            )
        if not char.alive and char.death_day is None:
            violations.append(
                Violation(
                    "temporal_death",
                    f"Dead character {char.id} missing death_day",
                    (char.id,),
                )
            )
        if char.death_day is not None and char.death_day < char.birth_day:
            violations.append(
                Violation(
                    "temporal_death",
                    f"{char.id} death_day before birth_day",
                    (char.id,),
                )
            )
        for parent_id in char.parent_ids:
            parent = world.characters.get(parent_id)
            if parent is None:
                continue
            min_parent_birth = char.birth_day - MIN_PARENT_AGE_AT_BIRTH_DAYS
            if parent.birth_day > min_parent_birth:
                violations.append(
                    Violation(
                        "temporal_birth",
                        f"{char.id} born before parent {parent_id} was old enough",
                        (char.id, parent_id),
                    )
                )
    return violations


def _check_dead_characters(world: WorldState) -> list[Violation]:
    violations: list[Violation] = []
    for char in world.characters.values():
        if not char.alive and char.spouse_id is not None:
            if char.marital_status == MaritalStatus.MARRIED:
                violations.append(
                    Violation(
                        "dead_still_married",
                        f"Dead character {char.id} still marked married",
                        (char.id,),
                    )
                )
    return violations
