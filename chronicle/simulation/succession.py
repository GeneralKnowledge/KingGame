from __future__ import annotations

from chronicle.history.log import append_event
from chronicle.models.character import Character, Goal, Sex
from chronicle.models.claim import Claim
from chronicle.models.events import EventKind
from chronicle.models.house import TitleKind
from chronicle.models.world import WorldState
from chronicle.world.ids import allocate_id


def living_legitimate_children(world: WorldState, parent_id: str) -> list[Character]:
    return [
        c
        for c in world.living_characters()
        if parent_id in c.parent_ids
    ]


def had_childless_succession(world: WorldState, deceased_id: str) -> bool:
    """True if deceased has no living children at death (succession drama hook)."""
    return len(living_legitimate_children(world, deceased_id)) == 0


def _sibling_claimants(
    world: WorldState, deceased: Character, title_id: str
) -> list[Character]:
    if not deceased.house_id:
        return []
    if deceased.parent_ids:
        siblings = [
            c
            for c in world.living_characters()
            if c.house_id == deceased.house_id
            and c.id != deceased.id
            and c.parent_ids == deceased.parent_ids
        ]
        if siblings:
            return siblings
    return [
        c
        for c in world.living_characters()
        if c.house_id == deceased.house_id
        and c.id != deceased.id
        and deceased.id not in c.parent_ids
    ]


def grant_claim(
    world: WorldState,
    *,
    character_id: str,
    title_id: str,
    strength: float,
    reason: str,
) -> Claim:
    claim_id = allocate_id(world, "claim")
    claim = Claim(
        id=claim_id,
        character_id=character_id,
        title_id=title_id,
        strength=strength,
        reason=reason,
        created_day=world.day,
    )
    world.claims[claim_id] = claim
    char = world.characters[character_id]
    if not any(g.kind == "press_claim" and g.target_id == title_id for g in char.goals):
        char.goals.append(
            Goal(kind="press_claim", priority=min(0.95, 0.55 + strength * 0.4), target_id=title_id)
        )
    return claim


def handle_succession_drama(
    world: WorldState,
    deceased_id: str,
    *,
    heir_id: str | None,
    was_head: bool,
) -> None:
    """Create claims and chronicle hooks for vacant or disputed succession."""
    deceased = world.characters[deceased_id]
    childless = had_childless_succession(world, deceased_id)

    house_titles = [
        t
        for t in world.titles.values()
        if t.house_id == deceased.house_id and t.kind == TitleKind.HOUSE_HEAD
    ]
    held = any(t.holder_id == deceased_id for t in world.titles.values())
    if not was_head and not held:
        return

    for title in house_titles:
        if heir_id is None or childless:
            for claimant in _sibling_claimants(world, deceased, title.id)[:3]:
                grant_claim(
                    world,
                    character_id=claimant.id,
                    title_id=title.id,
                    strength=0.45 if childless else 0.35,
                    reason="childless_line" if childless else "disputed_heir",
                )
            append_event(
                world,
                day=world.day,
                kind=EventKind.SUCCESSION,
                actor_id=None,
                causes=[deceased_id],
                effects={
                    "title_id": title.id,
                    "vacant": heir_id is None,
                    "childless": childless,
                    "disputed": True,
                },
                summary=(
                    f"{deceased.name}'s line ends with no surviving children; "
                    f"claims arise over {title.name}."
                    if childless
                    else f"Succession over {title.name} is disputed after {deceased.name}'s death."
                ),
            )
            continue

        heir = world.characters.get(heir_id)
        if heir and heir.sex == Sex.FEMALE:
            for claimant in _sibling_claimants(world, deceased, title.id):
                if claimant.sex == Sex.MALE and claimant.id != heir_id:
                    grant_claim(
                        world,
                        character_id=claimant.id,
                        title_id=title.id,
                        strength=0.4,
                        reason="male_preference",
                    )
            append_event(
                world,
                day=world.day,
                kind=EventKind.SUCCESSION,
                actor_id=heir_id,
                causes=[deceased_id],
                effects={"title_id": title.id, "disputed": True, "female_heir": True},
                summary=f"{heir.name} inherits {title.name}; male relations challenge the succession.",
            )
