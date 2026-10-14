from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from chronicle.models.world import WorldState
from chronicle.world.ids import sync_id_counter_from_world

DEFAULT_DB = Path("data/chronicle.db")


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS saves (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            payload TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def save_world(world: WorldState, path: Path | None = None) -> None:
    db_path = path or DEFAULT_DB
    payload = world.model_dump_json()
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO saves (id, payload) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=CURRENT_TIMESTAMP",
            (payload,),
        )
        conn.commit()


def load_world(path: Path | None = None) -> WorldState | None:
    db_path = path or DEFAULT_DB
    if not db_path.exists():
        return None
    with _connect(db_path) as conn:
        row = conn.execute("SELECT payload FROM saves WHERE id = 1").fetchone()
    if not row:
        return None
    data = json.loads(row[0])
    world = WorldState.model_validate(data)
    sync_id_counter_from_world(world)
    return world
