"""Unit tests for the vectorized Monte Carlo simulation engine."""

import time
import numpy as np
import pytest

from parallelme.engine import run_simulation, simulate_scenario
from parallelme.models import Decision, Scenario, TrackConfig
from parallelme.validation import InfeasibleScenarioError


def test_simulation_determinism_with_same_seed():
    """Identical seed and inputs must yield bitwise identical outcomes."""
    sc = Scenario(
        name="DSA Focus",
        allocations={"DSA": 15.0},
        track_configs={"DSA": TrackConfig(name="DSA", velocity_mean=1.2, velocity_sd=0.2)},
    )

    rng1 = np.random.default_rng(42)
    res1, skills1, hrs1 = simulate_scenario(sc, time_horizon_weeks=12, iterations=1000, rng=rng1)

    rng2 = np.random.default_rng(42)
    res2, skills2, hrs2 = simulate_scenario(sc, time_horizon_weeks=12, iterations=1000, rng=rng2)

    np.testing.assert_array_equal(skills1["DSA"], skills2["DSA"])
    np.testing.assert_array_equal(hrs1, hrs2)
    assert res1.track_summaries["DSA"].median == res2.track_summaries["DSA"].median
    assert res1.track_summaries["DSA"].p10 == res2.track_summaries["DSA"].p10
    assert res1.track_summaries["DSA"].p90 == res2.track_summaries["DSA"].p90


def test_simulation_divergence_with_different_seeds():
    """Different seeds must generate distinct stochastic paths."""
    sc = Scenario(
        name="DSA Focus",
        allocations={"DSA": 15.0},
        track_configs={"DSA": TrackConfig(name="DSA", velocity_mean=1.2, velocity_sd=0.2)},
    )

    rng1 = np.random.default_rng(42)
    _, skills1, _ = simulate_scenario(sc, time_horizon_weeks=12, iterations=1000, rng=rng1)

    rng2 = np.random.default_rng(999)
    _, skills2, _ = simulate_scenario(sc, time_horizon_weeks=12, iterations=1000, rng=rng2)

    assert not np.array_equal(skills1["DSA"], skills2["DSA"])


def test_more_hours_yields_higher_median_skill():
    """More allocated study time should monotonically increase median skill."""
    cfg = TrackConfig(name="DSA", velocity_mean=1.0, velocity_sd=0.1)

    sc_low = Scenario(name="Low", allocations={"DSA": 5.0}, track_configs={"DSA": cfg})
    sc_high = Scenario(name="High", allocations={"DSA": 15.0}, track_configs={"DSA": cfg})

    rng = np.random.default_rng(42)
    res_low, _, _ = simulate_scenario(sc_low, time_horizon_weeks=12, iterations=1000, rng=rng)

    rng = np.random.default_rng(42)
    res_high, _, _ = simulate_scenario(sc_high, time_horizon_weeks=12, iterations=1000, rng=rng)

    assert res_high.track_summaries["DSA"].median > res_low.track_summaries["DSA"].median


def test_zero_hours_causes_retention_decay():
    """Zero allocated hours should result in exponential retention decay."""
    cfg = TrackConfig(name="DSA", baseline_skill=100.0, retention_decay=0.05)
    sc = Scenario(name="Idle", allocations={"DSA": 0.0}, track_configs={"DSA": cfg})

    rng = np.random.default_rng(42)
    res, skills, _ = simulate_scenario(sc, time_horizon_weeks=10, iterations=500, rng=rng)

    # 100 * (1 - 0.05)^10 approx 59.87
    median_final = res.track_summaries["DSA"].median
    assert median_final < 100.0
    assert 58.0 < median_final < 62.0


def test_threshold_attainment_calculation():
    """Threshold probability should correctly measure proportion reaching benchmark."""
    cfg = TrackConfig(name="DSA", baseline_skill=0.0, velocity_mean=2.0, velocity_sd=0.1)
    # 10 hrs/week * 10 weeks * ~2.0 velocity with diminishing returns = ~128 units
    sc = Scenario(
        name="Study",
        allocations={"DSA": 10.0},
        track_configs={"DSA": cfg},
        target_thresholds={"DSA": 100.0},
    )

    rng = np.random.default_rng(42)
    res, _, _ = simulate_scenario(sc, time_horizon_weeks=10, iterations=1000, rng=rng)

    prob = res.track_summaries["DSA"].threshold_prob
    assert prob is not None
    assert prob > 0.90  # Almost all should achieve >= 100 units


def test_full_decision_simulation_run_execution():
    decision = Decision(
        title="DSA vs AI",
        time_horizon_weeks=8,
        max_weekly_hours=20.0,
        scenarios=[
            Scenario(name="Pure DSA", allocations={"DSA": 18.0}),
            Scenario(name="Pure AI", allocations={"AI": 18.0}),
        ],
    )

    run = run_simulation(decision, iterations=500, random_seed=42)
    assert len(run.results) == 2
    assert run.iterations == 500
    assert run.random_seed == 42


def test_infeasible_scenario_in_decision_halts_simulation():
    decision = Decision(
        title="Overbooked",
        max_weekly_hours=15.0,
        scenarios=[
            Scenario(name="Fine", allocations={"DSA": 10.0}),
            Scenario(name="Too Heavy", allocations={"DSA": 25.0}),
        ],
    )

    with pytest.raises(InfeasibleScenarioError):
        run_simulation(decision, iterations=500, random_seed=42)


def test_simulation_execution_performance():
    """Ensure vectorized NumPy Monte Carlo engine is fast (< 300ms for 5000 iterations)."""
    sc = Scenario(
        name="Perf Test",
        allocations={"DSA": 10.0, "AI": 10.0},
        track_configs={
            "DSA": TrackConfig(name="DSA", velocity_mean=1.0),
            "AI": TrackConfig(name="AI", velocity_mean=1.0),
        },
    )

    rng = np.random.default_rng(42)
    start_time = time.perf_counter()
    simulate_scenario(sc, time_horizon_weeks=12, iterations=5000, rng=rng)
    elapsed = time.perf_counter() - start_time

    assert elapsed < 0.30, f"Simulation took too long: {elapsed:.4f}s"
