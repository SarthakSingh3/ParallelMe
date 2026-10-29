# ParallelMe

> **Transparent alternative decision simulator and empirical feedback engine.**

[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-39%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)]()

ParallelMe is an open-source, local-first alternative decision simulator. It allows students, engineers, and planners to explore counterfactual choices under uncertainty using transparent Monte Carlo simulations, enforce strict shared resource constraints across alternatives, inspect all driving assumptions, and log real-world observations over time to evaluate estimation bias.

---

## 🎯 Core Principles

1. **Simulation is Not Certainty:** Simulated percentile spreads ($P_{10}$ to $P_{90}$) reflect user-provided assumptions propagated through a mathematical model, never factual future predictions.
2. **Zero Black-Box Guessing:** Every numerical output has a traceable calculation. No LLM invents probabilities, statistics, or evidence.
3. **Transparent Assumptions:** Every parameter, distribution choice, and constraint is visible, inspectable, and user-editable.
4. **No Premature Model Fitting:** Model re-calibration is disabled until sufficient out-of-sample empirical data ($N \ge 30$ consistent intervals) is recorded.
5. **Fair Resource Accounting:** Competing scenarios must respect identical global resource limits (e.g., weekly time capacity).
6. **Local-First & Private:** Runs entirely offline using standard open-source numerical libraries with SQLite local storage.

---

## 📐 Architecture & Mathematical Dynamics

```
                           ParallelMe Architecture
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           Streamlit Web UI                             │
  │   - Scenario Manager     - Monte Carlo Runner    - Sensitivity View    │
  │   - Resource Audit       - Observation Ledger    - JSON/CSV Exporter   │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                    Validation & Constraints Engine                     │
  │   - Capacity Budget Guard (sum(allocations) <= MaxWeeklyHours)         │
  │   - Numeric Sanity Checks (Reject NaN, Inf, Negatives)                 │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                     Vectorized Monte Carlo Core                        │
  │   - Discrete-Time Stochastic Simulation (N iterations x T weeks)       │
  │   - Diminishing Returns: dS = (v * H_eff) / (1 + gamma * S)            │
  │   - Schedule Volatility: H_eff = h_k * eta_t                           │
  │   - Memory Retention Decay: S_t = (1 - r) * S_{t-1} + dS               │
  │   - Fast NumPy Vectorization (< 100ms for 5,000 iterations)            │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                  Persistence & Storage Layer (SQLite)                  │
  │   - Decisions & Scenarios Table     - Immutable Run Snapshots          │
  │   - Empirical Observations Table    - Foreign Key Integrity            │
  └────────────────────────────────────────────────────────────────────────┘
```

### Mathematical Formulation
For scenario $k$ during week $t \in [1, \dots, T]$ and iteration $i \in [1, \dots, N]$:
1. **Effective Hours:**
   $$\tilde{H}_{t, k}^{(i)} = h_k \cdot \eta_t^{(i)}, \quad \eta_t^{(i)} \sim \text{Triangular}(0.5, 1.0, 1.1)$$
2. **Skill Increment with Diminishing Returns:**
   $$\Delta S_{t, k}^{(i)} = \frac{v_k^{(i)} \cdot \tilde{H}_{t, k}^{(i)}}{1 + \gamma \cdot S_{t-1, k}^{(i)}}, \quad v_k^{(i)} \sim \text{Lognormal}(\mu_v, \sigma_v)$$
3. **Retention Decay & State Transition:**
   $$S_{t, k}^{(i)} = (1 - r_k) \cdot S_{t-1, k}^{(i)} + \Delta S_{t, k}^{(i)}$$

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.11, 3.12, or 3.13
* Windows PowerShell, macOS Terminal, or Linux Shell

### 2. Setup Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies in Editable Mode

```powershell
pip install -e ".[dev,ui]"
```

### 4. Run Automated Test Suite (39 Tests, 95% Coverage)

```powershell
pytest --cov=parallelme --cov-report=term-missing
```

### 5. Launch the Interactive Web Application

```powershell
streamlit run src/parallelme/app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 📊 Example: 90-Day Learning Decision

ParallelMe includes a pre-configured 12-week study decision in `examples/learning_decision.json` comparing:
* **Heavy DSA Focus:** 16 hrs/week DSA, 2 hrs/week AI/ML.
* **Heavy AI/ML Focus:** 2 hrs/week DSA, 16 hrs/week AI/ML.
* **Balanced 50/50 Split:** 9 hrs/week DSA, 9 hrs/week AI/ML (with 2 buffer hours).

All three scenarios operate strictly under a shared budget of **20.0 hours/week**.

---

## 🔒 Security & Privacy

* **Zero Cloud Dependence:** No personal habits, schedules, or decisions leave your machine.
* **Parameterized Queries:** SQLite access uses 100% parameterized SQL statements with foreign keys enabled.
* **No `eval` or `pickle`:** Serialization uses strictly validated standard JSON schemas.
* **Resource Bounds:** Iteration counts and time horizons are hard-capped to prevent accidental resource exhaustion.
* Detailed threat analysis is available in [`docs/threat_model.md`](docs/threat_model.md).

---

## 📚 Documentation
* [`docs/product_spec.md`](docs/product_spec.md) — Complete data schemas and functional specifications.
* [`docs/methodology.md`](docs/methodology.md) — Mathematical derivation, distribution proofs, and limitations.
* [`docs/prior_art.md`](docs/prior_art.md) — Prior art investigation and comparative landscape.
* [`docs/threat_model.md`](docs/threat_model.md) — Security, privacy, and integrity model.
