# KingGame — Simulation Evaluation Framework

How to measure whether KingGame produces **believable stories**, not merely **many events**.

**Related:** [GAME_DESIGN.md](./GAME_DESIGN.md) pillars · [ROADMAP.md](./ROADMAP.md) milestone exit criteria

---

## 1. Principles

1. **Reproducibility first:** Every experiment records `seed`, git commit, schema version.
2. **Separate metrics from targets:** Establish baselines before setting numeric thresholds.
3. **Human rubric + automation:** Some qualities need chronicle review samples.
4. **Headless batch runs:** UI not required for evaluation (F2).

---

## 2. Test layers

| Layer | Purpose | Tools |
|-------|---------|-------|
| Unit | Model invariants, utility math, relationship deltas | pytest |
| Integration | Tick + resolver + event log consistency | pytest fixtures |
| Simulation experiments | Multi-seed, multi-decade batches | `chronicle.run` (F2) + JSON reports |
| Narrative QA | Human or LLM-assist **scoring rubric** on exported chronicles | Sample 10 seeds × 50 years |

---

## 3. Quality criteria and experiments

### 3.1 Personality differentiation

**Question:** Do different temperaments change action distributions?

**Experiment:** Fixture `personality_sensitivity`: 4 clones of realm, only house head trait swapped (cautious vs impulsive vs ambitious vs compassionate). Run 10 years.

**Metrics:**

- KL divergence or chi-square over action kind histograms per variant
- Mean utility of risky actions (`scheme`, `public_insult`) vs cautious actions

**Target (after baseline):** Impulsive variant ≥30% higher risky-action rate than cautious (same seed family).

**Milestone gate:** B4

---

### 3.2 Relationship consistency

**Experiment:** Scripted promise → break → measure trust delta; sacrifice → loyalty increase.

**Metrics:**

- Trust change sign correctness 100% on unit tests
- Resentment/affection can co-occur above threshold in sibling fixture

**Target:** Unit tests pass; integration trust delta within documented bounds.

**Milestone gate:** C1, C2

---

### 3.3 Social agency

**Question:** Do characters initiate non-demographic events?

**Experiment:** 50-year headless run, seed 0–99.

**Metrics:**

- `initiated_social_events / total_events` (exclude birth/death/aging)
- Unique actors initiating schemes or marriage proposals per century

**Target (initial):** ≥0.5 social initiations per character per 50 years (median); tune after B3.

**Milestone gate:** B4

---

### 3.4 Causal continuity

**Experiment:** Sample 20 significant events (score > T); automated backward walk on causal graph.

**Metrics:**

- `% with trace depth ≥2 to non-demographic cause`
- Zero orphan significant events (no cause and not tagged `exogenous`)

**Target:** ≥85% trace depth ≥2 for significant events (E1+).

**Milestone gate:** E1, A3

---

### 3.5 Generational continuity

**Experiment:** 100-year run; validate kinship and titles each year.

**Metrics:**

- House head always alive or null with regency flag (when implemented)
- Heir claims match succession law in 100% sampled deaths
- Memory references only dead characters when historical (no id ghosting)

**Target:** Zero invariant violations in automated checker.

**Milestone gate:** A2, D1

---

### 3.6 Narrative diversity

**Experiment:** 50 seeds × 30 years; hash event graph topology (kind sequence + house ids).

**Metrics:**

- Unique topology count / 50
- Bigram repetition rate in chronicle summaries

**Target:** ≥70% unique topologies; bigram repetition below baseline CK-style feed (manual rubric initially).

**Milestone gate:** F3

---

### 3.7 Believable surprises

**Human rubric** (1–5) on 10 sampled stories:

- Understandable motive
- Not random noise
- Not identical to prior seed

**Target:** Median ≥4 after Minimum Story Realm.

**Milestone gate:** F3

---

### 3.8 Population health

**Metrics per 100-year run:**

- Living population min/max/mean
- Marriage rate (marriages / eligible person-years)
- Fraction never married by age 40
- Mean trust across pairs (detect suspicion deadlock: mean trust <25 everywhere)
- Active feud count equilibrium

**Targets (initial guardrails):**

- Population stays within 50–150% of start (200 baseline)
- Marriage rate > 0.02 eligible person-years
- Never-married by 40 < 60%
- No global trust deadlock

**Milestone gate:** F3, ongoing regression

---

### 3.9 Observer value

**Task study (developer-as-player):** 15 minutes to find one 3-hop causal story.

**Success:** Complete within time using UI tools only.

**Milestone gate:** F1

---

## 4. Reproducibility requirements

- `WorldState.seed` immutable during run
- Log `sim_version` string in export metadata
- CI runs: unit + 1 short integration (500 days) on every PR
- Weekly (optional): 20-seed batch on main

**Regression:** `test_simulation_is_deterministic_for_fixed_seed` (existing) extended to include decision phase when added.

---

## 5. Anti-metrics (do not optimise)

- Raw event count per day
- Chronicle length
- Random action diversity without motive linkage

---

## 6. Fixture library (build over milestones)

| Fixture | Purpose |
|---------|---------|
| `haldenmere_200` | Default realm gen |
| `eleanor_succession_40` | North-star story |
| `personality_sensitivity` | B4 |
| `promise_betrayal_pair` | C1/C2 |
| `three_house_rivalry` | D3 |

Store under `tests/fixtures/` as seed + parameters JSON.

---

## 7. Reporting format

Batch runner outputs `report.json`:

```json
{
  "seed": 42,
  "days": 18250,
  "metrics": { "population_health": {}, "social_agency": {} },
  "invariant_violations": [],
  "sample_chronicle_path": "artifacts/chronicle_42.txt"
}
```

---

## Cross-references

- Current tests: [CURRENT_STATE_AUDIT.md](./CURRENT_STATE_AUDIT.md)
- Milestones: [ROADMAP.md](./ROADMAP.md)
