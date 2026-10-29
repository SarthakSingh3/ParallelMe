"""Input validation and constraint enforcement for ParallelMe.

This module guarantees that no simulation runs on mathematically invalid,
infeasible, non-finite, or contradictory configurations.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Optional

from parallelme.models import Decision, Observation, Scenario, TrackConfig


class ValidationError(ValueError):
    """Base exception for all domain validation failures."""


class InfeasibleScenarioError(ValidationError):
    """Raised when a scenario violates physical or shared resource budgets."""


class NumericSanityError(ValidationError):
    """Raised when numbers are non-finite (NaN, inf, -inf) or out of sane bounds."""


def assert_finite_positive(val: float, name: str, allow_zero: bool = False, max_val: Optional[float] = None) -> None:
    """Validate that a float is finite, non-negative/positive, and below max_val."""
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        raise ValidationError(f"Parameter '{name}' must be a number, got {type(val).__name__}.")
    if math.isnan(val):
        raise NumericSanityError(f"Parameter '{name}' cannot be NaN.")
    if math.isinf(val):
        raise NumericSanityError(f"Parameter '{name}' cannot be infinite.")
    if allow_zero:
        if val < 0.0:
            raise NumericSanityError(f"Parameter '{name}' cannot be negative, got {val}.")
    else:
        if val <= 0.0:
            raise NumericSanityError(f"Parameter '{name}' must be strictly positive, got {val}.")
    if max_val is not None and val > max_val:
        raise NumericSanityError(f"Parameter '{name}' cannot exceed {max_val}, got {val}.")


def validate_decision(decision: Decision) -> None:
    """Validate top-level decision context.

    Raises:
        ValidationError: If title is empty or types are invalid.
        NumericSanityError: If numeric bounds are violated.
    """
    if not isinstance(decision.title, str) or not decision.title.strip():
        raise ValidationError("Decision 'title' must be a non-empty string.")

    if not isinstance(decision.time_horizon_weeks, int) or isinstance(decision.time_horizon_weeks, bool):
        raise ValidationError("Decision 'time_horizon_weeks' must be an integer.")
    if decision.time_horizon_weeks <= 0:
        raise NumericSanityError(
            f"Decision 'time_horizon_weeks' must be positive, got {decision.time_horizon_weeks}."
        )
    if decision.time_horizon_weeks > 52:
        raise NumericSanityError(
            f"Decision 'time_horizon_weeks' must not exceed 52 weeks (1 year), got {decision.time_horizon_weeks}."
        )

    assert_finite_positive(
        decision.max_weekly_hours,
        name="max_weekly_hours",
        allow_zero=False,
        max_val=168.0,  # 7 days * 24 hours
    )


def validate_track_config(config: TrackConfig) -> None:
    """Validate individual skill track distributional assumptions."""
    if not isinstance(config.name, str) or not config.name.strip():
        raise ValidationError("TrackConfig 'name' must be a non-empty string.")

    assert_finite_positive(config.baseline_skill, "baseline_skill", allow_zero=True, max_val=100_000.0)
    assert_finite_positive(config.velocity_mean, "velocity_mean", allow_zero=False, max_val=100.0)
    assert_finite_positive(config.velocity_sd, "velocity_sd", allow_zero=False, max_val=50.0)

    if config.velocity_dist not in {"lognormal", "triangular"}:
        raise ValidationError(
            f"TrackConfig 'velocity_dist' must be 'lognormal' or 'triangular', got '{config.velocity_dist}'."
        )

    assert_finite_positive(config.retention_decay, "retention_decay", allow_zero=True, max_val=1.0)
    assert_finite_positive(config.diminishing_returns, "diminishing_returns", allow_zero=True, max_val=1.0)


def validate_scenario(scenario: Scenario, decision: Optional[Decision] = None) -> None:
    """Validate a single scenario's integrity and budget adherence."""
    if not isinstance(scenario.name, str) or not scenario.name.strip():
        raise ValidationError("Scenario 'name' must be a non-empty string.")

    if not scenario.allocations:
        raise ValidationError(f"Scenario '{scenario.name}' must define at least one track allocation.")

    total_allocated = 0.0
    for track_name, hours in scenario.allocations.items():
        if not isinstance(track_name, str) or not track_name.strip():
            raise ValidationError("Track name in scenario allocations cannot be empty.")
        assert_finite_positive(hours, f"allocation['{track_name}']", allow_zero=True, max_val=168.0)
        total_allocated += hours

    for track_name, cfg in scenario.track_configs.items():
        validate_track_config(cfg)

    for track_name, threshold in scenario.target_thresholds.items():
        assert_finite_positive(threshold, f"target_threshold['{track_name}']", allow_zero=False)

    if decision is not None:
        if total_allocated > decision.max_weekly_hours + 1e-9:
            raise InfeasibleScenarioError(
                f"Scenario '{scenario.name}' allocates {total_allocated:.2f} hrs/week, "
                f"which exceeds the shared decision budget of {decision.max_weekly_hours:.2f} hrs/week."
            )


def validate_scenarios_for_comparison(scenarios: List[Scenario], decision: Decision) -> None:
    """Validate a collection of scenarios prepared for fair comparison."""
    validate_decision(decision)

    if not isinstance(scenarios, list) or len(scenarios) < 2:
        raise ValidationError(
            f"Decision comparison requires at least 2 alternative scenarios, got {len(scenarios) if isinstance(scenarios, list) else 0}."
        )

    seen_ids = set()
    seen_names = set()
    for s in scenarios:
        if s.id in seen_ids:
            raise ValidationError(f"Duplicate scenario ID detected: '{s.id}'.")
        seen_ids.add(s.id)

        clean_name = s.name.strip().lower()
        if clean_name in seen_names:
            raise ValidationError(f"Duplicate scenario name detected: '{s.name}'. Names must be unique.")
        seen_names.add(clean_name)

        validate_scenario(s, decision=decision)


def validate_simulation_parameters(iterations: int, random_seed: int) -> None:
    """Validate simulation execution settings."""
    if not isinstance(iterations, int) or isinstance(iterations, bool):
        raise ValidationError("Iterations must be an integer.")
    if iterations < 100:
        raise NumericSanityError(f"Iterations must be at least 100 for stable statistics, got {iterations}.")
    if iterations > 100_000:
        raise NumericSanityError(f"Iterations capped at 100,000 to prevent memory exhaustion, got {iterations}.")

    if not isinstance(random_seed, int) or isinstance(random_seed, bool):
        raise ValidationError("Random seed must be an integer.")
    if random_seed < 0:
        raise NumericSanityError(f"Random seed must be a non-negative integer, got {random_seed}.")


def validate_observation(observation: Observation, decision: Decision) -> None:
    """Validate an empirical observation against decision constraints."""
    if not isinstance(observation.week_number, int) or isinstance(observation.week_number, bool):
        raise ValidationError("Observation 'week_number' must be an integer.")
    if observation.week_number < 1 or observation.week_number > decision.time_horizon_weeks:
        raise NumericSanityError(
            f"Observation 'week_number' must be between 1 and {decision.time_horizon_weeks}, "
            f"got {observation.week_number}."
        )

    for track, hours in observation.actual_hours.items():
        assert_finite_positive(hours, f"actual_hours['{track}']", allow_zero=True, max_val=168.0)

    for track, units in observation.actual_units.items():
        assert_finite_positive(units, f"actual_units['{track}']", allow_zero=True, max_val=100_000.0)
