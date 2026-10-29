# ParallelMe Product Specification

## 1. Core Data Models

### 1.1 Decision
* `id` (`str`, UUID v4): Unique identifier.
* `title` (`str`, 1–100 chars): Descriptive title.
* `description` (`str`, optional): Context and objectives.
* `time_horizon_weeks` (`int`, $1 \le T \le 52$): Planning duration.
* `max_weekly_hours` (`float`, $0 < H_{\max} \le 168$): Total weekly capacity constraint.
* `created_at` (`datetime` UTC): Creation timestamp.

### 1.2 Scenario
* `id` (`str`, UUID v4): Unique identifier.
* `decision_id` (`str`, UUID v4): Parent decision.
* `name` (`str`, 1–50 chars): Scenario label (e.g., "Full DSA Focus").
* `description` (`str`, optional): Scenario premise.
* `allocations` (`dict[str, float]`): Weekly hours allocated per track, e.g. `{"dsa": 15.0, "ai": 0.0}`.
* `parameters` (`dict[str, Any]`): Parameter distribution settings per track (velocity, decay, diminishing returns).

### 1.3 SimulationRun (Immutable Snapshot)
* `id` (`str`, UUID v4): Run identifier.
* `decision_id` (`str`): Parent decision.
* `scenario_ids` (`list[str]`): Scenarios included in the comparison.
* `iterations` (`int`, $100 \le N \le 50000$): Number of Monte Carlo draws.
* `random_seed` (`int`): RNG seed for determinism.
* `snapshot_config` (`dict`): Complete serialized copy of inputs at run time.
* `results` (`dict`): Aggregated metrics and percentile distributions.
* `created_at` (`datetime` UTC): Timestamp.

### 1.4 Observation
* `id` (`str`, UUID v4): Observation identifier.
* `decision_id` (`str`): Parent decision.
* `scenario_id` (`str`): Scenario actively being executed in reality.
* `week_number` (`int`, $1 \le t \le T$): Period index.
* `actual_hours` (`dict[str, float]`): Actual hours logged per track.
* `actual_units` (`dict[str, float]`): Real units or milestones achieved.
* `notes` (`str`, optional): Qualitative context (e.g., "Midterm exam week").
* `logged_at` (`datetime` UTC): Entry timestamp.

---

## 2. Validation & Edge-Case Rules

1. **Budget Enforcement:** $\sum_{k} \text{allocations}[k] \le \text{max\_weekly\_hours}$. Violation yields `ValidationError("Total allocated hours ({sum}) exceeds max weekly hours ({budget})")`.
2. **Numeric Sanity:** Any `NaN`, `+inf`, `-inf`, or negative hour allocation is rejected immediately.
3. **Multi-Alternative Check:** Scenario comparisons require at least 2 distinct scenarios.
4. **Duplicate Detection:** Scenarios within a decision cannot share the same name.
5. **Deterministic Seeds:** A run with identical seed and inputs produces bitwise identical percentiles.
