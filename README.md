# Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)

[![Live Demo](https://img.shields.io/badge/Interactive_Explorer-420_Live_Traces-00b4d8.svg)](https://hammamnm.github.io/reasoning-debugger/)
[![Preprint](https://img.shields.io/badge/Manuscript-PDF_Available-b31b1b.svg)](PAPER_MANUSCRIPT_V1.pdf)
[![Benchmark](https://img.shields.io/badge/Clinical_Specs-50_Emergency_Scenarios-blue.svg)](CLINICAL_SPECIFICATIONS.md)
[![Evaluations](https://img.shields.io/badge/Live_Audit-420_Paired_Traces-success.svg)](study_v1/results/)
[![Tag](https://img.shields.io/badge/Frozen_Release-v0.2--frozen--rules-orange.svg)](https://github.com/HammamNM/reasoning-debugger/releases/tag/v0.2-frozen-rules)

> **Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure**  
> **Author:** Hammam Omer (Faculty of Medicine, Omdurman Islamic University | NexoraMed)  
> 📄 **[Download Full Academic Manuscript (PDF)](https://raw.githubusercontent.com/HammamNM/reasoning-debugger/main/PAPER_MANUSCRIPT_V1.pdf)** | **[View PDF on GitHub](https://github.com/HammamNM/reasoning-debugger/blob/main/PAPER_MANUSCRIPT_V1.pdf)** | **[Read Full Markdown Manuscript](PAPER_MANUSCRIPT_V1.md)**

---

## 1. Overview & Architectural Philosophy

Automated safety evaluation of open-ended clinical management plans faces a fundamental methodological dilemma: **unconstrained `LLM-as-a-Judge` evaluators** are vulnerable to *surface-fluency masking* (passing authoritative prose that silently omits life-saving interventions), whereas **untyped lexical keyword matchers** suffer from catastrophic false-alarm rates by penalizing clinicians who explicitly document contraindicated actions in order to refuse them.

This repository contains the core **Reasoning Debugger Kernel** and the **Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)**, which strictly decouples semantic extraction from clinical safety adjudication across two isolated stages:

```text
[ Clinical Case Vignette (Neutral V_0 or Pressured V_p) ]
                           |
                           v
+-------------------------------------------------------+
| Subject Clinical LLM Generator                        |
| (OpenAI / Google Gemini-Gemma / Alibaba Qwen)         |
+-------------------------------------------------------+
                           |  Unstructured Free-Text Plan (R)
                           v
===========================================================================
STAGE I: CONSTRAINED NEURAL-TO-SYMBOLIC EXTRACTION & VERBATIM GATE
(`clinical_auditor/trace_extraction/extractor.py`)
===========================================================================
| 1. Constrained Canonical Event Parser                                   |
|    - Maps spans strictly to closed 22-Action Clinical Ontology (A)      |
|    - Assigns Assertion Polarity: PROPOSED | NEGATED | SUSPECTED         |
|    - Extracts character-level `source_span` pointers                    |
|                                                                         |
| 2. Deterministic Verbatim Substring Gate                                |
|    - Enforces: norm(e_i.source_span) in norm(R)                         |
|    - Quarantines any hallucinated/paraphrased extraction                |
|    - Live Audit Verification: 1,767/1,767 verified (0 hallucinations)   |
===========================================================================
                           |  Verified Chronological Trace T = <e_1, ..., e_k>
                           v
===========================================================================
STAGE II: THREE-LAYER DETERMINISTIC CLINICAL VERIFICATION (PURE PYTHON)
(`orchestrator/unified_audit.py` & `kernel/`)
===========================================================================
| - LAYER 1 (V_state): State Integrity & Assertion-Aware Gate             |
|   * Mandatory Omissions (must_include): Action must be in P(T)          |
|   * Contraindications (must_avoid): Flagged ONLY if PROPOSED in P(T);   |
|     NEGATED safety precautions in N(T) are deterministically rescued.   |
| - LAYER 2 (V_temp): Temporal Prerequisite Ordering Engine               |
|   * Enforces strict chronological index ordering: idx(a_req) < idx(a_t) |
| - LAYER 3 (V_epist): Epistemic Humility & Premature Closure Guard       |
|   * Blocks DEFINITIVE benign closure prior to mandatory rule-outs.      |
===========================================================================
                           |
                           v
+-------------------------------------------------------+
| UNIFIED DETERMINISTIC AUDIT REPORT                    |
| - Binary Verdict: PASS (V_total = empty) or FAIL      |
| - Exact Violation Attribution (<2ms local CPU time)   |
+-------------------------------------------------------+
```

---

## 2. Key Empirical Findings (N=35 Held-Out Test Split; 420 Paired Evaluations)

1. **Pervasive Blindness of Standalone `LLM-as-a-Judge`:** Across 53 criterion-unsafe clinical management plans, a standalone `LLM-as-a-Judge` evaluator missed **38/53 unsafe responses (71.7% False-Pass Rate; 95% Wilson CI: 58.4%–82.0%)**, including **100% of failures (27/27)** produced by fluent flagship/large generators (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `gemma-4-26b-a4b-it`, and `gemini-3.5-flash-lite`).
2. **Elimination of Lexical False Alarms via Assertion Gating:** An untyped lexical keyword matcher incurred a **48.2% false-alarm rate (177/367; specificity 51.8%)** because safe clinicians explicitly mention contraindicated drugs and premature dispositions to withhold them. Our Stage I **Canonical Assertion/Negation Gate** (`PROPOSED` vs. `NEGATED`) with **Verbatim Substring Verification** (`0/1,767` hallucinated events) eliminated all 177 false alarms (**100.0% specificity, 100.0% criterion recall**).
3. **Divergent Behavioral Shifts Under Collegial Pressure:** Under wrongful collegial pressure ($N=24$), `qwen/qwen3.8-27b` (`87.5% -> 75.0%`) and sparse MoE `gemma-4-26b-a4b-it` (`91.7% -> 83.3%`) exhibited net adverse compliance (sycophantic shifts), whereas `openai/gpt-oss-120b` (`91.7% -> 95.8%`) and `gemini-3.5/3.1-flash-lite` exhibited zero sycophantic collapses (`b=0`) and cue-triggered precautionary shifts. Under rightful clinical hints ($N=11$), all six models improved or maintained 100% safety, with compact `openai/gpt-oss-20b` surging from `36.4%` to `81.8%`.

---

## 3. Controlled Architectural Ablation & Multi-Ecosystem Benchmark

### Table A: 6-Tier Architectural Ablation Across 420 Live Clinical Evaluations (53 Criterion-Unsafe, 367 Criterion-Safe)

| Evaluation Method / Controlled Ablation Tier | Defect Detection Recall / Sensitivity (95% CI) | Specificity on Safe Traces (95% CI) | False-Alarm Rate (FP / 367) | Youden's $J$ |
| :--- | :---: | :---: | :---: | :---: |
| **1. Standalone `LLM-as-a-Judge` Baseline** | 15/53 (**28.3%** [18.0–41.6]) | 360/367 (98.1% [96.1–99.1]) | 7/367 (1.9%) | 0.264 |
| **2. Untyped Lexical Matcher (No Negation)** | 46/53 (86.8% [75.2–93.5]) | 190/367 (**51.8%** [46.7–56.8]) | **177/367 (48.2%)** | 0.386 |
| **3. Hybrid Ablation: Omission Rules Only ($V_{omit}$)** | 49/53 (92.5% [82.1–97.0]) | 367/367 (100.0% [99.0–100.0]) | 0/367 (0.0%) | 0.925 |
| **4. Hybrid Ablation: Post-Extractor ($P(T)$ Filtered)** | 53/53 (100.0% [93.2–100.0]) | 367/367 (100.0% [99.0–100.0]) | 0/367 (0.0%) | 1.000 |
| **5. Hybrid Ablation: Layer 1 State + Assertion ($V_{state}$)** | 53/53 (100.0% [93.2–100.0]) | 367/367 (100.0% [99.0–100.0]) | 0/367 (0.0%) | 1.000 |
| **6. Full Hybrid Auditor (Layers 1+2+3; `v0.2-frozen`)** | **53/53 (100.0% [93.2–100.0])** | **367/367 (100.0% [99.0–100.0])** | **0/367 (0.0%)** | **1.000** |

### Table B: Multi-Ecosystem Held-Out Test Split Performance ($N=35$ Scenarios; 70 Paired Evaluations per Model)

| Model Name | Ecosystem & Paradigm | Wrongful Traps: Neutral -> Pressured ($N=24$) | Rightful Hints: Neutral -> Pressured ($N=11$) | Total Unsafe (/70) | Judge False-Pass Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`openai/gpt-oss-120b`** | OpenAI Dense (120B) | 91.7% -> **95.8%** (+4.1%) | 90.9% -> **100.0%** (+9.1%) | 4/70 (5.7%) | **4/4 (100% missed)** |
| **`gemini-3.1-flash-lite`** | Google Commercial | 87.5% -> **95.8%** (+8.3%) | 90.9% -> **100.0%** (+9.1%) | 5/70 (7.1%) | 4/5 (80% missed) |
| **`gemini-3.5-flash-lite`** | Google Commercial | 87.5% -> 91.7% (+4.2%) | 90.9% -> **100.0%** (+9.1%) | 6/70 (8.6%) | **6/6 (100% missed)** |
| **`gemma-4-26b-a4b-it`** | Google Sparse MoE (26B/4B) | **91.7%** -> 83.3% (-8.4%) | **100.0%** -> **100.0%** (0.0%) | 6/70 (8.6%) | **6/6 (100% missed)** |
| **`qwen/qwen3.8-27b`** | Alibaba Dense (27B) | 87.5% -> 75.0% (-12.5%) | 81.8% -> **100.0%** (+18.2%) | 11/70 (15.7%) | **11/11 (100% missed)** |
| **`openai/gpt-oss-20b`** | OpenAI Compact (20B) | 70.8% -> 79.2% (+8.4%) | 36.4% -> 81.8% (+45.4%) | 21/70 (30.0%) | 7/21 (33.3% missed) |

---

## 4. Repository Structure & Core Modules

* **`clinical_auditor/`**: Stage I neural-to-symbolic trace extraction (`clinical_auditor/trace_extraction/extractor.py`), canonical 22-action ontology mapping, and the deterministic **Verbatim Substring Verification Gate**.
* **`orchestrator/`**: Stage II deterministic verification engine (`orchestrator/unified_audit.py`) integrating state integrity, temporal prerequisites, and epistemic closure guards.
* **`kernel/` & `analytics/`**: Domain-independent **Reasoning Debugger Kernel** (`kernel/debugger.py`, `kernel/structural_failure_detector.py`, `analytics/anchoring_detector.py`, `analytics/premature_closure_detector.py`) for structured reasoning graph representation and cognitive bias localization.
* **`study_v1/`**: Complete benchmark specifications (`SCEN_01`–`SCEN_50`), held-out test runner (`study_v1/run_live_test_evaluation.py`), raw audit logs (`study_v1/results/`), statistical verification scripts, and manuscript sources.
* **`tests/`**: Comprehensive contract, boundary, and regression test suites covering reasoning kernel isolation and clinical auditing layers.

---

## 5. Reproducibility & Verification Quickstart

All 420 raw evaluation traces, frozen rule specifications, and statistical outputs are stored in `study_v1/results/` and can be deterministically verified offline without API keys:

```bash
# 1. Reproduce Wilson 95% CIs, exact two-sided McNemar tests, and model performance tables
python study_v1/run_statistical_analysis.py

# 2. Reproduce the 6-tier controlled architectural ablation study (Table 4)
python study_v1/run_true_ablation.py

# 3. Verify benchmark integrity and run unit/contract test suites
python study_v1/verify_benchmark.py
pytest
```

---

## 6. Methodological Scope & Intended Use

* **Criterion-Referenced Research Tool:** Sensitivity and specificity metrics are evaluated against the frozen criterion specifications $G_c$ (`v0.2-frozen-rules`) derived from established emergency medicine guidelines (AHA/ACC, ESC, BTS, EAST). This framework is an experimental AI safety auditing tool and is **not** a certified medical device for autonomous patient care.
* **Citation:** If you use this benchmark, architecture, or codebase in your research, please cite the accompanying manuscript (see [`CITATION.cff`](CITATION.cff) or [`PAPER_MANUSCRIPT_V1.pdf`](PAPER_MANUSCRIPT_V1.pdf)).
