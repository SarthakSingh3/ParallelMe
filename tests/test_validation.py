"""Unit tests for input validation, edge cases, and constraints."""

import pytest

from parallelme.models import Decision, Observation, Scenario, TrackConfig
from parallelme.validation import (
    InfeasibleScenarioError,
    NumericSanityError,
    ValidationError,
    validate_decision,
    validate_observation,
    validate_scenario,
    validate_scenarios_for_comparison,
    validate_simulation_parameters,
    validate_track_config,
)


def test_empty_decision_title_rejected():
    d = Decision(title="")
    with pytest.raises(ValidationError, match="non-empty string"):
        validate_decision(d)


def test_negative_or_zero_time_horizon_rejected():
    d1 = Decision(title="Valid", time_horizon_weeks=0)
    with pytest.raises(NumericSanityError, match="must be positive"):
        validate_decision(d1)

    d2 = Decision(title="Valid", time_horizon_weeks=-5)
    with pytest.raises(NumericSanityError, match="must be positive"):
        validate_decision(d2)

    d3 = Decision(title="Valid", time_horizon_weeks=53)
    with pytest.raises(NumericSanityError, match="must not exceed 52 weeks"):
        validate_decision(d3)


def test_nan_or_infinite_budget_rejected():
    d_nan = Decision(title="Valid", max_weekly_hours=float("nan"))
    with pytest.raises(NumericSanityError, match="cannot be NaN"):
        validate_decision(d_nan)

    d_inf = Decision(title="Valid", max_weekly_hours=float("inf"))
    with pytest.raises(NumericSanityError, match="cannot be infinite"):
        validate_decision(d_inf)

    d_huge = Decision(title="Valid", max_weekly_hours=200.0)
    with pytest.raises(NumericSanityError, match="cannot exceed 168"):
        validate_decision(d_huge)


def test_scenario_budget_exceeded():
    decision = Decision(title="Test", max_weekly_hours=20.0)
    scenario = Scenario(name="Overloaded", allocations={"DSA": 15.0, "AI": 10.0})
    with pytest.raises(InfeasibleScenarioError, match="exceeds the shared decision budget"):
        validate_scenario(scenario, decision=decision)


def test_negative_hours_allocation_rejected():
    scenario = Scenario(name="Invalid", allocations={"DSA": -5.0})
    with pytest.raises(NumericSanityError, match="cannot be negative"):
        validate_scenario(scenario)


def test_track_config_invalid_distribution_rejected():
    cfg = TrackConfig(name="DSA", velocity_dist="unknown_dist")
    with pytest.raises(ValidationError, match="velocity_dist"):
        validate_track_config(cfg)


def test_comparison_requires_at_least_two_scenarios():
    decision = Decision(title="Test", max_weekly_hours=20.0)
    sc1 = Scenario(name="Option A", allocations={"DSA": 10.0})

    with pytest.raises(ValidationError, match="at least 2 alternative scenarios"):
        validate_scenarios_for_comparison([sc1], decision)


def test_duplicate_scenario_names_rejected():
    decision = Decision(title="Test", max_weekly_hours=20.0)
    sc1 = Scenario(name="DSA Focus", allocations={"DSA": 10.0})
    sc2 = Scenario(name="dsa focus", allocations={"DSA": 12.0})

    with pytest.raises(ValidationError, match="Duplicate scenario name"):
        validate_scenarios_for_comparison([sc1, sc2], decision)


def test_simulation_parameter_bounds():
    with pytest.raises(NumericSanityError, match="at least 100"):
        validate_simulation_parameters(iterations=50, random_seed=42)

    with pytest.raises(NumericSanityError, match="capped at 100,000"):
        validate_simulation_parameters(iterations=200_000, random_seed=42)

    with pytest.raises(NumericSanityError, match="non-negative"):
        validate_simulation_parameters(iterations=1000, random_seed=-1)


def test_observation_week_bounds():
    decision = Decision(title="Test", time_horizon_weeks=12)
    obs_zero = Observation(decision_id=decision.id, week_number=0)
    with pytest.raises(NumericSanityError, match="must be between 1 and 12"):
        validate_observation(obs_zero, decision)

    obs_overflow = Observation(decision_id=decision.id, week_number=13)
    with pytest.raises(NumericSanityError, match="must be between 1 and 12"):
        validate_observation(obs_overflow, decision)
