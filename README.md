# `archetype-symbolic-reasoning`: Neuro-Symbolic Grounding over Formal Archetypal Systems

An independent Python toolkit and research repository for **deterministic symbolic computation, constraint verification, and canonical grounding** over selected classical symbolic systems. It can be used directly as a Python package or exposed to external agents through its MCP server.

Rather than treating symbolic frameworks as free-form generative prose, the implemented engines represent selected systems—currently I Ching, Tarot, and Lenormand—with explicit deterministic operations and structured outputs. The broader research plan includes additional systems such as Zi Wei Dou Shu and Numerology; those planned phases should not be mistaken for completed implementations. The package provides a deterministic layer that an LLM or other client can call and verify.

---

## Contents

- [Implemented Scope & Problem Formulation](#1-implemented-scope--problem-formulation)
- [Research Roadmap & Implementation Status](#2-research-roadmap--implementation-status)
- [Repository Structure](#3-repository-structure)
- [Installation & Standalone Use](#4-installation--standalone-use)
- [MCP Integration](#5-mcp-integration)

---

## 1. Implemented Scope & Problem Formulation

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

## 2. Research Roadmap & Implementation Status

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
│       ├── core/           # Pure deterministic engines (iching, tarot, lenormand)
│       ├── eval/           # Automated verifiers & metrics (State Acc, CVR, CCP)
│       └── mcp_server.py   # Zero-dependency MCP stdio JSON-RPC 2.0 server
├── corpus/                 # Versioned, provenance-tracked canonical texts & mappings
├── experiments/            # Reproducible experiment configs, seeds, and logged outputs
├── tests/                  # Unit & algebraic invariant tests (core + MCP server)
├── pyproject.toml          # uv-managed Python 3.12+ environment
└── LICENSE                 # MIT License
```

---

## 4. Installation & Standalone Use

```bash
# Clone and enter the repository
git clone https://github.com/Thundercok/archetype-symbolic-reasoning.git
cd archetype-symbolic-reasoning

# Install the project and development tools
uv sync

# Run tests and lint checks
uv run pytest
uv run ruff check src tests
```

The core package has no runtime dependencies declared in `pyproject.toml`. The `uv` development environment installs the test and lint tools.

### Use as a Python package

After `uv sync`, import the deterministic functions directly:

```python
from archetype_symbolic.core import analyze_hexagram, draw_tarot

# Six binary lines, ordered bottom-to-top.
state = analyze_hexagram(lines=[1, 0, 1, 0, 1, 0], changing_lines=[])
print(state)

# Seeded draw for reproducible experiments.
cards = draw_tarot(count=3, allow_reversed=True, seed=42)
print(cards)
```

The core functions can be called without starting an LLM, desktop app, RAT, or network service.

---

## 5. MCP Integration

The repository includes a zero-dependency stdio MCP server. Start it from the cloned repository:

```bash
uv run archetype-mcp
```

Example client configuration (adjust the absolute path to your local clone):

```json
{
  "mcpServers": {
    "archetype-symbolic-reasoning": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/archetype-symbolic-reasoning",
        "archetype-mcp"
      ]
    }
  }
}
```

The server exposes tools for parsing and verifying Tarot spreads, drawing Tarot and Lenormand cards, casting I Ching, and analyzing/verifying I Ching states. It uses stdio; do not print logs or other text to stdout in an MCP client process.

### Optional RAT integration

The package declares a `rat.plugins` entry point for its Divination ToolPack. This is an optional adapter: the symbolic core remains usable without RAT, and RAT is not a dependency of the core package. To enable the adapter, install this project into the same Python environment as a compatible RAT installation and enable the plugin in RAT. The plugin manifest currently defaults to disabled. The MCP server remains the more general integration route for other MCP-compatible clients.

For full experimental methodology and contribution standards, see [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) and [docs/GUIDE.md](docs/GUIDE.md).
