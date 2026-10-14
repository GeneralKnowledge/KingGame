# A2b runtime

| Scenario | Before A2b | After A2b |
|----------|------------|-----------|
| 100-year headless run (seed 0, ~200 start) | ~35 minutes (~180k living; A2 suite) | **~6.1 s** (413 living; measured on A2b branch) |
| Default `pytest` (excludes `slow`) | N/A (100y tests in default) | Under 60 seconds |

Post-regulation population (~320–413 at year 100) shrinks per-tick work versus ~180k–220k; the 100-year headless path is intended to stay under 60 seconds.
