# Hammam Omer
**Medical Student | Medical AI Research & Systems Engineering**  
Omdurman, Sudan | Email: [hammamomer304@gmail.com](mailto:hammamomer304@gmail.com) | [GitHub: HammamNM](https://github.com/HammamNM) | [Live Audit Explorer](https://hammamnm.github.io/reasoning-debugger/) | [Cloud Platform](https://hammam16.pythonanywhere.com/) | [NexoraMed](https://nexoramed.online) | [DOI: 10.5281/zenodo.23835945](https://doi.org/10.5281/zenodo.23835945)

---

## Executive Profile
Third-year medical student and Python systems builder specializing in **Clinical LLM Safety Auditing, Neuro-Symbolic Verification, and Automated Rubric Engineering**. Architect of two live open-source tools—a **Deterministic-First Hybrid Clinical Auditor** and a **Cloud Clinical Reasoning Platform**—backed by a DOI-registered benchmark across 420 emergency clinical evaluations anchored to Class I international society guidelines. Bridges clinical training with test-driven Python engineering (TDD), directed acyclic graph (DAG) reasoning models, and zero-leakage benchmark design.

---

## Independent Research & Systems Engineering Experience

### 1. Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)
*Independent Lead Researcher & System Architect (2026)* | [Interactive 420-Trace Explorer](https://hammamnm.github.io/reasoning-debugger/) | [GitHub Repo](https://github.com/HammamNM/reasoning-debugger) | [50-Scenario Clinical Specs](https://github.com/HammamNM/reasoning-debugger/blob/main/CLINICAL_SPECIFICATIONS.md)
* **Two-Stage Neuro-Symbolic Architecture:** Engineered a decoupled evaluation pipeline isolating constrained semantic extraction (Stage I) from pure-Python deterministic rule verification (Stage II, `< 2 ms` CPU latency) across **420 paired emergency management plans** on 6 model ecosystems (`openai/gpt-oss-120b`, `gemini-3.5/3.1-flash-lite`, `gemma-4-26b-a4b-it`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`).
* **Exposed LLM-as-a-Judge Blindness:** Demonstrated empirically on the held-out 35-scenario test split that standalone LLM judges missed **71.7% (38/53; 95% Wilson CI: 58.4%–82.0%)** of criterion-unsafe responses—including **100% of failures (27/27)** from fluent flagship models—due to surface-fluency masking.
* **Eliminated Lexical False Alarms on Frozen Rules:** Resolved the **48.2% false-alarm rate (177/367)** of untyped keyword matchers via a canonical Assertion/Negation Gate (`PROPOSED` vs. `NEGATED`), achieving **100.0% specificity (367/367)** and **100.0% criterion sensitivity** (`Youden's J = 1.000`) against pre-frozen guideline rule specifications.
* **Zero-Hallucination Extraction & Guideline Grounding:** Enforced exact character-level grounding (`norm(source_span) in norm(R)`) with **0 hallucinations across 1,767 extracted events** across 50 emergency scenarios anchored directly to Class I recommendations from **AHA/ACC, ESC, BTS, EAST, and Surviving Sepsis Campaign** guidelines.

### 2. Clinical Reasoning Platform & Domain-Independent Execution Kernel
*Creator & Full-Stack Python Developer (2026)* | [Live Cloud Web App (PythonAnywhere)](https://hammam16.pythonanywhere.com/) | [Kernel Architecture Spec](https://github.com/HammamNM/reasoning-debugger/blob/main/ARCHITECTURE.md) | [Source Code](https://github.com/HammamNM/reasoning-debugger/tree/main/kernel)
* **Full-Stack Cloud Reasoning Engine:** Built and deployed a live Python web platform (`hammam16.pythonanywhere.com`) and modular runtime kernel that transforms unstructured clinical decision flows and chain-of-thought traces into structured **Directed Acyclic Reasoning Graphs (DAGs)** with explicit provenance links.
* **Automated Cognitive Bias & Epistemic Detectors:** Implemented deterministic structural analyzers to localize *anchoring bias*, *premature diagnostic closure*, *unsupported inference*, and *temporal prerequisite violations* (`idx(prereq) < idx(action)`).
* **Contract-Driven Software Quality:** Enforced strict API boundary isolation, schema serialization guarantees, and zero-leakage architecture verified across **30+ automated `pytest` contract suites**.

---

## Peer-Citable Preprint & Technical Medical Publishing

* **Preprint Manuscript (Zenodo / CERN):** **Omer, H.** (2026). *Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure*. Official DOI: [10.5281/zenodo.23835945](https://doi.org/10.5281/zenodo.23835945) (20 pages, 50 scenarios, 420 live evaluations).
* **Founder & Technical Author — NexoraMed ([nexoramed.online](https://nexoramed.online)):** Authoring English technical articles analyzing Medical AI safety, clinical reasoning benchmarks, and AI tools in medical education (2026 – Present).

---

## Technical & Clinical Arsenal

* **AI Safety & Evaluation Engineering:** Multi-Ecosystem LLM Benchmarking, LLM-as-a-Judge Failure Auditing, Sycophancy & Precautionary Shift Analysis, Automated Rubric & Protocol Engineering, Statistical Verification (Wilson 95% CIs, Exact McNemar Tests, 6-Tier Ablation Design).
* **Software & Systems Engineering:** Python (OOP, Type-Safe Schemas, Cloud Web Apps, CLI & REST APIs), Neuro-Symbolic Pipelines, Deterministic Substring & Regex Engines, JSON Schema Constrained Decoding, Pytest TDD, Git/GitHub, Linux/Termux CLI.
* **Clinical Domain Grounding:** Emergency Medicine Resuscitation & Triage Protocols, Class I Guideline Interpretation (AHA/ACC, ESC, BTS, EAST, ATLS), Differential Diagnosis & Contraindication Auditing.

---

## Education

**Bachelor of Medicine, Bachelor of Surgery (MBBS Candidate — 3rd Year)**  
Faculty of Medicine, Omdurman Islamic University — Omdurman, Sudan | **Expected Graduation: 2029**
