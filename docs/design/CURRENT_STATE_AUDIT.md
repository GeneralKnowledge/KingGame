# KingGame — Current State Audit

**Audit date:** 2026-10-13  
**Repository:** https://github.com/GeneralKnowledge/KingGame

This audit distinguishes **branch reality** from **marketing names**. The product vision uses **KingGame**; the in-repo prototype package is named `the-chronicle` / **The Chronicle** on the Streamlit title bar.

## Branch and history snapshot

| Branch | State |
|--------|--------|
| `main` | Single commit: `README.md` containing `# KingGame` only. **No simulation code.** |
| `cursor/chronicle-phase1-prototype-bdeb` (PR #1) | Phase 1 scaffold: models, generation, lifecycle simulation, chronicle, SQLite, Streamlit, tests. **Not merged to `main` at audit time.** |

**Audit basis:** Files and tests on `cursor/chronicle-phase1-prototype-bdeb` (current workspace), with `main` noted explicitly.

### Tests executed (2026-10-13)

Command: `python3 -m pytest -v` from repository root.

| Result | Detail |
|--------|--------|
| **4 passed** | `test_generate_world_population_in_range`, `test_simulation_is_deterministic_for_fixed_seed`, `test_long_run_produces_lifecycle_events`, `test_random_character_has_family_context` |
| Runtime | ~0.86s |
| Not run | Streamlit UI, SQLite round-trip, property-based tests (Hypothesis installed but unused) |

---

## Repository structure (prototype branch)

```
app/streamlit_app.py          # Observer UI
chronicle/
  models/                     # Pydantic domain models
  generation/realm.py           # Initial world builder
  simulation/engine.py        # Daily tick orchestration
  simulation/lifecycle.py     # Birth, death, marriage, inheritance
  history/                    # Event append + chronicle text
  persistence/sqlite_store.py # Full-state JSON blob in SQLite
  character_ai/               # Stub (docstring only)
  social/                     # Stub
  events/                     # Stub
tests/test_simulation.py
pyproject.toml                # deps: pydantic, streamlit; dev: pytest, hypothesis
```

**Tooling:** No ESLint (Python project). No CI config in repo. Editable install via `pip install -e ".[dev]"`.

---

## Capability matrix

Legend: ✅ working · ⚠️ incomplete/superficial · 🧩 stub/disconnected · ❌ not implemented

### World model and persistence

| Capability | Status | Evidence |
|------------|--------|----------|
| `Character`, `House`, `Title`, `Realm`, `WorldState` | ✅ | `chronicle/models/*.py` |
| `DirectedRelationship` model | ⚠️ | Defined; only populated at world gen for some sibling pairs |
| `Goal`, `Memory` on `Character` | 🧩 | Schema exists; simulation never writes goals/memories |
| `WorldEvent` append-only log | ✅ | `history/log.py`, events accumulate in `world.events` |
| SQLite save/load | ⚠️ | Serialises entire `WorldState` as JSON; no migrations, single slot |
| Deterministic RNG per day | ✅ | `Random(world.seed + world.day)` in `SimulationEngine` |

### Realm generation

| Capability | Status | Evidence |
|------------|--------|----------|
| ~200 population target | ✅ | `generate_world(population_target=200)`; tests assert 150–260 |
| 8 houses, 3 lordships, 1 county | ✅ | `generation/realm.py` |
| Kinship seeds (head, spouse, children) | ✅ | `_seed_kinship` |
| Roles (peasant, noble, clergy, etc.) | ✅ | Assigned at generation |
| 11 continuous traits per character | ⚠️ | Random 0.15–0.85; **not used in decisions** except marriage acceptance nudge |
| Initial sibling relationship axes | ⚠️ | envy/resentment seeded once; never updated |

### Simulation engine

| Capability | Status | Evidence |
|------------|--------|----------|
| Daily tick | ✅ | `SimulationEngine.tick()` |
| Tick order | ✅ | day++ → age (yearly) → deaths → marriages (every 14d) → births (every 30d) |
| Aging | ✅ | +1 year every 365 days |
| Death | ⚠️ | Age-based daily probability; no cause, disease, or violence |
| Marriage | ⚠️ | Random pairing of eligible cross-house singles; prestige/personality roll |
| Birth | ⚠️ | Fixed 8% chance monthly for married women 18–42 |
| Succession / inheritance | ⚠️ | Male-preference eldest child/heir pool; house head title transfer |
| Character-initiated social actions | ❌ | No proposals, schemes, promises |
| Population-independent systems | ❌ | No economy, war, religion, travel |

### Character AI and social modules

| Capability | Status | Evidence |
|------------|--------|----------|
| `character_ai/` | 🧩 | Empty package docstring |
| `social/` | 🧩 | Empty package docstring |
| `events/` resolver | 🧩 | Empty package docstring |
| Utility / goals / plans | ❌ | — |

### History and chronicle

| Capability | Status | Evidence |
|------------|--------|----------|
| Event recording with `causes`, `effects` | ⚠️ | Fields exist; `causes` sometimes stores character IDs not event IDs |
| Chronicle rendering | ⚠️ | Prefers `event.summary`; fallback templates by `EventKind` |
| Significance ranking / story arcs | ❌ | — |
| Biographies | ❌ | — |
| Causal investigation UI | ❌ | — |

### Observer interface (Streamlit)

| Capability | Status | Evidence |
|------------|--------|----------|
| Time advance (+1/7/30/365 days) | ✅ | Buttons wired to engine |
| New world (fixed seed 42) | ✅ | |
| Save to SQLite | ✅ | |
| Living chronicle feed | ✅ | Last ~35 events |
| Character picker + traits + relationships | ⚠️ | Relationships mostly empty after gen |
| Event list per character | ✅ | |
| Family tree view | ❌ | |
| Plans, goals, memories display | ❌ | Data absent |
| Causal trace | ❌ | |

### Event kinds declared vs used

**Used in simulation:** `birth`, `death`, `marriage`, `inheritance`, `succession`

**Declared but unused:** `aging`, `promise`, `rumour`, `scheme`, `reconciliation`, `custom`

---

## Architectural constraints (observed)

**Preserve:**

- Python + Pydantic domain models
- Deterministic seeded simulation core (UI-agnostic)
- Modular monolith package layout
- Append-only event log as narrative source of truth
- SQLite (or equivalent) snapshot persistence for prototype
- Streamlit as observer shell until investigation tools justify a heavier frontend

**Technical debt to schedule (not blockers for design):**

1. **Naming:** KingGame vs The Chronicle vs package `the-chronicle`.
2. **Global ID counter:** `reset_id_counter()` on world gen — correct for reproducibility; event IDs during sim use same counter (OK if documented).
3. **`causes` semantics:** Mix of entity IDs and event IDs — normalise in milestone A3.
4. **In-memory event list:** Will need pagination / archival for multi-century runs (Stage F).
5. **No headless CLI** for batch simulation yet (Stage F2).
6. **Traits partially redundant** (`honest` vs `deceitful`, `courageous` vs `cautious`) — design decision in [DECISIONS.md](./DECISIONS.md).

---

## Reuse recommendations

| Asset | Reuse |
|-------|--------|
| Pydantic models | Extend in place; avoid parallel schema |
| `SimulationEngine` tick loop | Insert decision phases **before** lifecycle resolution |
| `append_event` | Single write path for authoritative history |
| `generate_world` | Keep as scenario fixture factory; add smaller scenario seeds for tests |
| Streamlit app | Evolve incrementally; split pages in F1 |
| Existing pytest smoke tests | Keep as regression gate; expand per [SIMULATION_EVALUATION.md](./SIMULATION_EVALUATION.md) |

---

## What the game actually does today (honest summary)

On the prototype branch, KingGame is a **deterministic demography and genealogy toy** with flavour text. It produces births, deaths, marriages, and house-head successions across a fixed initial realm. Personalities and relationships are **mostly decorative**. Nothing chooses actions from motives; drama is incidental, not emergent from competing goals.

That is an appropriate **Stage A foundation**, not yet the product vision.

---

## Cross-references

- Vision and pillars: [GAME_DESIGN.md](./GAME_DESIGN.md)
- Target architecture: [SIMULATION_ARCHITECTURE.md](./SIMULATION_ARCHITECTURE.md)
- Milestones: [ROADMAP.md](./ROADMAP.md)
- Decisions: [DECISIONS.md](./DECISIONS.md)
- Quality bar: [SIMULATION_EVALUATION.md](./SIMULATION_EVALUATION.md)
