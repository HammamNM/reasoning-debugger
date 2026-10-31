# Hammam Omer
**Medical AI Researcher, Clinical Safety Auditor & Python Systems Architect**  
Omdurman, Sudan | [GitHub: HammamNM](https://github.com/HammamNM) | [Live Audit Explorer](https://hammamnm.github.io/reasoning-debugger/) | [Cloud Platform](https://hammam16.pythonanywhere.com/) | [NexoraMed](https://nexoramed.online) | [DOI: 10.5281/zenodo.23835945](https://doi.org/10.5281/zenodo.23835945)

---

## Executive Profile
Medical AI researcher and software builder specializing in **Clinical LLM Safety Auditing, Neuro-Symbolic Verification, and Automated Reasoning Analysis**. Architect of two production open-source systems—a **Deterministic-First Hybrid Clinical Auditor** and a **Cloud Clinical Reasoning Platform**—backed by a peer-citable empirical benchmark study across 420 emergency clinical evaluations. Combines clinical medicine training with test-driven Python engineering (TDD), formal directed acyclic graph (DAG) reasoning models, and technical medical publishing.

---

## Core Engineering Systems & Research Deliverables

### 1. Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)
*Lead Architect & Sole Author* | [Interactive 420-Trace Explorer](https://hammamnm.github.io/reasoning-debugger/) | [GitHub Repo](https://github.com/HammamNM/reasoning-debugger) | [50-Scenario Clinical Specs](https://github.com/HammamNM/reasoning-debugger/blob/main/CLINICAL_SPECIFICATIONS.md)
* **Two-Stage Neuro-Symbolic Architecture:** Decoupled constrained semantic extraction (Stage I) from pure-Python deterministic clinical rule verification (Stage II) across **420 paired emergency management plans** on 6 model ecosystems (`openai/gpt-oss-120b`, `gemini-3.5/3.1-flash-lite`, `gemma-4-26b-a4b-it`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`).
* **Exposed LLM-as-a-Judge Blindness:** Empirically proved that standalone LLM judges missed **71.7% (38/53; 95% Wilson CI: 58.4%–82.0%)** of safety-critical failures—including **100% of failures (27/27)** from fluent flagship models—due to surface-fluency masking.
* **Eliminated Lexical False Alarms:** Resolved the **48.2% false-alarm rate (177/367)** of untyped keyword matchers via a canonical Assertion/Negation Gate (`PROPOSED` vs. `NEGATED`), achieving **100.0% specificity (367/367)** and **100.0% criterion recall** (`Youden's J = 1.000`) in `< 2 ms` on local CPU.
* **Zero-Hallucination Extraction Gate:** Engineered a character-level *Verbatim Substring Gate* (`norm(source_span) in norm(R)`), enforcing **0 hallucinations across 1,767 extracted clinical events**.

### 2. Clinical Reasoning Platform & Domain-Independent Execution Kernel
*Creator & System Architect* | [Live Cloud Web App (PythonAnywhere)](https://hammam16.pythonanywhere.com/) | [Kernel Architecture Spec](https://github.com/HammamNM/reasoning-debugger/blob/main/ARCHITECTURE.md) | [Source Code](https://github.com/HammamNM/reasoning-debugger/tree/main/kernel)
* **Full-Stack Cloud Reasoning Engine:** Deployed a live Python web platform (`hammam16.pythonanywhere.com`) and modular runtime kernel that transforms unstructured clinical decision flows and chain-of-thought traces into structured **Directed Acyclic Reasoning Graphs (DAGs)**.
* **Automated Cognitive Bias & Epistemic Detectors:** Built deterministic structural analyzers to detect and localize *anchoring bias*, *premature diagnostic closure*, *unsupported inference*, and *temporal prerequisite violations* (`idx(prereq) < idx(action)`).
* **Contract-Driven Software Quality:** Enforced strict API boundary isolation, schema serialization guarantees, and zero-leakage architecture verified across **30+ automated `pytest` contract suites**.

---

## Publications & Scientific Communication

* **Preprint Manuscript (Zenodo / CERN):** **Omer, H.** (2026). *Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure*. DOI: [10.5281/zenodo.23835945](https://doi.org/10.5281/zenodo.23835945).
* **Founder & Technical Author — NexoraMed ([nexoramed.online](https://nexoramed.online)):** Authoring English technical articles on Medical AI safety, clinical reasoning benchmarks, and AI integration in medical education.

---

## Technical & Clinical Arsenal

* **AI Safety & Evaluation Engineering:** Multi-Ecosystem LLM Benchmarking, LLM-as-a-Judge Failure Auditing, Sycophancy & Precautionary Shift Analysis, Automated Rubric Engineering, Statistical Verification (Wilson 95% CIs, Exact McNemar Tests, 6-Tier Ablation Design).
* **Software & Systems Engineering:** Python (OOP, Type-Safe Schemas, Web Deployment, REST APIs), Neuro-Symbolic Pipelines, Deterministic Substring & Regex Engines, JSON Schema Constrained Decoding, Pytest TDD, Git/GitHub, Linux CLI.
* **Clinical Domain Grounding:** Emergency Medicine Resuscitation & Triage Protocols, Class I Guideline Interpretation (AHA/ACC, ESC, BTS, EAST, Surviving Sepsis Campaign), Differential Diagnosis & Contraindication Auditing.

---

## Education

**Bachelor of Medicine, Bachelor of Surgery (MBBS Candidate — 3rd Year)**  
Faculty of Medicine, Omdurman Islamic University — Omdurman, Sudan (Ongoing, 2026)
