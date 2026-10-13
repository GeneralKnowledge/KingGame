# KingGame — Decision Log

Significant design and architecture decisions with defaults, rationale, and timing.

**Legend:** **Now** = settle before next implementation milestone · **Later** = default OK until milestone noted

---

## D1 — Product naming

| Option | Implications |
|--------|----------------|
| **KingGame everywhere** | Repo alignment; rename package from `the-chronicle` |
| Keep `chronicle` package, KingGame product | Minor confusion for contributors |

**Default:** **KingGame** public name; Python package rename to `kinggame` in milestone **A2** (optional, non-blocking).

**When:** Before public release; not blocking B1.

---

## D2 — Observer-only vs optional intervention

| Option | Implications |
|--------|----------------|
| Pure observer | Simpler ethics, clearer emergent cred |
| Optional god-tools | Fun experiments; risks breaking causality narrative |

**Default:** **Pure observer** for Minimum Story Realm; god-tools behind flag in **F1** with logged `player_caused` events.

**When:** Now (design); implement F1.

---

## D3 — Character agency granularity

| Option | Implications |
|--------|----------------|
| Daily decisions for all adults | Rich; ~200 chars costly |
| Staggered cohorts (1/7 per day) | 7-day reaction latency; cheaper |
| Weekly decisions | Faster but blunter drama |

**Default:** **Staggered daily cohort** + immediate resolve for crisis actions (succession day, marriage response).

**When:** Now; implement B3.

---

## D4 — Personality representation

| Option | Implications |
|--------|----------------|
| 11 independent 0–1 traits (prototype) | Redundant pairs; weak signal |
| 8 dimensions (Big-Five-ish + ambition, honesty, pride) | Less correlation |
| Categorical archetypes | Readable but caricature risk |

**Default:** **8 continuous dimensions** (0–1): ambition, courage, compassion, honesty, pride, patience, sociability, vengefulness. Retire redundant prototype traits via mapping on load.

**When:** **B2** (before utility tuning).

---

## D5 — Emotion vs personality

**Default:** Personality **biases** utility weights; emotions **temporarily shift** weights and decay daily (half-life ~7–30 days).

**When:** B2.

---

## D6 — Relationship storage

| Option | Implications |
|--------|----------------|
| Multi-axis directed dict (prototype) | Works; needs update rules |
| Single opinion score | Fails Pillar C |

**Default:** **Directed multi-axis** (affection, trust, respect, fear, resentment, envy, attraction optional) + explicit legal edges.

**When:** Now; implement C1.

---

## D7 — Memory and knowledge

| Option | Implications |
|--------|----------------|
| Full knowledge propagation graph | Expensive; powerful |
| Personal memories + local rumour pool | 80% value |

**Default:** **Staged:** C2 personal memories from witnessed events; C5 house/court rumour pool with belief confidence.

**When:** C2/C5 split.

---

## D8 — World detail level

**Default:** **Single abstract realm** (county + lordships + houses). No tile map. Travel = same court unless “away” flag for story (defer).

**Politics:** Abstract prestige, titles, claims—no battles until post-prototype.

**When:** Now.

---

## D9 — Succession law

| Option | Implications |
|--------|----------------|
| Male-preference primogeniture | Simple; CK-familiar |
| Full legal library | Scope explosion |

**Default:** **One law per house** enum: `male_preference_primogeniture`, `absolute_primogeniture`, `eldest_child` (rare). Prototype already uses male preference.

**When:** D1 milestone; document on `Title`/`House`.

---

## D10 — Marriage restrictions

**Default:** Age 16+, not close kin (sibling/parent), opposite-sex for v1 (extend later), cross-house encouraged for drama. Same-sex partnerships optional extension post-prototype.

**When:** C3.

---

## D11 — Story identification

**Default:** **Significance scoring** on events (relationship delta, title change, betrayal flags) + causal graph components. No template-required arcs.

**When:** E1.

---

## D12 — Determinism

**Default:** **Strict** for given seed and version tag. Any UI intervention breaks determinism by design (separate seed channel).

RNG: `Random(seed + day + actor_slot)` documented per module.

**When:** A3 codifies; tests enforce.

---

## D13 — LLM role

| Option | Implications |
|--------|----------------|
| None | Zero cost, full reproducibility |
| Chronicle prose polish only | Nice UX; optional |
| NPC decisions | Rejected |

**Default:** **None in Minimum Story Realm**; optional prose formatter later with template fallback.

**When:** E2 optional.

---

## D14 — Historical realism vs fun emergence

**Default:** **Plausible medieval flavour** (titles, marriage alliance pressure) over strict history sim. Laws are readable game rules, not legal history dissertation.

**When:** Now.

---

## D15 — Population 200

**Default:** Keep **200** until F3 evaluation shows story density saturates; then step to 400.

**When:** F3 measurement.

---

## Open questions (genuinely deferred)

| Question | Default working assumption | Finalise by |
|----------|---------------------------|-------------|
| Infidelity mechanics | Defer; jealousy via existing axes | Post-prototype |
| Player bookmarks / notifications | Bookmark character highlights events | F1 |
| Modding / scenario format | JSON fixture worlds | E4 |
| Combat abstraction | Prestige + scheme success rolls | D4 milestone review |

---

## Cross-references

- Architecture: [SIMULATION_ARCHITECTURE.md](./SIMULATION_ARCHITECTURE.md)
- Roadmap: [ROADMAP.md](./ROADMAP.md)
