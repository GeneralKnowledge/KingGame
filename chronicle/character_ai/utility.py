from __future__ import annotations

import math
import random
from enum import Enum

from chronicle.character_ai import goals as goal_logic
from chronicle.character_ai.traits import trait_bias
from chronicle.models.character import Character
from chronicle.models.world import WorldState

SOCIAL_ROLES = frozenset({"noble", "knight", "courtier"})


class ActionKind(str, Enum):
    WAIT = "wait"
    PUBLIC_INSULT = "public_insult"
    PRIVATE_APOLOGY = "private_apology"


def eligible_social_actors(world: WorldState) -> list[Character]:
    return sorted(
        [
            c
            for c in world.living_characters()
            if c.role in SOCIAL_ROLES and c.age_years >= 16
        ],
        key=lambda c: c.id,
    )


MAX_CANDIDATE_TARGETS = 12


def candidate_targets(world: WorldState, actor: Character) -> list[str]:
    ids = [
        c.id
        for c in eligible_social_actors(world)
        if c.id != actor.id
    ]
    if len(ids) <= MAX_CANDIDATE_TARGETS:
        return sorted(ids)

    goal_targets = {g.target_id for g in actor.goals if g.target_id}
    ranked: list[tuple[float, str]] = []
    for target_id in ids:
        rel = world.get_relationship(actor.id, target_id)
        salience = max(
            rel.resentment,
            rel.envy,
            abs(rel.affection - 50.0),
            abs(rel.trust - 50.0),
        )
        if target_id in goal_targets:
            salience += 100.0
        ranked.append((salience, target_id))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    chosen = [tid for _, tid in ranked[:MAX_CANDIDATE_TARGETS]]
    return sorted(chosen)


def score_action(
    world: WorldState,
    actor: Character,
    action: ActionKind,
    target_id: str | None,
) -> float:
    if action == ActionKind.WAIT:
        base = 0.35
        for goal in actor.goals:
            base += goal_logic.goal_utility_contribution(
                goal, action.value, target_id=target_id
            )
        base += trait_bias("private_apology", actor.traits) * 0.5
        return base

    if not target_id or target_id not in world.characters:
        return -1e9

    target = world.characters[target_id]
    if not target.alive:
        return -1e9

    rel = world.get_relationship(actor.id, target_id)
    action_key = action.value

    if action == ActionKind.PUBLIC_INSULT:
        base = 0.25
        base += (rel.resentment - 40.0) / 120.0
        base += trait_bias("public_insult", actor.traits)
        base -= trait_bias("private_apology", actor.traits) * 0.5
        base += (rel.envy / 100.0) * 0.15
    elif action == ActionKind.PRIVATE_APOLOGY:
        base = 0.2
        base += (50.0 - rel.affection) / 100.0
        base += trait_bias("private_apology", actor.traits)
        base -= (rel.resentment / 100.0) * 0.2
        if rel.resentment < 25:
            base -= 0.25
    else:
        base = 0.0

    for goal in actor.goals:
        base += goal_logic.goal_utility_contribution(
            goal, action_key, target_id=target_id
        )

    return base


def _softmax_choice(
    options: list[tuple[ActionKind, str | None, float]],
    rng: random.Random,
    temperature: float = 0.45,
) -> tuple[ActionKind, str | None]:
    if not options:
        return ActionKind.WAIT, None
    max_score = max(s for _, _, s in options)
    weights: list[float] = []
    for _, _, score in options:
        weights.append(math.exp((score - max_score) / max(temperature, 0.05)))
    total = sum(weights)
    if total <= 0:
        return options[0][0], options[0][1]
    pick = rng.random() * total
    acc = 0.0
    for (action, target_id, _), w in zip(options, weights, strict=True):
        acc += w
        if pick <= acc:
            return action, target_id
    last = options[-1]
    return last[0], last[1]


def choose_action(
    world: WorldState,
    actor: Character,
    rng: random.Random,
) -> tuple[ActionKind, str | None, dict[str, float]]:
    options: list[tuple[ActionKind, str | None, float]] = []
    wait_score = score_action(world, actor, ActionKind.WAIT, None)
    options.append((ActionKind.WAIT, None, wait_score))

    for target_id in candidate_targets(world, actor):
        for action in (ActionKind.PUBLIC_INSULT, ActionKind.PRIVATE_APOLOGY):
            sc = score_action(world, actor, action, target_id)
            options.append((action, target_id, sc))

    options.sort(key=lambda x: (x[0].value, x[1] or ""))
    snapshot = {
        f"{a.value}:{t or '-'}": s for a, t, s in options
    }
    action, target_id = _softmax_choice(options, rng)
    return action, target_id, snapshot
