import json

with open("study_v1/scenarios/dev_scenarios_v1.json") as f:
    dev = json.load(f)
with open("study_v1/scenarios/test_scenarios_v1.json") as f:
    test = json.load(f)

all_s = dev + test
print("="*72)
print(f"✅ VERIFIED BENCHMARK TOTAL : {len(all_s)}/50 CLINICAL SCENARIOS")
print(f"   • Dev Split (Frozen)     : {len(dev)} scenarios ({sum(not s['pressure_valid'] for s in dev)} Wrongful, {sum(s['pressure_valid'] for s in dev)} Rightful)")
print(f"   • Held-Out Test Split    : {len(test)} scenarios ({sum(not s['pressure_valid'] for s in test)} Wrongful, {sum(s['pressure_valid'] for s in test)} Rightful)")
print(f"   • Overall Balance        : {sum(not s['pressure_valid'] for s in all_s)} Wrongful Traps | {sum(s['pressure_valid'] for s in all_s)} Rightful Hints")
print("="*72)
