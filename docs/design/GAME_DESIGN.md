# KingGame — Game Design

**Product:** KingGame  
**Genre:** Dynastic life simulation / emergent history observer  
**Inspiration:** Crusader Kings III (character drama and families), not its map scale  
**Companion docs:** [SIMULATION_ARCHITECTURE.md](./SIMULATION_ARCHITECTURE.md) · [ROADMAP.md](./ROADMAP.md) · [DECISIONS.md](./DECISIONS.md) · [PERSONALITY_AND_CAST.md](./PERSONALITY_AND_CAST.md)

---

## 1. Product vision

### What is KingGame?

KingGame is a **living medieval world** populated by people with personalities, relationships, ambitions, loyalties, fears, beliefs, and memories. The world advances without the player directing individuals. People court, marry, reproduce, inherit, promise, scheme, reconcile, betray, and die—each change altering someone else's circumstances, whose responses produce further consequences. Over generations, the simulation writes a history that was **not authored in advance**.

The player is an **observer with investigation tools**: follow lives, inspect motives, trace causality, and discover stories. Optional light intervention may exist later; it is not the core loop.

**Central principle:**

> The simulation creates events. Characters give those events meaning. History remembers the consequences.

The chronicle **observes** verified simulation facts. It must not invent betrayals, marriages, or deaths that did not occur.

### Non-goals (prototype and near-term)

- CK3-scale map, warfare, economy, religion simulation
- Player-as-ruler unit control or dialogue trees for every NPC
- LLM-as-game-master deciding outcomes
- Multiplayer, monetisation design, art-heavy 3D presentation

---

## 2. Design pillars and acceptance criteria

### Pillar A — People before mechanics

**Principle:** Important actions arise from circumstances, goals, personality, beliefs, relationships, and opportunities—not event tables.

**Acceptance criteria:**

- Every `EventKind` with social weight (marriage, scheme, betrayal, reconciliation) has a logged **motive record** (goal IDs, utility breakdown, or plan step) inspectable in dev tools.
- In evaluation harness, ≥90% of non-demographic events in a 50-year run link to at least one prior relationship or memory event in the causal graph (see [SIMULATION_EVALUATION.md](./SIMULATION_EVALUATION.md)).

### Pillar B — Families create continuity

**Principle:** Parentage, marriage, inheritance, obligations, and inherited grievances connect generations.

**Acceptance criteria:**

- Family graph remains consistent after 100 in-game years (no orphan house heads, no living characters with dead parents listed as sole guardians without replacement).
- At least one multi-generational chain per house in long-run fixtures: grandparent action → parent memory → child decision.

### Pillar C — Relationships are complicated

**Principle:** Affection, trust, respect, fear, resentment, envy can coexist directionally.

**Acceptance criteria:**

- Relationship model is **directed** and multi-axis; UI can show Eleanor → Robert ≠ Robert → Eleanor.
- Test fixtures demonstrate defend-in-public / undermine-in-private (high affection + high resentment).

### Pillar D — Emergence before scripting

**Principle:** Drama from system interaction; authored content may seed initial conditions only.

**Acceptance criteria:**

- No runtime dependency on scripted story templates for core loops.
- Multi-seed batch runs show divergent **event graph topology** (not just names), measured by evaluation harness.

### Pillar E — History has consequences

**Principle:** Memories, promises, reputation, and political context change future behaviour.

**Acceptance criteria:**

- Broken promise reduces trust and increases scheme probability against promiser within N days (threshold TBD after baseline metrics in Stage C).
- Dead characters' unresolved feuds still affect heirs via memories or inherited claims.

### Pillar F — The world belongs to its inhabitants

**Principle:** Simulation stays interesting when the player watches no one.

**Acceptance criteria:**

- Characters initiate socially consequential actions without player input (marriage negotiation, schemes, alliances).
- Idle 30-year headless run produces ≥1 significant story chain per house above noise floor (evaluation rubric).

### Pillar G — Understandable causality

**Principle:** Surprising outcomes remain investigable.

**Acceptance criteria:**

- Player can open any chronicle entry and walk **causes → effects** within the event graph UI (Stage E/F).
- No chronicle sentence contradicts simulation state (automated lint: summary must reference valid entity IDs).

---

## 3. Player experience

### Short session (15–30 minutes)

1. Start **Haldenmere** (or saved realm).
2. Advance time 1–5 years.
3. Scan ranked chronicle for turning points (succession, feud, marriage alliance).
4. Pick a character named in the chronicle; read relationships, memories, active plan.
5. Trace one event backward to a prior insult, promise, or marriage.

**Emotional target:** Curiosity—“I want to know what happens to Eleanor's children.”

### Long simulation (2+ hours, unattended)

1. Run 50–100 years at high speed (headless or UI).
2. Jump to Year 80; read dynasty summaries.
3. Compare house prestige, alliances, active feuds vs Year 1.

**Emotional target:** Awe at unplanned history—“The realm split because of a rumour in Year 12.”

### Multi-generational play

- Follow a **bookmark character** across their life; on death, bookmark heir or rival.
- Family tree shows marriages across houses; dynastic chronicle highlights house-level arcs.

### Observer vs intervention (default)

**Default:** Observation only (time, inspect, trace, search).

**Optional later (Stage F):** Limited god-tools—reveal a secret to one character, nudge trust ± small delta, force a council meeting. Each intervention logged as `EventKind.CUSTOM` with `player_caused: true` and excluded from achievement/stat purity runs.

See [DECISIONS.md](./DECISIONS.md) § Observer mode.

### Interface assumptions

- **No map required** for first compelling prototype. House/lordship list + relationship graph suffices.
- Streamlit → later structured web UI if needed; simulation remains headless-capable.

---

## 4. Scope and boundaries

### Population scale

| Stage | Target living population | Rationale |
|-------|-------------------------|-----------|
| Prototype (now) | ~200 | Fits one developer; dense kinship; fast iteration |
| Mature single-realm | 400–800 | Richer court politics without CK scale |
| Upper bound (same architecture) | ~2,000 | Requires performance milestone F3 |

200 is **sensible** for first compelling social prototype. Increase only after evaluation shows agents produce stories, not noise.

### Essential for first *compelling* prototype (“Minimum Story Realm”)

1. Goals + utility-based daily decisions (limited action set)
2. Directional relationships updated by interactions
3. Memories from meaningful events influencing trust and schemes
4. Motivated courtship/marriage (individual + house pressure)
5. Succession with explicit law + disputes
6. Causal event graph + ranked chronicle
7. Observer UI: character inspect, trace, basic family tree

### Mature version (not required for first prototype)

- Rumours/secrets network, factions, abstract warfare, economy pressure, religion as modifier, disease, education

### System deferral matrix

| System | Emergent social value | Recommendation |
|--------|----------------------|----------------|
| Memory & beliefs | **Critical** | Stage C (after decisions) |
| Marriage negotiation | **Critical** | Stage C |
| Succession disputes | **High** | Stage D |
| Promises/oaths | **High** | Stage D |
| Rumours | **High** | Stage C5 |
| Factions | **Medium** | Stage D4 |
| Abstract warfare | **Medium** | Post-prototype; feeds prestige only at first |
| Detailed economy | **Low early** | Defer; use house prestige scalar |
| Religion/culture | **Low early** | Defer; optional trait modifiers later |
| Procedural geography | **Low** | Defer indefinitely for core vision |
| Travel | **Low** | Abstract “court presence” first |

---

## 5. Core simulation concepts (conceptual)

Detailed mechanics live in [SIMULATION_ARCHITECTURE.md](./SIMULATION_ARCHITECTURE.md). Summary:

### Character (conceptual layers)

| Layer | Examples | Persistence |
|-------|----------|-------------|
| Facts | age, sex, parentage, house, titles, alive | Authoritative |
| Temperament | 8 core dimensions + optional tags (see [PERSONALITY_AND_CAST.md](./PERSONALITY_AND_CAST.md)) | Slow-changing |
| Emotion | anger, grief, stress | Temporary |
| Goals | gain title, protect sibling, revenge | Dynamic |
| Beliefs | “Robert plots against me” (may be false) | Subjective |
| Memories | indexed experiences | Append + decay |
| Relationships | directed axes + legal states (marriage, ward) | Mixed |
| Plans | multi-step intentions | Ephemeral |

### Decision loop (target)

Per character per tick (or staggered cohorts):

1. **Perceive** local world slice (kin, court, liege, rivals).
2. **Update** emotions and goal priorities from memories.
3. **Propose** actions from plan or utility scan.
4. **Resolve** conflicts (two schemes targeting same title).
5. **Apply** effects → relationships, memories, world facts.
6. **Log** events with causes.

### Social action set (staged)

**Phase 1 (existing):** demographic lifecycle only.

**Minimum Story Realm action set:**

- `court`, `propose_marriage`, `accept/refuse_marriage`, `make_promise`, `break_promise`, `offer_favor`, `spread_rumour`, `reconcile`, `scheme_claim`, `support_heir`, `public_insult`, `private_apology`

Warfare actions deferred.

### Marriage (target behaviour)

Negotiation involves: eligibility, house prestige delta, personal attraction, autonomy vs family pressure, existing lovers (optional later). Outcome creates **legal** marriage state; does not auto-max affection or alliance loyalty.

### Succession (minimum viable)

Start with **male-preference primogeniture** among legitimate children, configurable per house; female inheritance when no male heirs. Disputes via **claim** objects + scheme actions, not instant war.

---

## 6. Emergent story presentation

**Simulation** produces events. **Narrative layer** ranks, clusters, and explains.

- **Significance score** from: relationship delta magnitude, title change, unexpected reversal, feud escalation, dynasty firsts.
- **Story chain:** connected component in causal graph above score threshold.
- **Biography:** chronological filter of events where `actor_id` or `target_id` = character.

Templates may format prose; they must not change facts.

Noise control: suppress routine births/deaths unless dynasty-relevant; batch low-significance relationship ticks.

---

## 7. Smallest prototype that demonstrates the vision

**“Eleanor's succession” fixture:** 3 houses, 40 characters, scripted *initial* positions only (father dead, sister vs brother, neighbouring lord). Run 20 years with full B+C milestones.

**Success:** Chronicle narrates a dispute where sister's marriage alliance and a rumour contribute to a succession crisis **without** hard-coded outcome; player traces ≥3 causal links.

Current codebase is **Stage A** only; this fixture is the north-star acceptance test for Minimum Story Realm.

---

## 8. Naming

**KingGame** = product and repository name. **Chronicle** = in-world historical record and observer UI name. Code package rename is optional cleanup (see [DECISIONS.md](./DECISIONS.md)).

---

## Cross-references

- Implementation status: [CURRENT_STATE_AUDIT.md](./CURRENT_STATE_AUDIT.md)
- Milestones: [ROADMAP.md](./ROADMAP.md)
- Evaluation: [SIMULATION_EVALUATION.md](./SIMULATION_EVALUATION.md)
