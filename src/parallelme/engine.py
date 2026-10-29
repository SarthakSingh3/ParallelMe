"""Vectorized Monte Carlo simulation engine for decision alternatives."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from parallelme.distributions import sample_schedule_factor, sample_velocity
from parallelme.metrics import compute_metric_summary
from parallelme.models import (
    Decision,
    MetricSummary,
    Scenario,
    ScenarioResult,
    SimulationRun,
    TrackConfig,
)
from parallelme.validation import (
    validate_decision,
    validate_scenario,
    validate_scenarios_for_comparison,
    validate_simulation_parameters,
)


def simulate_scenario(
    scenario: Scenario,
    time_horizon_weeks: int,
    iterations: int,
    rng: np.random.Generator,
) -> Tuple[ScenarioResult, Dict[str, np.ndarray], np.ndarray]:
    """Execute Monte Carlo simulation for a single scenario.

    Args:
        scenario: The scenario defining track allocations and distributions.
        time_horizon_weeks: Duration in weeks (T).
        iterations: Number of simulated futures (N).
        rng: Initialized NumPy random Generator instance.

    Returns:
        Tuple of:
            - ScenarioResult with descriptive statistics.
            - Dict mapping track_name -> 1D array of final outcomes of length N.
            - 1D array of total hours expended of length N.
    """
    track_names = list(scenario.allocations.keys())

    # Initialize skill state arrays
    current_skills: Dict[str, np.ndarray] = {}
    for track in track_names:
        cfg = scenario.track_configs.get(track)
        baseline = cfg.baseline_skill if cfg else 0.0
        current_skills[track] = np.full(iterations, baseline, dtype=np.float64)

    total_hours_sim = np.zeros(iterations, dtype=np.float64)

    # Step through each week
    for _ in range(time_horizon_weeks):
        # Human schedule execution factor for this week across all iterations
        eta = sample_schedule_factor(rng, size=(iterations,))

        for track in track_names:
            planned_hours = scenario.allocations[track]
            cfg = scenario.track_configs.get(track, TrackConfig(name=track))

            # Effective hours spent on this track
            effective_hours = planned_hours * eta
            total_hours_sim += effective_hours

            # Sample learning velocity for each iteration
            velocity = sample_velocity(
                rng,
                size=(iterations,),
                mean=cfg.velocity_mean,
                sd=cfg.velocity_sd,
                dist_family=cfg.velocity_dist,
            )

            # Diminishing returns scaling: d_factor = 1 / (1 + gamma * S)
            diminishing = 1.0 + (cfg.diminishing_returns * current_skills[track])
            delta_skill = (velocity * effective_hours) / diminishing

            # Retention decay & state transition
            decay = cfg.retention_decay
            new_skill = (1.0 - decay) * current_skills[track] + delta_skill
            current_skills[track] = np.maximum(0.0, new_skill)

    # Aggregate summaries
    track_summaries: Dict[str, MetricSummary] = {}
    for track in track_names:
        threshold = scenario.target_thresholds.get(track)
        track_summaries[track] = compute_metric_summary(
            current_skills[track],
            target_threshold=threshold,
        )

    total_hours_summary = compute_metric_summary(total_hours_sim)

    result = ScenarioResult(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        track_summaries=track_summaries,
        total_hours_summary=total_hours_summary,
    )

    return result, current_skills, total_hours_sim


def run_simulation(
    decision: Decision,
    scenarios: Optional[List[Scenario]] = None,
    iterations: int = 1000,
    random_seed: int = 42,
) -> SimulationRun:
    """Run full Monte Carlo simulation for all scenarios in a decision.

    Guarantees reproducible execution when given the same random seed.

    Args:
        decision: The parent decision.
        scenarios: Optional list of scenarios to run. If None, uses decision.scenarios.
        iterations: Number of Monte Carlo iterations (default: 1000).
        random_seed: Integer seed for NumPy Generator (default: 42).

    Returns:
        SimulationRun containing immutable snapshot and aggregated results.
    """
    active_scenarios = scenarios if scenarios is not None else decision.scenarios

    # Validate inputs
    validate_simulation_parameters(iterations, random_seed)
    validate_scenarios_for_comparison(active_scenarios, decision)

    # Initialize master RNG
    rng = np.random.default_rng(random_seed)

    results: Dict[str, ScenarioResult] = {}
    for sc in active_scenarios:
        res, _, _ = simulate_scenario(
            scenario=sc,
            time_horizon_weeks=decision.time_horizon_weeks,
            iterations=iterations,
            rng=rng,
        )
        results[sc.id] = res

    # Create immutable run snapshot
    run = SimulationRun(
        decision_id=decision.id,
        scenario_ids=[sc.id for sc in active_scenarios],
        iterations=iterations,
        random_seed=random_seed,
        snapshot_config={
            "decision": decision.to_dict(),
            "scenarios": [sc.to_dict() for sc in active_scenarios],
        },
        results=results,
    )

    return run
