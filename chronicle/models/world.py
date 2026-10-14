from __future__ import annotations

from pydantic import BaseModel, Field

from chronicle.models.character import Character
from chronicle.models.events import WorldEvent
from chronicle.models.house import House, Title
from chronicle.models.relationship import DirectedRelationship


class Realm(BaseModel):
    id: str
    name: str
    county_title_id: str


class WorldState(BaseModel):
    schema_version: int = 2
    seed: int
    day: int = 0
    next_entity_id: int = 1
    realm: Realm
    characters: dict[str, Character] = Field(default_factory=dict)
    houses: dict[str, House] = Field(default_factory=dict)
    titles: dict[str, Title] = Field(default_factory=dict)
    relationships: dict[str, DirectedRelationship] = Field(default_factory=dict)
    events: list[WorldEvent] = Field(default_factory=list)

    def living_characters(self) -> list[Character]:
        return [c for c in self.characters.values() if c.alive]

    def get_character(self, char_id: str) -> Character | None:
        return self.characters.get(char_id)

    def relationship_key(self, from_id: str, to_id: str) -> str:
        return f"{from_id}->{to_id}"

    def get_relationship(self, from_id: str, to_id: str) -> DirectedRelationship:
        key = self.relationship_key(from_id, to_id)
        if key not in self.relationships:
            self.relationships[key] = DirectedRelationship(from_id=from_id, to_id=to_id)
        return self.relationships[key]
