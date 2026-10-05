# Changelog

All meaningful changes to the project are recorded here. Dates use
ISO format. Commit hashes are filled after each commit.

## 2026-10-05 — Phase 0: Project Initialization

### Added

- `README.md` (English) with Persian documentation link at the top.
- `README_FA.md` (Persian documentation).
- `docs/STRATEGY_SPEC.md` — formal Strategy Specification v1.0.
- `docs/PARAMETER_REGISTRY.md` — all 32 parameters with values and
  FIXED/INITIAL/OPTIMIZABLE/DERIVED classifications.
- `docs/ARCHITECTURE.md` — system architecture, data flow, timezone
  model, no-look-ahead contract, MQL5 indicator contract.
- `HANDOFF.md`, `ROADMAP.md`, `CHANGELOG.md`, `EXPERIMENT_LOG.md`,
  `DECISION_LOG.md`, `ASSUMPTIONS.md`.
- `data/` and `results/` placeholder directories.
- `.gitignore`.

### Changed

- Nothing (initial commit).

### Fixed

- Nothing.

### Research

- Strategy v1.0 specification frozen. No parameter has been optimized.
- Baseline parameters recorded in the registry as the control
  experiment.

### Decisions

- MQL5 indicator is the Phase 1 deliverable; no EA in v1.0.
- Python `engine/` is the canonical research layer.
- Input data timestamps are assumed UTC.
- Same-bar SL/TP ambiguity resolves conservatively (SL first).

### Commit

- `phase-00: project initialization and documentation skeleton`
  (hash filled at commit time)

### Environment Verified

- Python 3.10.12; pytest 9.1.1; git 2.34.1; GitHub SSH push
  access confirmed.
