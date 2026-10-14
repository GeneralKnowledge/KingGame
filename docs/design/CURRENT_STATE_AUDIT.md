# KingGame — Current State Audit

**Audit date:** 2026-10-14 (baseline for milestone A2)  
**Repository:** https://github.com/GeneralKnowledge/KingGame

This audit distinguishes **branch reality** from **marketing names**. The product vision uses **KingGame**; the in-repo prototype package is named `the-chronicle` / **The Chronicle** on the Streamlit title bar.

## Branch and history snapshot

| Branch | State |
|--------|--------|
| `main` | Phase 1 prototype merged (PR #1 + design docs PR #2): models, generation, lifecycle simulation, chronicle, SQLite, Streamlit, `docs/design/*`, four smoke tests. |
| `a2-lifecycle-integrity` | Milestone A2 work: lifecycle invariants, RNG, ID persistence, save/load safety (in progress). |

**Audit basis:** Code and tests on `main` unless a row explicitly refers to A2 branch progress.

### Tests executed (2026-10-14, A2 task 1 baseline on `main`)

Command: `python -m pytest -v` from repository root.

| Result | Detail |
|--------|--------|
| **4 passed** | `test_generate_world_population_in_range`, `test_simulation_is_deterministic_for_fixed_seed`, `test_long_run_produces_lifecycle_events`, `test_random_character_has_family_context` |
| Runtime | ~0.89s |
| **Executed** | Full pytest suite above |
| **Inspected only (not executed)** | Streamlit UI manual session, SQLite save/load round-trip, Hypothesis property tests, headless batch CLI |

### Milestone A2 status (on `a2-lifecycle-integrity`)

| Item | Status (A2 complete on `a2-lifecycle-integrity`) |
|------|-----------------------------------------------------|
| String-seeded RNG (`derive_rng`) | Implemented |
| `WorldState.next_entity_id` / save-load ID safety | Implemented |
| `validate_world` invariant checker | Implemented |
| Widowhood, `death_day`, title/lordship sync, `schema_version` | Implemented |
| Persistence equivalence tests | Implemented |
| Population health loose-bound test | Implemented |
| `python -m chronicle.run` | Implemented |

---

## Repository structure (`main`)

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
| Deterministic RNG per day | ✅ | `derive_rng(seed, day, module)` in `chronicle/world/rng.py` (A2) |

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
2. **Global ID counter:** Process-global counter not persisted in `WorldState` — **A2 task 3** addresses save/load duplication risk.
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

On `main`, KingGame is a **deterministic demography and genealogy toy** with flavour text. It produces births, deaths, marriages, and house-head successions across a fixed initial realm. Personalities and relationships are **mostly decorative**. Nothing chooses actions from motives; drama is incidental, not emergent from competing goals.

That is an appropriate **Stage A foundation**, not yet the product vision.

---

## Cross-references

- Vision and pillars: [GAME_DESIGN.md](./GAME_DESIGN.md)
- Target architecture: [SIMULATION_ARCHITECTURE.md](./SIMULATION_ARCHITECTURE.md)
- Milestones: [ROADMAP.md](./ROADMAP.md)
- Decisions: [DECISIONS.md](./DECISIONS.md)
- Quality bar: [SIMULATION_EVALUATION.md](./SIMULATION_EVALUATION.md)
