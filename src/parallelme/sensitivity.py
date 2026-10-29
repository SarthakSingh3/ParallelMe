"""Sensitivity and fragility analysis for decision simulations.

Explores how results vary when assumptions change, identifies parameters
with the largest impact, and detects potential scenario ranking reversals.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from parallelme.engine import simulate_scenario
from parallelme.models import Decision, Scenario, TrackConfig


def run_parameter_sweep(
    scenario: Scenario,
    time_horizon_weeks: int,
    track_name: str,
    param_name: str,
    multipliers: List[float],
    iterations: int = 500,
    random_seed: int = 42,
) -> List[Dict[str, Any]]:
    """Evaluate how varying a parameter by percentage multipliers shifts outcome metrics.

    Args:
        scenario: Base scenario.
        time_horizon_weeks: Planning duration in weeks.
        track_name: Target skill track to perturb.
        param_name: Attribute name on TrackConfig (e.g. 'velocity_mean', 'diminishing_returns').
        multipliers: List of relative multipliers (e.g. [0.7, 0.85, 1.0, 1.15, 1.3]).
        iterations: Number of Monte Carlo draws per test point.
        random_seed: Deterministic seed for fair across-point comparison.

    Returns:
        List of dicts with multiplier, actual_param_value, median, p10, p90.
    """
    if track_name not in scenario.track_configs:
        raise ValueError(f"Track '{track_name}' not configured in scenario.")

    results = []
    base_cfg = scenario.track_configs[track_name]
    base_val = getattr(base_cfg, param_name, None)
    if base_val is None:
        raise ValueError(f"TrackConfig has no parameter '{param_name}'.")

    for mult in multipliers:
        # Clone scenario to ensure no side effects
        cloned_sc = copy.deepcopy(scenario)
        new_cfg = cloned_sc.track_configs[track_name]
        perturbed_val = max(0.001, base_val * mult)
        setattr(new_cfg, param_name, perturbed_val)

        rng = np.random.default_rng(random_seed)
        res, skills_dict, _ = simulate_scenario(
            cloned_sc,
            time_horizon_weeks=time_horizon_weeks,
            iterations=iterations,
            rng=rng,
        )

        track_summary = res.track_summaries[track_name]
        results.append(
            {
                "multiplier": mult,
                "param_value": round(perturbed_val, 4),
                "median": track_summary.median,
                "p10": track_summary.p10,
                "p90": track_summary.p90,
            }
        )

    return results


def check_scenario_ranking_fragility(
    decision: Decision,
    scenarios: List[Scenario],
    target_track: str,
    param_name: str = "velocity_mean",
    perturbation_pct: float = 0.20,
    iterations: int = 500,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Test whether perturbing an assumption by +/- perturbation_pct reverses scenario rankings.

    If Scenario A is superior to Scenario B at baseline, but Scenario B surpasses
    Scenario A under a small 10-20% shift in assumptions, the recommendation is
    classified as 'fragile'.
    """
    if len(scenarios) < 2:
        raise ValueError("Ranking comparison requires at least 2 scenarios.")

    def get_medians_at(mult: float) -> Dict[str, float]:
        medians = {}
        for sc in scenarios:
            cloned_sc = copy.deepcopy(sc)
            if target_track in cloned_sc.track_configs:
                cfg = cloned_sc.track_configs[target_track]
                base_v = getattr(cfg, param_name)
                setattr(cfg, param_name, max(0.001, base_v * mult))

            rng = np.random.default_rng(random_seed)
            res, _, _ = simulate_scenario(
                cloned_sc,
                time_horizon_weeks=decision.time_horizon_weeks,
                iterations=iterations,
                rng=rng,
            )
            if target_track in res.track_summaries:
                medians[sc.id] = res.track_summaries[target_track].median
            else:
                medians[sc.id] = 0.0
        return medians

    baseline_medians = get_medians_at(1.0)
    low_medians = get_medians_at(1.0 - perturbation_pct)
    high_medians = get_medians_at(1.0 + perturbation_pct)

    # Rank scenario IDs descending
    baseline_ranking = sorted(baseline_medians.keys(), key=lambda sid: baseline_medians[sid], reverse=True)
    low_ranking = sorted(low_medians.keys(), key=lambda sid: low_medians[sid], reverse=True)
    high_ranking = sorted(high_medians.keys(), key=lambda sid: high_medians[sid], reverse=True)

    is_fragile = (baseline_ranking != low_ranking) or (baseline_ranking != high_ranking)

    return {
        "target_track": target_track,
        "parameter_varied": param_name,
        "perturbation_tested": perturbation_pct,
        "is_fragile": is_fragile,
        "baseline_ranking": [
            {"scenario_id": sid, "median": baseline_medians[sid]} for sid in baseline_ranking
        ],
        "low_ranking": [
            {"scenario_id": sid, "median": low_medians[sid]} for sid in low_ranking
        ],
        "high_ranking": [
            {"scenario_id": sid, "median": high_medians[sid]} for sid in high_ranking
        ],
    }
