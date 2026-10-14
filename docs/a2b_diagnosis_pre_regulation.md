# A2b task 1 — pre-regulation diagnosis (seed 0, 100 years)

Run: `python3 -m chronicle.run --seeds 0 --years 100 --stats`

## Why population grew ~1000× (180k–220k from ~200)

The lifecycle model before A2b regulation combines:

1. **High effective fertility** — every 30 days each married woman aged 18–42 has an **8% independent chance** of birth (~12 rolls/year → ~0.96 expected births/woman/year if always eligible; many cohorts overlap because infant/child death is negligible).
2. **Very low adult mortality** — daily death probability 0.00005 under age 40 (~1.8%/year), so almost all adults survive to reproduce for decades.
3. **No density feedback** — births and marriages do not slow as the realm fills.
4. **Compound generations** — with ~200 starters, hundreds of marriageable singles each fortnight, and cross-house pairing, marriage throughput scales with population; each generation adds net positive births.

Over 100 years this is exponential growth with a weak death ceiling, not a stable small-realm equilibrium.

## Why seeds 0–9 cluster (180k–220k)

- Identical rules and similar **starting structure** from `generate_world` (same population target, same algorithms).
- **Deterministic RNG** via `derive_rng` — no per-seed rate parameters; differences come only from initial layout and stochastic paths.
- Large-N dynamics **wash out** seed-specific early noise; all runs hit the same unconstrained growth regime.

## Hidden counter / accounting bug?

Invariant checks and save/load equality tests pass; births/deaths are event-logged. The ballooning matches the stated 8%/month × low death arithmetic — **not** an ID or double-count bug.

See CLI `--stats` output on this branch (pre task 2–4) for measured births, deaths, marriage rates, and infant mortality share.
