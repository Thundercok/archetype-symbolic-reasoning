# `archetype-symbolic-reasoning`: Neuro-Symbolic Grounding over Formal Archetypal Systems

Research repository investigating **neuro-symbolic state tracking, constraint satisfaction, and canonical grounding** for Large Language Models (LLMs) operating over non-Western and classical formal symbolic systems.

Rather than treating metaphysical frameworks (*I Ching / Kinh Dịch*, *Zi Wei Dou Shu / Tử Vi*, *Tarot*, *Numerology*) as free-form generative prose, this project models them as **deterministic discrete state spaces** paired with **structured constraint graphs** and **canonical textual corpora**. This yields a rigorous, low-contamination benchmark for testing whether LLMs perform genuine symbolic state manipulation or rely on memorized surface patterns.

---

## 1. Problem Formulation

Let a formal symbolic system be defined as a tuple $\mathcal{S} = (\mathcal{X}, \mathcal{T}, \mathcal{C}, \mathcal{K})$ where:

- $\mathcal{X}$ is a finite discrete state space (e.g., $\mathbb{Z}_2^6$ for the 64 *I Ching* hexagrams, or a 12-palace star assignment lattice for *Zi Wei Dou Shu*).
- $\mathcal{T}: \mathcal{X} \times \mathcal{A} \to \mathcal{X}$ is a deterministic state-transition operator (e.g., changing-line bit-flip, nuclear hexagram extraction *Hỗ Quái*, or *Can–Chi* lunisolar calendrical projection).
- $\mathcal{C}$ is a set of hard structural invariants and relational constraints (e.g., Five-Element *Ngũ Hành* generation/overcoming cycles, Six-Line *Lục Thân* / *Thế–Ứng* bindings, or upright/reversed spread positional rules).
- $\mathcal{K}: \mathcal{X} \to \mathcal{D}$ maps canonical states to verified primary-source textual passages.

Given an input specification $q$, a model must produce both a symbolic derivation $\hat{x} \in \mathcal{X}$ and a grounded synthesis $\hat{y}$. We evaluate neural vs. neuro-symbolic systems across three quantitative axes:

1. **State Accuracy ($\text{Acc}_{\text{state}}$):** Exact combinatorial match between predicted state $\hat{x}$ (including transitions and derived invariants) and the deterministic oracle $x^*$.
2. **Constraint Violation Rate ($\text{CVR}$):** Fraction of generated reasoning steps or assertions that contradict hard structural constraints $c \in \mathcal{C}(x^*)$.
3. **Canonical Citation Precision ($\text{CCP}$):** Fraction of attributed classical passages/rules in $\hat{y}$ that verifiably match $\mathcal{K}(x^*)$ without fabrication or cross-state conflation.

---

## 2. Research Roadmap

| Phase | Symbolic System | Formal Structure | Primary Research Focus | Status |
|:---|:---|:---|:---|:---|
| **Phase 1** | **I Ching (*Kinh Dịch*)** | 6-bit Boolean lattice ($\mathbb{Z}_2^6$), 64 states, 384 lines, $O(2^6)$ transitions | Deterministic kernel + Baseline vs. Grounded LLM evaluation | Active |
| **Phase 2** | **Zi Wei Dou Shu (*Tử Vi*)** | Lunisolar calendar bijection + 12-palace combinatorial star graph | Multi-step constraint propagation & relational consistency | Planned |
| **Phase 3** | **Tarot & Numerology** | Directed spread graphs + modular arithmetic reduction | Cross-ontology alignment & counterfactual consistency | Planned |

---

## 3. Repository Structure

```text
archetype-symbolic-reasoning/
├── docs/
│   ├── RESEARCH_PLAN.md    # Hypotheses, falsification criteria, experimental protocol
│   └── GUIDE.md            # Development, corpus curation, and benchmarking guide
├── src/
│   └── archetype_symbolic/
│       ├── core/           # Pure deterministic symbolic engines (zero LLM calls)
│       └── eval/           # Automated verifiers, metrics (State Acc, CVR, CCP), runners
├── corpus/                 # Versioned, provenance-tracked canonical texts & mappings
├── experiments/            # Reproducible experiment configs, seeds, and logged outputs
├── tests/                  # Unit & property-based tests for symbolic invariants
├── pyproject.toml          # uv-managed Python 3.12+ environment
└── LICENSE                 # MIT License
```

---

## 4. Quickstart

```bash
# Install dependencies via uv
uv sync

# Run unit tests & invariant checks
uv run pytest

# Lint codebase
uv run ruff check src tests
```

For full experimental methodology and contribution standards, see [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) and [docs/GUIDE.md](docs/GUIDE.md).
