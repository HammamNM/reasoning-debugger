import os
import json
import glob
import math

results_dir = "study_v1/results"
result_files = glob.glob(os.path.join(results_dir, "live_eval_*.json"))

print("="*100)
print("📊 ACADEMIC BENCHMARK SUMMARY TABLE: CROSS-MODEL MULTI-SCALE EVALUATION (N=35 TEST SPLIT)")
print("="*100)
print(f"{'Model Name':<30} | {'Wrongful (Neutral -> Pressured)':<32} | {'Rightful (Neutral -> Pressured)':<32} | {'Judge Error Rate'}")
print("-" * 125)

for fpath in sorted(result_files):
    mname = os.path.basename(fpath).replace("live_eval_", "").replace(".json", "").replace("_", "/")
    with open(fpath, "r") as f:
        data = json.load(f)

    if not data:
        continue

    wrongful = [v for v in data.values() if not v["pressure_valid"]]
    rightful = [v for v in data.values() if v["pressure_valid"]]

    w_neut = sum(1 for v in wrongful if v["neutral"]["auditor_verdict"] == "PASS")
    w_pres = sum(1 for v in wrongful if v["pressured"]["auditor_verdict"] == "PASS")
    w_tot = len(wrongful)

    r_neut = sum(1 for v in rightful if v["neutral"]["auditor_verdict"] == "PASS")
    r_pres = sum(1 for v in rightful if v["pressured"]["auditor_verdict"] == "PASS")
    r_tot = len(rightful)

    # Calculate how many times LLM-judge said PASS while our auditor said FAIL
    judge_errors = 0
    total_evals = 0
    for v in data.values():
        for cond in ["neutral", "pressured"]:
            total_evals += 1
            aud_v = v[cond]["auditor_verdict"]
            j_v = v[cond]["llm_judge_verdict"]
            if aud_v == "FAIL" and j_v == "PASS":
                judge_errors += 1

    w_str = f"{w_neut}/{w_tot} ({w_neut/w_tot*100:.1f}%) -> {w_pres}/{w_tot} ({w_pres/w_tot*100:.1f}%)" if w_tot > 0 else "N/A"
    r_str = f"{r_neut}/{r_tot} ({r_neut/r_tot*100:.1f}%) -> {r_pres}/{r_tot} ({r_pres/r_tot*100:.1f}%)" if r_tot > 0 else "N/A"
    j_err_pct = (judge_errors / total_evals * 100) if total_evals > 0 else 0.0

    print(f"{mname:<30} | {w_str:<32} | {r_str:<32} | {judge_errors}/{total_evals} ({j_err_pct:.1f}%)")

print("="*100)
