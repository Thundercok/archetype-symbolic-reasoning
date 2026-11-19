# Research Plan: Neuro-Symbolic Reasoning over Formal Archetypal Systems

## 1. Motivation & Research Gap

Modern LLMs exhibit strong surface fluency on cultural and esoteric topics (e.g., *I Ching*, *Zi Wei Dou Shu*, *Tarot*), yet their underlying symbolic computation is frequently unfaithful:
- They conflate hexagram indices (King Wen sequence vs. binary encoding) or miscompute transformed (*Biến Quái*) and nuclear (*Hỗ Quái*) states.
- They assert relational properties (e.g., *Ngũ Hành* elemental interactions or line positions) that directly contradict the state they just generated.
- They fabricate or cross-attribute canonical passages (e.g., citing the text of Hexagram 14 Line 3 while discussing Hexagram 14 Line 5).

Unlike standard math benchmarks (e.g., GSM8K), classical formal symbolic systems combine **strict discrete state transitions**, **non-Western combinatorial constraints**, and **canonical textual grounding** in a domain with high memorization temptation and low formal tooling coverage.

---

## 2. Core Research Questions & Falsifiable Hypotheses

- **RQ1 (Symbolic Faithfulness):** How accurately do frontier and open-weight LLMs track exact multi-step discrete states and structural constraints in formal archetypal systems without external symbolic tools?
  - **H1:** Raw LLMs (Zero-shot and Few-shot CoT) will exhibit steep accuracy degradation as derivation depth increases (e.g., base hexagram $\to$ changing lines $\to$ transformed + nuclear + mutual hexagrams + elemental constraints), with State Accuracy dropping substantially below 50% on multi-hop compositional tasks.
  - *Disconfirmation criterion:* If raw LLMs achieve $>90\%$ exact State Accuracy and $<5\%$ CVR on multi-hop compositional derivations (including counterfactual/renamed symbol probes), then the symbolic bottleneck is already solved by parametric memory alone.

- **RQ2 (Grounding vs. Retrieval):** Does deterministic symbolic grounding (exact state + constraint graph verification) outperform standard text-only RAG in reducing Constraint Violation Rate (CVR) and improving Canonical Citation Precision (CCP)?
  - **H2:** Text-only RAG improves CCP over raw LLMs but fails to eliminate CVR on multi-step state derivations because retrieval keys depend on accurate intermediate state computation. Neuro-symbolic grounding (deterministic solver + verifier-gated generation) will reduce CVR to near-zero while maximizing CCP.
  - *Disconfirmation criterion:* If standard RAG matches neuro-symbolic grounding within statistical noise ($p > 0.05$) on both CVR and CCP across multi-hop queries.

- **RQ3 (Counterfactual / Anti-Contamination Test):** Are LLM errors caused by reasoning failure or memorization conflict?
  - **H3:** Under isomorphic symbol relabeling (preserving the mathematical structure of $\mathbb{Z}_2^6$ and $\mathcal{C}$ while permuting labels), raw LLM performance will collapse, whereas the neuro-symbolic pipeline remains invariant.

---

## 3. Experimental Conditions (Baselines vs. Proposed Method)

All conditions are evaluated on the exact same held-out problem suite with fixed random seeds and matched token/compute budgets:

| Condition | Symbolic Engine | Canonical Corpus Access | Constraint Verifier |
|:---|:---|:---|:---|
| `B0: Zero-Shot LLM` | None | Parametric only | None |
| `B1: Few-Shot CoT` | None | Parametric + $k$-shot examples | None |
| `B2: RAG-Only` | None | Dense/BM25 retrieval over `corpus/` | None |
| `M1: Neuro-Symbolic Grounded` | Deterministic oracle (`core/`) | Exact state-indexed lookup $\mathcal{K}(x^*)$ | Automated post-hoc / guided verifier |

---

## 4. Metrics & Statistical Rigor

1. **State Accuracy ($\text{Acc}_{\text{state}}$):** Exact match over structured JSON state outputs (primary hexagram, transformed hexagram, nuclear hexagram, moving line indices, derived elemental relations).
2. **Constraint Violation Rate ($\text{CVR}$):** Automated programmatic check of extracted assertions against the deterministic constraint graph $\mathcal{C}(x^*)$, supplemented by a human-audited calibration subset (reporting inter-annotator Cohen's $\kappa$).
3. **Canonical Citation Precision ($\text{CCP}$):** Exact / normalized-span verification of quoted or referenced canonical lines against the provenance-tracked ground-truth corpus.
4. **Statistical Testing:** Paired comparisons across identical test instances using McNemar's test (binary exact match) and paired bootstrap / Wilcoxon signed-rank tests (continuous rates), with confidence intervals and effect sizes reported.

---

## 5. Phase 1 Concrete Milestone (I Ching Testbed)

Before expanding to *Zi Wei Dou Shu*, *Tarot*, or *Numerology*, Phase 1 must complete and verify:
1. Pure deterministic I Ching engine (`core/iching.py`) with 100% unit-test coverage of algebraic invariants (King Wen mapping, trigram decomposition, nuclear/inverted/opposite transformations, moving lines, Five-Element bindings).
2. Clean, provenance-verified canonical corpus (`corpus/iching/`) with explicit edition metadata.
3. Benchmark task suite covering 4 difficulty tiers (Single-state lookup, Multi-step state transformation, Constraint consistency check, Isomorphic symbol-permutation probe).
4. Pilot baseline run (`B0`, `B1`, `B2`, `M1`) with full raw logs saved under `experiments/`.
