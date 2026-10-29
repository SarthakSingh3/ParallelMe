# ParallelMe Threat Model & Reliability Analysis

## 1. System Scope & Assets

ParallelMe is an offline, local-first analytical tool. Assets requiring protection:
1. **User Planning Data:** Stored in local SQLite database (`parallelme.db`). Contains personal learning decisions, time budgets, and empirical logs.
2. **Computational Availability:** Local CPU and memory resources against resource exhaustion (DoS) from unbounded simulation runs.
3. **Data Integrity:** Protection against file corruption, invalid schema imports, or silent numeric coercion.

---

## 2. Threat Analysis & Mitigations

### 2.1 Arbitrary Code Execution (Zero Unsafe Deserialization)
* **Threat:** Malicious scenario files attempting code injection via `eval()`, `exec()`, or Python `pickle`.
* **Mitigation:** The application strictly forbids `pickle` or dynamic code evaluation. All import/export operations use standard `json.loads` with strict schema validation through `parallelme.models.Decision.from_dict` and `parallelme.validation.validate_decision`.

### 2.2 Denial of Service (Resource Exhaustion)
* **Threat:** User or imported file specifies $N = 10^{10}$ iterations or 10,000 weeks, causing out-of-memory (OOM) crashes or CPU hang.
* **Mitigation:** Strict bounds enforced in `validate_simulation_parameters`:
  * Maximum iterations: $100,000$
  * Maximum time horizon: $52$ weeks (1 year)
  * Maximum weekly hours: $168.0$ hours

### 2.3 SQL Injection
* **Threat:** Malicious characters in titles, notes, or scenario names injecting arbitrary SQL.
* **Mitigation:** 100% parameterized queries in `parallelme.persistence.Database`. No string concatenation is used for SQL execution. Foreign keys with `ON DELETE CASCADE` prevent orphaned records.

### 2.4 Path Traversal & Unsafe File Handling
* **Threat:** Export or import routines accessing arbitrary system directories.
* **Mitigation:** Database paths are explicitly normalized using `Path.resolve()`. File exports in the UI operate via in-memory buffers through Streamlit's `download_button`.

### 2.5 Privacy & Data Leakage
* **Threat:** Personal habits or notes transmitted to third-party cloud services.
* **Mitigation:** Zero network calls in the simulation core. No analytics tracking or remote telemetry. All data resides in the user's local directory.

---

## 3. Reliability & Numerical Stability Guarantees

1. **Floating-Point NaN / Infinity Protection:** Any presence of `NaN`, `+inf`, or `-inf` immediately aborts validation with `NumericSanityError`.
2. **Deterministic Reproducibility:** Every Monte Carlo run requires an explicit random seed and uses NumPy's decoupled `np.random.default_rng(seed)`.
3. **Zero Black-Box LLM Guessing:** No LLM is connected to the numerical simulation pipeline. Output distributions are purely mathematical consequences of user inputs.
