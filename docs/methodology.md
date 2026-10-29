# ParallelMe Simulation Methodology

## 1. Domain: Career & Learning Decisions

The initial domain models multi-skill allocation over a fixed planning horizon $T$ (measured in weeks).

### 1.1 Decision Variables & Constraints

Let $K$ be the set of alternative skill tracks or study domains (e.g., $K = \{\text{DSA}, \text{AI/ML}\}$).
For each track $k \in K$:
* $h_k \ge 0$: Planned weekly hours dedicated to skill $k$.
* $H_{\max} > 0$: Total weekly available study capacity.

**Feasibility Constraint:**
$$\sum_{k \in K} h_k \le H_{\max}$$

Any scenario where $\sum_k h_k > H_{\max}$ violates resource capacity and is mathematically infeasible.

---

## 2. Stochastic Discrete-Time Dynamics

For iteration $i \in \{1, \dots, N\}$ and week $t \in \{1, \dots, T\}$:

### 2.1 Schedule Volatility (Execution Factor $\eta_t$)

Human schedules deviate from plans due to illness, workload, and social commitments.
$$\eta_t^{(i)} \sim \text{Triangular}(\text{left}=0.5, \text{mode}=1.0, \text{right}=1.1)$$
Effective weekly hours spent on skill $k$:
$$\tilde{H}_{t, k}^{(i)} = h_k \cdot \eta_t^{(i)}$$

### 2.2 Skill Acquisition with Diminishing Marginal Returns

Learning efficiency slows as advanced concepts are encountered or fatigue accumulates:
$$\Delta S_{t, k}^{(i)} = \frac{v_k^{(i)} \cdot \tilde{H}_{t, k}^{(i)}}{1 + \gamma \cdot S_{t-1, k}^{(i)}}$$

Where:
* $v_k^{(i)} \sim \text{Lognormal}(\mu_v, \sigma_v)$ represents the baseline learning velocity (units mastered per effective hour).
* $\gamma \ge 0$ is the diminishing returns parameter. When $\gamma = 0$, learning is strictly linear.
* $S_{t-1, k}^{(i)}$ is the mastery level accumulated prior to week $t$.

### 2.3 Retention and Memory Decay

If a skill receives zero study time in a given week, natural forgetting occurs:
$$S_{t, k}^{(i)} = (1 - r_k) \cdot S_{t-1, k}^{(i)} + \Delta S_{t, k}^{(i)}$$

Where $r_k \in [0, 0.05]$ is the weekly decay coefficient.

---

## 3. Output Metrics & Descriptive Statistics

For each skill $k$ across all $N$ simulation iterations, final outcomes $\{S_{T, k}^{(1)}, \dots, S_{T, k}^{(N)}\}$ are summarized:

1. **Median ($P_{50}$):** The central tendency robust to skewness.
2. **Simulated Range ($[P_{10}, P_{90}]$):** An 80% range of simulated outcomes under the stated uncertainty distributions. (Explicitly *not* a frequentist confidence interval).
3. **Threshold Attainment Probability:**
   $$P(S_{T, k} \ge \theta) = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(S_{T, k}^{(i)} \ge \theta)$$
   where $\theta$ is the user's target benchmark (e.g., 100 LeetCode problems or 5 end-to-end ML projects).
4. **Total Hours Expended:**
   $$\text{Total Hours}^{(i)} = \sum_{t=1}^T \sum_{k \in K} \tilde{H}_{t, k}^{(i)}$$

---

## 4. Scientific Limitations & Failure Modes

1. **Unmodeled Synergies:** The initial model assumes skill domains are additive. In reality, learning Python may accelerate learning AI/ML. Future iterations will support explicit cross-skill transfer terms.
2. **Subjective Prior Sensitivity:** If the user specifies an unrealistic velocity $v_k$, simulated mastery scales accordingly. Sensitivity analysis must flag the degree to which results depend on $v_k$.
3. **Non-Causal Counterfactuals:** Comparing an unchosen scenario against an observed chosen path is a model-based comparison, not a proven counterfactual.
