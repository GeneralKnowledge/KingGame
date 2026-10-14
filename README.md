# KingGame

A **dynastic life simulator first, game second**: a small medieval realm where families, marriages, inheritance, and personality-driven choices write their own history. The in-game chronicle (**The Chronicle** observer UI) **observes** the simulation—it does not invent events.

**Design and roadmap:** [docs/design/README.md](docs/design/README.md)

## Phase 1 (this prototype)

- Haldenmere county with three lordships and eight noble houses (~200 characters)
- Daily simulation ticks: aging, births, deaths, courtship/marriage, succession & inheritance
- Append-only event log with causal references (extensible)
- Streamlit observer UI: time controls, living chronicle, character inspector
- SQLite save/load
- Deterministic runs from seed (reproducible simulations)

## Architecture (modular monolith)

| Module | Role |
|--------|------|
| `chronicle/models` | World model (characters, houses, titles, events) |
| `chronicle/generation` | Initial realm generation |
| `chronicle/simulation` | Tick engine & lifecycle |
| `chronicle/history` | Event log & chronicle rendering |
| `chronicle/persistence` | SQLite snapshots |
| `chronicle/character_ai` | Phase 2 — goals & utility AI |
| `chronicle/social` | Phase 3 — relationships & memories |
| `chronicle/events` | Phase 4 — action resolver |

## Run locally

```bash
pip install -e ".[dev]"
pytest
streamlit run app/streamlit_app.py
```

## Roadmap

Implementation milestones and dependencies live in [docs/design/ROADMAP.md](docs/design/ROADMAP.md). Phase 1 (world of people) matches the prototype on `main`; agency and social systems follow stages B–F in that document.
