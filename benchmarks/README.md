# Evaluation Benchmarks

To prove the engine is domain-agnostic and deterministic, traces are strictly categorized:

* **synthetic_realistic:** Controlled traces simulating real-world logic (e.g., coding, data analysis).
* **negative_control:** 100% valid reasoning traces to prove zero false-positive rates.
* **adversarial:** Traces with isolated early errors that are *not* used downstream, testing strict semantic propagation.
* **public_real_trace:** Raw, unmodified traces ingested from live agents (e.g., LangChain, AutoGPT) in the wild.
