"""Unit tests for ParallelMe domain data models."""

from parallelme.models import (
    Decision,
    MetricSummary,
    Observation,
    Scenario,
    ScenarioResult,
    SimulationRun,
    TrackConfig,
)


def test_track_config_roundtrip():
    cfg = TrackConfig(
        name="DSA",
        baseline_skill=10.0,
        velocity_mean=1.5,
        velocity_sd=0.3,
        velocity_dist="lognormal",
        retention_decay=0.02,
        diminishing_returns=0.01,
    )
    d = cfg.to_dict()
    assert d["name"] == "DSA"
    assert d["baseline_skill"] == 10.0

    restored = TrackConfig.from_dict(d)
    assert restored.name == cfg.name
    assert restored.baseline_skill == cfg.baseline_skill
    assert restored.velocity_mean == cfg.velocity_mean
    assert restored.velocity_sd == cfg.velocity_sd
    assert restored.velocity_dist == cfg.velocity_dist


def test_scenario_roundtrip():
    cfg = TrackConfig(name="DSA", velocity_mean=2.0)
    sc = Scenario(
        name="Intensive DSA",
        description="Full-time DSA prep",
        allocations={"DSA": 15.0},
        track_configs={"DSA": cfg},
        target_thresholds={"DSA": 100.0},
    )
    assert sc.total_planned_hours == 15.0

    d = sc.to_dict()
    restored = Scenario.from_dict(d)
    assert restored.name == "Intensive DSA"
    assert restored.allocations["DSA"] == 15.0
    assert restored.track_configs["DSA"].velocity_mean == 2.0
    assert restored.target_thresholds["DSA"] == 100.0


def test_decision_roundtrip():
    sc1 = Scenario(name="Plan A", allocations={"DSA": 10.0})
    sc2 = Scenario(name="Plan B", allocations={"DSA": 5.0, "AI": 5.0})
    decision = Decision(
        title="Q1 Learning Focus",
        description="Choose between pure DSA and split focus",
        time_horizon_weeks=12,
        max_weekly_hours=15.0,
        scenarios=[sc1, sc2],
    )

    d = decision.to_dict()
    restored = Decision.from_dict(d)
    assert restored.title == "Q1 Learning Focus"
    assert len(restored.scenarios) == 2
    assert restored.scenarios[0].name == "Plan A"
    assert restored.scenarios[1].name == "Plan B"


def test_metric_summary_roundtrip():
    m = MetricSummary(
        mean=50.5,
        std=4.2,
        median=50.1,
        p10=45.0,
        p25=48.0,
        p75=53.0,
        p90=56.0,
        min_val=38.0,
        max_val=64.0,
        threshold_prob=0.85,
    )
    d = m.to_dict()
    restored = MetricSummary.from_dict(d)
    assert restored.median == 50.1
    assert restored.threshold_prob == 0.85


def test_observation_roundtrip():
    obs = Observation(
        decision_id="dec-123",
        scenario_id="sc-456",
        week_number=3,
        actual_hours={"DSA": 12.5},
        actual_units={"DSA": 14.0},
        notes="Minor sickness on Thursday",
    )
    d = obs.to_dict()
    restored = Observation.from_dict(d)
    assert restored.week_number == 3
    assert restored.actual_hours["DSA"] == 12.5
    assert restored.notes == "Minor sickness on Thursday"
