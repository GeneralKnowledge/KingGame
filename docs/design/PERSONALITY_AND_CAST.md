# Personality, cast, and story focus (single realm)

**Product:** KingGame / Haldenmere — one abstract country, no map, observation-first drama (CK3-inspired families and succession, not warfare sim).

**Companion:** [GAME_DESIGN.md](./GAME_DESIGN.md) · [DECISIONS.md](./DECISIONS.md) D4 · [ROADMAP.md](./ROADMAP.md)

---

## 1. Hybrid personality model

Players should see **several readable traits per person**; the simulation uses a **full core vector** plus optional **tags**.

### 1.1 Core temperament (8 dimensions)

Continuous **0–1** on every character (DECISIONS D4):

| Dimension | Role in utility / social |
|-----------|-------------------------|
| ambition | Power, titles, schemes |
| courage | Risk-taking, confrontation |
| compassion | Forgiveness, mercy, family pressure |
| honesty | Oaths, rumours, deceit actions |
| pride | Insults, marriage prestige |
| patience | Long plans, waiting |
| sociability | Courtship, alliances |
| vengefulness | Feuds, reconciliation refusal |

**Legacy prototype:** 11 independent floats (`courageous`, `cautious`, …) map to these 8 on load (see `chronicle/character_ai/traits.py`).

### 1.2 Derived highlights (UI only)

2–4 labels computed from cores (e.g. **Ambitious**, **Forgiving**, **Hot-headed**) — not separate persisted state. Used in Streamlit and future biographies.

### 1.3 State / acquired tags (v0)

Several may coexist. Persisted on `Character.tags` when they affect sim or chronicle.

| Tag | Typical source | Sim effect (v0+) |
|-----|----------------|------------------|
| `widowed` | Spouse death | Flavour; chronicle |
| `disgraced` | Future schemes | Utility modifier (later) |
| `infertile` | Rare at marriage RNG | Couple fertility multiplier |
| `disinherited` | D1 succession | Claims / utility |
| `regent` | D1 vacant minor heir | Title proxy (later) |

Congenital / education trait **picks** defer to post-B2 (**B2b**).

---

## 2. Childless couples and succession drama

**County demography** stays regulated (A2b `DemographyConfig`). **House-level** lines may end with **no surviving legitimate heirs**.

### Mechanisms

1. **Per-couple fertility multiplier** (A2c): assigned at marriage via `derive_rng(seed, day, "couple_fertility", pair_key)`; log-normal around 1.0; some couples naturally childless.
2. **Infant/child mortality** (A2b): already culls heirs; couples may lose all children.
3. **D1 claims:** Vacant house head, sibling/cousin **Claim** objects, `support_heir` / dispute events — **no warfare**; pressure via prestige, alliances, rumours.

### Evaluation (slow tests)

- Population 120–450 at years 25/50/75/100 (seeds 0–9).
- Over 100 years, a measurable share of houses experience at least one **childless succession** (no living legitimate child at head death).

**Avoid:** post-hoc deletion of children to hit quotas.

---

## 3. Cast hierarchy and story builder

### 3.1 Political ladder (Haldenmere)

```
County holder (1)
  └── Lordships (3)
        └── Houses (8) — house head title
              └── Knights, courtiers, peasants, clergy
```

No tile map. Travel is abstract “at court” unless a story flag marks a character away.

### 3.2 Named cast vs demographic fill

| Tier | Approx. count | Chronicle default |
|------|---------------|-------------------|
| Named court | 40–80 | Full lifecycle + social events |
| Demographic fill | remainder of ~200–400 | Hide routine peasant birth/death unless dynasty-linked |

**Story importance** is a derived score (role, title distance to county holder, event participation, kin to ruler). See `chronicle/history/story.py`.

### 3.3 Observer flow

1. Advance time; chronicle ranks by **significance** (succession crises highest).
2. Filter **named cast** in UI optional toggle.
3. Bookmark a house head or courtier; on death, suggest heir, claimant, or widowed spouse.

### 3.4 War (deferred)

Abstract **plot pressure** only later (prestige, hostage, “levies raised” event). No unit combat.

---

## 4. Implementation map

| Milestone | Deliverable |
|-----------|-------------|
| Doc (this file) | Shared vocabulary |
| B2 | 8 cores, migration, `trait_bias()`, UI highlights |
| A2c | Couple fertility multiplier + calibration |
| D1 | `Claim`, succession law, childless/vacant events |
| E1 | `StoryImportance`, chronicle ranking, Streamlit filter |

---

## 5. Acceptance (story-first)

- Named-court characters show **8 cores + highlights + tags** in UI.
- Multi-seed runs produce **vacant/disputed successions** from genealogy, zero invariant violations.
- Player can browse **county → lordships → houses** without a map.
- A2b population bands hold after A2c recalibration.
