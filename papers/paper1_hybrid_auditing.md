# Traceable Hybrid Auditing of Clinical LLM Outputs: Combining Deterministic Span Verification, Protocol Rules, and Graph-Based Reasoning Kernels

**Authors:** Hammam N. M.  
**Repository:** `https://github.com/HammamNM/reasoning-debugger`

---

## Abstract
Evaluating Large Language Models (LLMs) in high-stakes clinical workflows such as acute chest pain management requires moving beyond final-answer accuracy toward rigorous process auditing. Current evaluation paradigms predominantly rely on unconstrained *LLM-as-a-Judge* frameworks, which are susceptible to judge hallucinations, unverified intermediate assumptions, and high false-positive rates when models express appropriate diagnostic uncertainty. In this paper, we present a **Traceable Neuro-Symbolic Auditing Framework** composed of three decoupled layers: (1) a `TraceExtractor` equipped with a deterministic substring verification firewall and canonical vocabulary normalizer, (2) a `ClinicalRuleEvaluator` enforcing temporal ordering, mandatory actions, and contraindications, and (3) a structural `Reasoning Kernel` that constructs Directed Acyclic Graphs (DAGs) to detect unsupported definitive inferences (`Pattern RP-001`). In a controlled validation and ablation study across synthetic adversarial traces, real frontier model outputs, and linguistic edge cases, incorporating explicit assertion-status calibration (`PROPOSED`, `REPORTED_PERFORMED`, `NEGATED`, `SUSPECTED`, `DEFINITIVE`) increased auditor specificity from **57.1%** to **100.0%** and improved the overall $F_1$-score from **0.667** to **1.000** while maintaining **100.0%** sensitivity to protocol violations.

---

## 1. Introduction
As Large Language Models (LLMs) transition from static medical multiple-choice benchmarks (e.g., USMLE) to open-ended clinical decision support, evaluating their safety becomes substantially more complex. In emergency medicine—and specifically in **Acute Chest Pain** triage—a model can arrive at a plausible differential diagnosis while simultaneously proposing lethal management steps, such as discharging a patient after symptomatic relief from a gastrointestinal cocktail before serial troponin results are available (premature closure), or initiating empiric anticoagulation in suspected aortic dissection.

Relying solely on another LLM to judge free-text clinical responses introduces two methodological vulnerabilities:
1. **Extractor/Judge Hallucination:** The evaluating model may infer or fabricate clinical actions that were never stated in the candidate response.
2. **Epistemic Penalization:** Standard evaluators frequently conflate diagnostic uncertainty (e.g., listing Non-ST-Elevation Myocardial Infarction [NSTEMI] as a *suspected* differential diagnosis) with an unsupported *definitive* diagnostic claim, or misclassify *negated* warnings (e.g., *"Do not administer heparin"*) as proposed actions.

To address these gaps, we introduce a traceable, three-tier neuro-symbolic auditing pipeline that separates linguistic event extraction from deterministic rule and graph verification.

---

## 2. System Architecture

Our architecture decomposes clinical auditing into three auditable stages:

### 2.1 Tier 1: `TraceExtractor` (Hallucination Firewall & Assertion Calibration)
Rather than permitting an LLM judge to directly score a response, the raw text $T$ is parsed into structured candidate events $E = \{e_1, e_2, \dots, e_n\}$ and support relations $R$. Each candidate event must pass three deterministic filters inside `TraceExtractor`:

1. **Deterministic Span Verification (`verify_span`):**  
   Every extracted event $e_i$ must carry a verbatim `source_span` $s_i$. Let $\mathcal{N}(\cdot)$ denote whitespace and case normalization. An event is accepted if and only if:
   $$\mathcal{N}(s_i) \subseteq \mathcal{N}(T)$$
   Any event failing this check is immediately rejected and logged with reason `SPAN_NOT_IN_SOURCE`, preventing extractor hallucinations from contaminating downstream evaluators.

2. **Canonical Vocabulary Normalization:**  
   Lexical variations (e.g., `PERFORM_ECG`, `OBTAIN_ECG`, `12_LEAD_ECG`) are deterministically mapped to canonical protocol codes (`ORDER_ECG`), eliminating false-negative omissions caused by surface-level phrasing differences.

3. **Assertion-Status Epistemic Filtering:**  
   Each event is tagged with an epistemic assertion status $\alpha(e_i) \in \{\text{PROPOSED}, \text{REPORTED\_PERFORMED}, \text{OBSERVED\_RESULT}, \text{NEGATED}, \text{SUSPECTED}, \text{DEFINITIVE}\}$.
   - Events with $\alpha(e_i) = \text{NEGATED}$ are filtered prior to execution auditing so that explicit clinical warnings are never penalized as executed contraindications.
   - Diagnostic inferences (`INFERENCE`) are forwarded to the strict structural kernel with `support_required = True` if and only if $\alpha(e_i) = \text{DEFINITIVE}$, preserving safe clinical differential reasoning (`SUSPECTED`).

### 2.2 Tier 2: `ClinicalRuleEvaluator` (Domain Protocol Engine)
Given the verified trace, the domain evaluator checks adherence against structured clinical case specifications:
- **Mandatory Omissions (`CRITICAL_OMISSION`):** Flags missing life-critical actions (`must_include`) or missing diagnostic alternatives (`must_include_any`).
- **Temporal Ordering Constraints (`PREMATURE_CLOSURE`):** Let $\text{idx}(a)$ denote the chronological step index of action $a$. For any ordering rule $(a_{\text{pre}} \prec a_{\text{target}})$, if $a_{\text{target}}$ (e.g., `DISCHARGE`) is proposed while $a_{\text{pre}}$ (e.g., `TROPONIN_RESULT_AVAILABLE`) is absent or occurs at $\text{idx}(a_{\text{pre}}) > \text{idx}(a_{\text{target}})$, a premature closure violation is triggered.
- **Contraindications (`CONTRAINDICATED_ACTION`):** Flags any proposed or performed action intersecting the scenario's `must_avoid` set (e.g., `ADMINISTER_HEPARIN` in acute aortic dissection).

### 2.3 Tier 3: `Reasoning Kernel` (Graph-Based Structural Verification)
Independent of specific clinical disease rules, the `Reasoning Kernel` constructs a Directed Acyclic Graph $G = (V, E_{\text{graph}})$ where nodes $V$ represent verified events and directed edges represent evidentiary support (`EdgeRelation.SUPPORTS`). The `UnsupportedInferenceDetector` evaluates structural soundness:
$$\forall v \in V_{\text{INFERENCE}}: \quad \text{if } \text{support\_required}(v) = \text{True} \land \text{deg}^{-}_{\text{SUPPORTS}}(v) = 0 \implies \text{Trigger } \texttt{RP-001}$$
where $\text{deg}^{-}_{\text{SUPPORTS}}(v)$ is the in-degree of supporting evidence edges targeting node $v$.

---

## 3. Experimental Validation & Ablation Study

### 3.1 Benchmark Design
We evaluated the auditing pipeline across three distinct test sets:
1. **Synthetic Calibration & Sensitivity Suite ($N=5$):** Five structured acute chest pain scenarios (`CP_PILOT_001` through `005`) covering mandatory ECG acquisition, premature discharge after a GI cocktail, ambiguous pulmonary embolism (PE) workup, anticoagulation in aortic dissection, and unsupported definitive NSTEMI claims.
2. **Real Frontier Model Run ($N=5$):** Responses generated by a safety-aligned frontier model (`GPT-4o`) subjected to adversarial prompts encouraging premature closure, empiric heparinization, and sycophantic adoption of an unverified NSTEMI diagnosis.
3. **Unseen Linguistic & Structural Edge Suite ($N=5$):** Independent stress tests evaluating quoted clinical errors, conditional discharge plans, injected extractor hallucinations, lexical synonyms, and evidence-backed definitive diagnoses.

### 3.2 Ablation Study Results (Assertion & Prerequisite Calibration)
Table 1 compares the baseline uncalibrated pipeline (which treats all extracted actions as active proposals and all diagnostic inferences as requiring immediate proof) against the calibrated hybrid architecture across the combined 10-case validation suite (3 true protocol/reasoning violations, 7 safe clinical pathways).

| Auditor Configuration | $TP$ | $FP$ | $TN$ | $FN$ | Recall (Sensitivity) | Specificity | Precision | $F_1$-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Baseline (Uncalibrated)** | 3 | 3 | 4 | 0 | 100.0% | 57.1% | 50.0% | 0.667 |
| **2. Full Hybrid (Calibrated)** | **3** | **0** | **7** | **0** | **100.0%** | **100.0%** | **100.0%** | **1.000** |

*Analysis:* In the uncalibrated baseline, safe responses that explicitly refused premature discharge (`NEGATED`) or listed NSTEMI as a differential possibility (`SUSPECTED`) generated 3 false-positive violations. Calibratingprerequisite rules and assertion filtering eliminated all false positives ($Specificity = 100.0\%$) without sacrificing violation detection ($Recall = 100.0\%$).

### 3.3 Edge-Case Stress Test Results
On the unseen 5-case linguistic stress suite (`run_edge_cases.py`), the calibrated auditor achieved **5/5 (100.0%)** concordance with ground-truth labels:
- Successfully rejected a fabricated ECG span (`SPAN_NOT_IN_SOURCE`).
- Correctly normalized `START_HEPARIN` $\rightarrow$ `ADMINISTER_HEPARIN` to catch a contraindicated dissection intervention.
- Distinguished a rejected colleague quote (`EDGE_01`) and an evidence-linked definitive NSTEMI claim (`EDGE_05`) from unsupported diagnostic leaps.

---

## 4. Methodological Limitations & Scope
While deterministic verification substantially improves audit traceability, several boundaries must be noted:
1. **Upstream Extraction Recall:** Span verification guarantees that *extracted* events exist verbatim in the source text (preventing false additions), but cannot guarantee that the upstream LLM parser did not omit a subtle clinical statement or misassign an assertion tag.
2. **Conditional Flattening:** Complex nested conditionals in prose (e.g., multi-branch PE algorithms) are partially flattened when represented as discrete chronological events unless explicitly modeled as conditional edges.
3. **Rule Scope:** Clinical rules in our pilot represent simplified educational pathways for acute chest pain and require formal guideline mapping before deployment in real-world clinical governance.

---

## 5. Conclusion
By decoupling text extraction from deterministic span verification, temporal protocol evaluation, and graph-based inference checking, our framework provides a transparent, reproducible foundation for auditing clinical LLMs. This architecture establishes the validated measurement instrument required for large-scale empirical evaluations of model vulnerability under clinical pressure.
