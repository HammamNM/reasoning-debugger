# Deterministic-First Hybrid Clinical Auditor (`v0.2-frozen-rules`)

**Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure**

* **Author:** Hammam Omer (Faculty of Medicine, Omdurman Islamic University; NexoraMed)
* **Full Manuscript (PDF, 24 Pages):** [`study_v1/PAPER_MANUSCRIPT_V1.pdf`](study_v1/PAPER_MANUSCRIPT_V1.pdf)
* **Full Manuscript (Markdown):** [`study_v1/PAPER_MANUSCRIPT_V1.md`](study_v1/PAPER_MANUSCRIPT_V1.md)
* **Frozen Audit Engine Tag:** `v0.2-frozen-rules`

---

## Key Empirical Findings (N=35 Held-Out Emergency Scenarios; 420 Paired Evaluations)

1. **Pervasive Blindness of Standalone `LLM-as-a-Judge`:** Across 53 criterion-unsafe clinical management plans, a standalone `LLM-as-a-Judge` evaluator missed **38/53 unsafe responses (71.7% False-Pass Rate; 95% Wilson CI: 58.4%–82.0%)**, including **100% of failures** produced by fluent flagship/large models (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `gemma-4-26b-a4b-it`, and `gemini-3.5-flash-lite`).
2. **Resolution of Lexical False Alarms via Assertion Gating:** An untyped lexical keyword matcher incurred a **48.2% false-alarm rate (177/367; specificity 51.8%)** because safe clinicians explicitly mention contraindicated drugs and premature dispositions in order to refuse them. Our Stage I **Canonical Assertion/Negation Gate** (`PROPOSED` vs. `NEGATED`) with **Verbatim Substring Verification** (`0/1,767` hallucinated events) eliminated all 177 false alarms (**100.0% specificity, 100.0% criterion recall**).
3. **Divergent Behavioral Shifts Under Collegial Pressure:** Under wrongful collegial pressure (N=24), `qwen/qwen3.8-27b` (`87.5% -> 75.0%`) and sparse MoE `gemma-4-26b-a4b-it` (`91.7% -> 83.3%`) exhibited net adverse compliance (sycophantic shifts), whereas `openai/gpt-oss-120b` (`91.7% -> 95.8%`) and `gemini-3.5/3.1-flash-lite` exhibited zero sycophantic collapses (`b=0`) and cue-triggered precautionary shifts.

---

## Summary Benchmark Table (Held-Out Test Split, N=35)

| Model Name | Ecosystem | Wrongful Traps: Neutral -> Pressured (N=24) | Rightful Hints: Neutral -> Pressured (N=11) | Total Unsafe (/70) | Judge False-Pass Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`openai/gpt-oss-120b`** | OpenAI Dense (120B) | 91.7% -> **95.8%** (+4.1%) | 90.9% -> **100.0%** | 4/70 (5.7%) | **4/4 (100% missed)** |
| **`gemini-3.1-flash-lite`** | Google Commercial | 87.5% -> **95.8%** (+8.3%) | 90.9% -> **100.0%** | 5/70 (7.1%) | 4/5 (80% missed) |
| **`gemini-3.5-flash-lite`** | Google Commercial | 87.5% -> 91.7% (+4.2%) | 90.9% -> **100.0%** | 6/70 (8.6%) | **6/6 (100% missed)** |
| **`gemma-4-26b-a4b-it`** | Google Sparse MoE | **91.7%** -> 83.3% (-8.4%) | **100.0%** -> **100.0%** | 6/70 (8.6%) | **6/6 (100% missed)** |
| **`qwen/qwen3.8-27b`** | Alibaba Dense (27B) | 87.5% -> 75.0% (-12.5%) | 81.8% -> **100.0%** | 11/70 (15.7%) | **11/11 (100% missed)** |
| **`openai/gpt-oss-20b`** | OpenAI Compact (20B) | 70.8% -> 79.2% (+8.4%) | 36.4% -> 81.8% | 21/70 (30.0%) | 7/21 (33.3% missed) |

---

## Reproducing the Statistical & Ablation Tables

```bash
python study_v1/run_statistical_analysis.py
python study_v1/run_true_ablation.py
