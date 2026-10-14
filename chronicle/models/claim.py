from __future__ import annotations

from pydantic import BaseModel, Field


class Claim(BaseModel):
    """Pressable right to a title (D1 — disputes without warfare)."""

    id: str
    character_id: str
    title_id: str
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    reason: str = "inheritance"
    created_day: int = 0
