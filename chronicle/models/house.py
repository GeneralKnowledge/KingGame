from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TitleKind(str, Enum):
    COUNTY = "county"
    LORDSHIP = "lordship"
    HOUSE_HEAD = "house_head"


class Title(BaseModel):
    id: str
    name: str
    kind: TitleKind
    holder_id: str | None = None
    house_id: str | None = None
    parent_title_id: str | None = None
    succession_law: str = "male_preference_eldest"


class House(BaseModel):
    id: str
    name: str
    motto: str = ""
    founder_id: str | None = None
    head_character_id: str | None = None
    lordship_id: str | None = None
    prestige: float = Field(default=50.0, ge=0.0, le=100.0)
