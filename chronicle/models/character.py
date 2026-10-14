from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"


class LifeStage(str, Enum):
    CHILD = "child"
    YOUTH = "youth"
    ADULT = "adult"
    ELDER = "elder"


Role = Literal[
    "peasant",
    "servant",
    "clergy",
    "courtier",
    "knight",
    "noble",
]


# Stable temperament axes used in Phase 1; expanded in Phase 2 decision engine.
DEFAULT_TRAITS: tuple[str, ...] = (
    "courageous",
    "cautious",
    "ambitious",
    "compassionate",
    "jealous",
    "honest",
    "deceitful",
    "patient",
    "impulsive",
    "proud",
    "sociable",
)


class Goal(BaseModel):
    """Placeholder for Phase 2 utility-based planning."""

    kind: str
    priority: float = Field(ge=0.0, le=1.0)
    target_id: str | None = None


class Memory(BaseModel):
    """Bridge between events and future decisions (Phase 3+)."""

    id: str
    day: int
    actor_id: str | None
    summary: str
    believed_summary: str | None = None
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_tags: list[str] = Field(default_factory=list)
    discussed: bool = False
    forgiven: bool = False
    disproved: bool = False


class Character(BaseModel):
    id: str
    name: str
    age_years: int = Field(ge=0)
    sex: Sex
    house_id: str | None = None
    role: Role = "peasant"
    parent_ids: tuple[str, ...] = ()
    birth_day: int = 0
    last_birth_day: int | None = None
    death_day: int | None = None
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    spouse_id: str | None = None
    traits: dict[str, float] = Field(default_factory=dict)
    goals: list[Goal] = Field(default_factory=list)
    memories: list[Memory] = Field(default_factory=list)
    alive: bool = True
    title_id: str | None = None

    def life_stage(self) -> LifeStage:
        if self.age_years < 12:
            return LifeStage.CHILD
        if self.age_years < 18:
            return LifeStage.YOUTH
        if self.age_years < 55:
            return LifeStage.ADULT
        return LifeStage.ELDER

    def is_marriageable(self) -> bool:
        return (
            self.alive
            and self.spouse_id is None
            and self.marital_status != MaritalStatus.MARRIED
            and 16 <= self.age_years <= 45
            and self.life_stage() in (LifeStage.YOUTH, LifeStage.ADULT)
        )
