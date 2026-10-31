# Hammam Omer
**Medical AI Researcher & Evaluation Engineer**  
Omdurman, Sudan | [GitHub: HammamNM](https://github.com/HammamNM) | [Interactive Audit Explorer](https://hammamnm.github.io/reasoning-debugger/) | [Repository](https://github.com/HammamNM/reasoning-debugger) | [NexoraMed](https://nexoramed.online)

---

## Professional Summary
Medical AI researcher and software builder specializing in **LLM Evaluation, Clinical Safety Benchmarking, and Neuro-Symbolic Auditing Architectures**. Designed and empirically validated a deterministic-first clinical safety auditor demonstrating the systematic blind spots of standalone *LLM-as-a-Judge* pipelines under emergency clinical pressure. Bridging clinical training with rigorous software testing, formal reasoning graph modeling, and zero-leakage benchmark engineering.

---

## Research Projects & Engineering Contributions

### 1. Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)
*Architect & Lead Researcher* | [Preprint PDF](https://github.com/HammamNM/reasoning-debugger/blob/main/PAPER_MANUSCRIPT_V1.pdf) | [Interactive Explorer](https://hammamnm.github.io/reasoning-debugger/) | [Clinical Specs](https://github.com/HammamNM/reasoning-debugger/blob/main/CLINICAL_SPECIFICATIONS.md)
* Engineered a decoupled, two-stage evaluation framework that isolates constrained semantic extraction from deterministic clinical adjudication across 420 live clinical evaluations on 6 model ecosystems (`openai/gpt-oss-120b`, `gemini-3.5/3.1-flash-lite`, `gemma-4-26b-a4b-it`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`).
* **Exposed LLM-as-a-Judge Blindness:** Empirically proved that standalone LLM judges missed **71.7% (38/53)** of safety-critical failures in emergency care (including 100% of failures from flagship models) due to surface-fluency masking.
* **Eliminated Lexical False Alarms:** Resolved the 48.2% false-alarm rate of untyped rule matchers by introducing an assertion/negation gate (`PROPOSED` vs. `NEGATED`), achieving **100.0% specificity (367/367)** and **100.0% criterion recall**.
* **Zero-Hallucination Extraction:** Designed a deterministic *Verbatim Substring Verification Gate* enforcing exact character-level grounding (`norm(span) in norm(R)`), achieving **0 hallucinations across 1,767 extracted clinical event spans**.
* **Clinical Guideline Grounding:** Formulated 50 end-to-end emergency medicine scenarios anchored directly to Class I recommendations from AHA/ACC, ESC, BTS, and EAST clinical guidelines.

### 2. Clinical Reasoning Platform & Execution Kernel
*Lead Developer & System Architect* | [Live Cloud Web App](https://hammam16.pythonanywhere.com/) | [Architecture Spec](https://github.com/HammamNM/reasoning-debugger/blob/main/ARCHITECTURE.md)
* Developed an open-source, domain-independent runtime kernel for transforming unstructured chain-of-thought traces into structured directed acyclic reasoning graphs.
* Implemented structural heuristic detectors for locating epistemic and cognitive bias patterns, including anchoring, unsupported inference, and premature diagnostic closure.
* Enforced strict contract-driven architecture with isolated runtime boundaries and automated multi-phase contract test suites (`pytest`).

---

## Technical & Research Skills

* **AI Safety & LLM Evaluation:** Multi-Ecosystem Benchmarking, LLM-as-a-Judge Failure Analysis, Behavioral Shift Detection (Sycophancy & Precautionary Shifts), Statistical Verification (Wilson 95% CI, Exact McNemar Tests, Youden's J).
* **Software Engineering & Architecture:** Python, Deterministic Parsing & Regex Verification, Neuro-Symbolic Pipelines, JSON Schema Enforcement, Git/GitHub, Linux CLI.
* **Testing & Quality Assurance:** Test-Driven Development (TDD), Boundary & Contract Testing (Pytest), Strict Data Leakage Isolation.
* **Clinical Knowledge:** Emergency Triage Protocols, ACLS/ATLS/AHA Guidelines, Diagnostic Reasoning & Clinical Workflow Auditing.

---

## Education

**Bachelor of Medicine, Bachelor of Surgery (MBBS / Candidate)**  
Faculty of Medicine, Omdurman Islamic University — Omdurman, Sudan (3rd Year)

---

## Publications & Preprints

* **Omer, H.** (2026). *Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure*. Zenodo Preprint (DOI: [10.5281/zenodo.23835945](https://doi.org/10.5281/zenodo.23835945)). Code & Live Audit Traces: `github.com/HammamNM/reasoning-debugger`.
