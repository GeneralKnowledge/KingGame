from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventKind(str, Enum):
    BIRTH = "birth"
    DEATH = "death"
    MARRIAGE = "marriage"
    INHERITANCE = "inheritance"
    SUCCESSION = "succession"
    AGING = "aging"
    PROMISE = "promise"
    RUMOUR = "rumour"
    SCHEME = "scheme"
    RECONCILIATION = "reconciliation"
    CUSTOM = "custom"


class WorldEvent(BaseModel):
    """Append-only simulation fact. Chronicle observes; it does not invent."""

    id: str
    day: int
    kind: EventKind
    actor_id: str | None = None
    target_id: str | None = None
    participant_ids: list[str] = Field(default_factory=list)
    causes: list[str] = Field(default_factory=list)
    effects: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""
