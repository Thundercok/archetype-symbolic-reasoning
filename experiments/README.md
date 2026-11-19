# Experiments Directory

Reproducible experiment configurations, benchmark splits, and append-only evaluation run logs.

Directory convention:
- `configs/` — YAML/JSON experiment definitions (model, decoding config, prompt template version, seed).
- `runs/<run_id>/` — Immutable evaluation summaries, metric tables, and error breakdowns.

See [docs/RESEARCH_PLAN.md](../docs/RESEARCH_PLAN.md) for the experimental protocol.
