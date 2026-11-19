# Developer & Researcher Guide

This guide documents the engineering standards, architectural invariants, and experimental rules for `archetype-symbolic-reasoning`.

---

## 1. Environment Setup

This project uses `uv` with Python 3.12+.

```bash
# Sync dependencies and create .venv
uv sync

# Run all unit and invariant tests
uv run pytest

# Check formatting and lint rules
uv run ruff check src tests
```

---

## 2. Architectural Boundaries (Strict Separation)

To preserve scientific validity, the codebase enforces a strict boundary between **deterministic symbolic computation** and **stochastic neural inference**:

1. **`src/archetype_symbolic/core/` (Pure Deterministic Layer)**
   - **Rule:** ZERO network calls, ZERO LLM calls, ZERO randomness (unless an explicit seed is passed for simulation helpers).
   - Every function must be deterministic, typed, and verified by unit/property tests in `tests/`.
   - Outputs must be serializable to canonical JSON so evaluators can compare model outputs against ground truth unambiguously.

2. **`corpus/` (Canonical Ground-Truth Layer)**
   - Every text file or JSON table MUST declare its provenance (source edition, translation/commentary lineage, license/public-domain status).
   - Never mix AI-paraphrased summaries into canonical primary-source fields. Keep primary texts and commentaries cleanly separated.

3. **`src/archetype_symbolic/eval/` (Verification & Metrics Layer)**
   - Implements objective graders for `State Accuracy`, `Constraint Violation Rate (CVR)`, and `Canonical Citation Precision (CCP)`.
   - Never rely solely on LLM-as-a-Judge when a programmatic verifier can check the invariant directly.

4. **`experiments/` (Reproducible Runs)**
   - Every experiment run must record: model identifier, temperature/decoding parameters, prompt template hash, dataset split version, git commit SHA, and timestamp.
   - Never edit or cherry-pick raw run outputs; treat `experiments/runs/` as append-only evidence.

---

## 3. Contract for Adding a New Symbolic System

Before adding a new system (e.g., *Zi Wei Dou Shu*, *Tarot*, *Numerology*), implement and verify all four components:

1. **Formal State Representation:** Explicit immutable dataclass/schema representing the discrete state space $\mathcal{X}$.
2. **Deterministic Operators:** Pure transition functions $\mathcal{T}$ and structural constraint checkers $\mathcal{C}$.
3. **Invariant Test Suite:** Automated tests in `tests/` verifying bijections, symmetries, boundary dates/cases, and known canonical reference examples.
4. **Canonical Corpus Entry:** Verified lookup table under `corpus/<system_name>/` with explicit provenance metadata.

---

## 4. Academic Integrity & Reproducibility Checklist

Before citing any number in `README.md`, reports, or manuscripts:
- [ ] All baselines (`B0`, `B1`, `B2`) and the grounded method (`M1`) ran on the exact same benchmark split.
- [ ] Decoding parameters, prompts, and compute budgets are matched and logged.
- [ ] No ground-truth answers or canonical texts leaked into raw-LLM baseline prompts.
- [ ] Both aggregate metrics and failure-mode error analyses are documented.
- [ ] Tests (`uv run pytest`) and linter (`uv run ruff check src tests`) pass cleanly.
