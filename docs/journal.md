# Build journal

> One entry per work block, newest first. Each entry ends with a teaching note:
> what was built, the key design choices, and what the scientist should be able to
> explain to a conference audience.

---

## 2026-06-10 — Session 1 (in progress)

**Scope:** v0.1 from empty repo, per docs/spec.md and the goal statement.

**Done so far:**
- Environment: Python 3.13 venv on the project volume; networkx / numpy /
  matplotlib / streamlit / pytest / jupyterlab installed. Git repo initialized
  (branch `main`), full AGPL-3.0 text in `LICENSE`.
- `docs/decisions.md` written **before any engine code**: 13 PROVISIONAL modeling
  decisions (D1–D13) covering threshold distribution, innovator mass, credibility
  weights, R/W/A operationalization, update/decay scheme, broadcast mechanics,
  seeding definitions, informal-layer generator, dead-pocket and pivot-node
  definitions, tenure inertness. **These are the items awaiting your arbitration.**
- `docs/limitations.md` seeded (spec §6 requires it from W1).

**Engineering notes (non-scientific, builder's discretion):**
- Scenario configs use TOML via stdlib `tomllib`, not YAML: the hard stack
  constraint is "NetworkX + NumPy + Streamlit only" and PyYAML would be a fourth
  runtime dependency; TOML gives identical readability at zero dependency cost.
  The spec's "YAML config per scenario" is treated as "human-readable config file
  per scenario". Flag if you disagree.
- Matplotlib/Jupyter/pytest are toolchain (spec §3 names them), not engine
  dependencies. A unit test enforces that `core/` imports only networkx, numpy,
  and the standard library.
- Results format: CSV + a JSON metadata sidecar (parameters, seed, git commit,
  library versions) per run batch. Parquet skipped (would need pyarrow).

(Entry will be completed at end of session.)
