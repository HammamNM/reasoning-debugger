import os
import json
import math

def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) / n) + ((z**2) / (4 * (n**2))))) / denom
    return (max(0.0, (center - half) * 100), min(100.0, (center + half) * 100))

def mcnemar_exact_p(b: int, c: int) -> float:
    """Exact binomial two-sided McNemar p-value for discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # Sum binomial tail probabilities
    tail = sum(math.comb(n, i) * (0.5 ** n) for i in range(k + 1))
    return min(1.0, 2.0 * tail)

MODELS = [
    ("openai/gpt-oss-120b", "study_v1/results/live_eval_openai_gpt-oss-120b.json", "OpenAI Open-Weight (120B Dense)"),
    ("openai/gpt-oss-20b", "study_v1/results/live_eval_openai_gpt-oss-20b.json", "OpenAI Open-Weight (20B Compact)"),
    ("qwen/qwen3.8-27b", "study_v1/results/live_eval_qwen_qwen3_8-27b.json", "Alibaba Qwen 3.8 (27B Dense)"),
    ("gemma-4-26b-a4b-it", "study_v1/results/live_eval_gemma-4-26b-a4b-it.json", "Google Gemma 4 (26B-A4B MoE)"),
    ("gemini-3.5-flash-lite", "study_v1/results/live_eval_gemini-3_5-flash-lite.json", "Google Gemini 3.5 Flash-Lite"),
    ("gemini-3.1-flash-lite", "study_v1/results/live_eval_gemini-3_1-flash-lite.json", "Google Gemini 3.1 Flash-Lite"),
]

report_out = {
    "benchmark_version": "v0.2-frozen-rules",
    "held_out_test_scenarios": 35,
    "wrongful_traps": 24,
    "rightful_hints": 11,
    "models": {}
}

print("\n" + "="*118)
print("🏛️  TABLE 1: HELD-OUT TEST SPLIT PERFORMANCE (N=35 SCENARIOS, 70 PAIRED EVALUATIONS PER MODEL) WITH 95% WILSON CIs")
print("="*118)
print(f"{'Model (Architecture)':<34} | {'Wrongful Neutral (95% CI)':<25} | {'Wrongful Pressured (95% CI)':<27} | {'Rightful Neutral -> Pressured':<28}")
print("-" * 118)

total_auditor_fails = 0
total_judge_false_passes = 0
violation_breakdown = {"MISSING_REQUIRED_ACTION": 0, "FORBIDDEN_ACTION": 0, "TEMPORAL_PREREQUISITE": 0, "EPISTEMIC_OTHER": 0}

for m_id, fpath, label in MODELS:
    if not os.path.exists(fpath):
        continue
    with open(fpath) as f:
        data = json.load(f)

    wrongful = [v for v in data.values() if not v["pressure_valid"]]
    rightful = [v for v in data.values() if v["pressure_valid"]]

    wn_k, wn_n = sum(1 for v in wrongful if v["neutral"]["auditor_verdict"] == "PASS"), len(wrongful)
    wp_k, wp_n = sum(1 for v in wrongful if v["pressured"]["auditor_verdict"] == "PASS"), len(wrongful)
    rn_k, rn_n = sum(1 for v in rightful if v["neutral"]["auditor_verdict"] == "PASS"), len(rightful)
    rp_k, rp_n = sum(1 for v in rightful if v["pressured"]["auditor_verdict"] == "PASS"), len(rightful)

    wn_ci = wilson_ci(wn_k, wn_n)
    wp_ci = wilson_ci(wp_k, wp_n)

    # Discordant pairs on Wrongful traps: b = Neutral PASS & Pressured FAIL (Sycophancy collapse), c = Neutral FAIL & Pressured PASS (Defensive arousal)
    b_syc = sum(1 for v in wrongful if v["neutral"]["auditor_verdict"] == "PASS" and v["pressured"]["auditor_verdict"] == "FAIL")
    c_def = sum(1 for v in wrongful if v["neutral"]["auditor_verdict"] == "FAIL" and v["pressured"]["auditor_verdict"] == "PASS")
    p_val_wrongful = mcnemar_exact_p(b_syc, c_def)

    # Judge false-pass rate on actual unsafe outputs (where Auditor == FAIL)
    m_fails = 0
    m_judge_fp = 0
    for v in data.values():
        for cond in ["neutral", "pressured"]:
            if v[cond]["auditor_verdict"] == "FAIL":
                m_fails += 1
                total_auditor_fails += 1
                if v[cond]["llm_judge_verdict"] == "PASS":
                    m_judge_fp += 1
                    total_judge_false_passes += 1

    wn_str = f"{wn_k}/{wn_n} ({wn_k/wn_n*100:4.1f}% [{wn_ci[0]:4.1f}-{wn_ci[1]:4.1f}])"
    wp_str = f"{wp_k}/{wp_n} ({wp_k/wp_n*100:4.1f}% [{wp_ci[0]:4.1f}-{wp_ci[1]:4.1f}])"
    r_str  = f"{rn_k}/{rn_n} ({rn_k/rn_n*100:4.1f}%) -> {rp_k}/{rp_n} ({rp_k/rp_n*100:4.1f}%)"

    print(f"{label:<34} | {wn_str:<25} | {wp_str:<27} | {r_str:<28}")

    report_out["models"][m_id] = {
        "label": label,
        "completed_scenarios": len(data),
        "wrongful_neutral": {"pass": wn_k, "total": wn_n, "pct": round(wn_k/wn_n*100, 2), "wilson_95_ci": [round(wn_ci[0], 1), round(wn_ci[1], 1)]},
        "wrongful_pressured": {"pass": wp_k, "total": wp_n, "pct": round(wp_k/wp_n*100, 2), "wilson_95_ci": [round(wp_ci[0], 1), round(wp_ci[1], 1)]},
        "wrongful_discordant": {"sycophancy_collapse_b": b_syc, "defensive_arousal_c": c_def, "mcnemar_p": round(p_val_wrongful, 4)},
        "rightful_neutral": {"pass": rn_k, "total": rn_n, "pct": round(rn_k/rn_n*100, 2)},
        "rightful_pressured": {"pass": rp_k, "total": rp_n, "pct": round(rp_k/rp_n*100, 2)},
        "auditor_detected_failures": m_fails,
        "llm_judge_false_passes_on_failures": m_judge_fp
    }

print("="*118)
print("\n" + "="*118)
print("🔍 TABLE 2: DISCORDANT PAIR ANALYSIS (SYCOPHANCY COLLAPSE vs. DEFENSIVE AROUSAL) & STANDALONE LLM-JUDGE BLINDNESS")
print("="*118)
print(f"{'Model':<26} | {'Sycophancy Collapse (P->F)':<26} | {'Defensive Arousal (F->P)':<24} | {'McNemar p':<10} | {'Judge False-Pass on Unsafe'}")
print("-" * 118)
for m_id, m_stat in report_out["models"].items():
    b = m_stat["wrongful_discordant"]["sycophancy_collapse_b"]
    c = m_stat["wrongful_discordant"]["defensive_arousal_c"]
    p = m_stat["wrongful_discordant"]["mcnemar_p"]
    mf = m_stat["auditor_detected_failures"]
    jfp = m_stat["llm_judge_false_passes_on_failures"]
    j_str = f"{jfp}/{mf} ({jfp/mf*100:.1f}% missed by Judge)" if mf > 0 else "0/0"
    print(f"{m_id:<26} | {b:<26} | {c:<24} | {p:<10.4f} | {j_str}")

overall_fp_rate = (total_judge_false_passes / total_auditor_fails * 100) if total_auditor_fails else 0.0
fp_ci = wilson_ci(total_judge_false_passes, total_auditor_fails)
print("-" * 118)
print(f"🚨 POOLED STANDALONE LLM-JUDGE FALSE-PASS RATE ON UNSAFE RESPONSES: {total_judge_false_passes}/{total_auditor_fails} ({overall_fp_rate:.1f}% [95% CI: {fp_ci[0]:.1f}% - {fp_ci[1]:.1f}%])")
print("="*118 + "\n")

with open("study_v1/results/final_statistical_summary_v1.json", "w") as out_f:
    json.dump(report_out, out_f, indent=2)
