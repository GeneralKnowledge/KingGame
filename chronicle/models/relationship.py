from __future__ import annotations

from pydantic import BaseModel, Field


class DirectedRelationship(BaseModel):
    """Directional social bond — Phase 3 expands usage in AI."""

    from_id: str
    to_id: str
    affection: float = Field(default=50.0, ge=0.0, le=100.0)
    trust: float = Field(default=50.0, ge=0.0, le=100.0)
    respect: float = Field(default=50.0, ge=0.0, le=100.0)
    fear: float = Field(default=0.0, ge=0.0, le=100.0)
    resentment: float = Field(default=0.0, ge=0.0, le=100.0)
    envy: float = Field(default=0.0, ge=0.0, le=100.0)


class RelationshipEdge(BaseModel):
    """Canonical key for relationship lookup."""

    from_id: str
    to_id: str

    def key(self) -> str:
        return f"{self.from_id}->{self.to_id}"
