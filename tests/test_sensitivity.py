"""Unit tests for sensitivity and ranking fragility analysis."""

from parallelme.models import Decision, Scenario, TrackConfig
from parallelme.sensitivity import check_scenario_ranking_fragility, run_parameter_sweep


def test_parameter_sweep_monotonic_velocity():
    sc = Scenario(
        name="DSA Focus",
        allocations={"DSA": 15.0},
        track_configs={"DSA": TrackConfig(name="DSA", velocity_mean=1.0)},
    )

    multipliers = [0.8, 1.0, 1.2]
    sweep_results = run_parameter_sweep(
        scenario=sc,
        time_horizon_weeks=8,
        track_name="DSA",
        param_name="velocity_mean",
        multipliers=multipliers,
        iterations=300,
        random_seed=42,
    )

    assert len(sweep_results) == 3
    # Check that median increases as velocity multiplier increases
    assert sweep_results[0]["median"] < sweep_results[1]["median"] < sweep_results[2]["median"]


def test_ranking_fragility_detection():
    decision = Decision(
        title="DSA vs AI Fragility",
        time_horizon_weeks=8,
        max_weekly_hours=20.0,
        scenarios=[
            Scenario(
                name="S1 High Hours Low Velocity",
                allocations={"DSA": 18.0},
                track_configs={"DSA": TrackConfig(name="DSA", velocity_mean=0.8)},
            ),
            Scenario(
                name="S2 Low Hours High Velocity",
                allocations={"DSA": 10.0},
                track_configs={"DSA": TrackConfig(name="DSA", velocity_mean=1.5)},
            ),
        ],
    )

    fragility_report = check_scenario_ranking_fragility(
        decision=decision,
        scenarios=decision.scenarios,
        target_track="DSA",
        param_name="velocity_mean",
        perturbation_pct=0.30,
        iterations=300,
        random_seed=42,
    )

    assert "is_fragile" in fragility_report
    assert "baseline_ranking" in fragility_report
