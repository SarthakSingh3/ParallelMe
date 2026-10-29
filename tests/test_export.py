"""Unit tests for JSON/CSV export and import."""

import pytest

from parallelme.engine import run_simulation
from parallelme.export import (
    export_decision_to_json,
    export_observations_to_csv,
    export_simulation_run_to_csv,
    import_decision_from_json,
)
from parallelme.models import Decision, Observation, Scenario
from parallelme.validation import ValidationError


def test_json_export_and_import_cycle():
    decision = Decision(
        title="Grad School vs Industry",
        time_horizon_weeks=16,
        max_weekly_hours=25.0,
        scenarios=[
            Scenario(name="Research", allocations={"Papers": 20.0}),
            Scenario(name="Internship", allocations={"Code": 20.0}),
        ],
    )

    json_str = export_decision_to_json(decision)
    assert "Grad School vs Industry" in json_str

    imported = import_decision_from_json(json_str)
    assert imported.id == decision.id
    assert imported.title == decision.title
    assert imported.time_horizon_weeks == 16
    assert len(imported.scenarios) == 2


def test_import_malformed_json_raises():
    with pytest.raises(ValidationError, match="Invalid JSON format"):
        import_decision_from_json("{broken json")


def test_csv_export_simulation_run():
    decision = Decision(
        title="Test CSV",
        time_horizon_weeks=6,
        max_weekly_hours=15.0,
        scenarios=[
            Scenario(name="Opt A", allocations={"Track1": 10.0}),
            Scenario(name="Opt B", allocations={"Track1": 12.0}),
        ],
    )
    run = run_simulation(decision, iterations=200, random_seed=42)
    csv_str = export_simulation_run_to_csv(run)

    assert "scenario_id,scenario_name,metric_type" in csv_str
    assert "Opt A" in csv_str
    assert "Opt B" in csv_str


def test_csv_export_observations():
    obs = [
        Observation(
            decision_id="d1",
            scenario_id="s1",
            week_number=1,
            actual_hours={"T1": 10.0},
            actual_units={"T1": 8.0},
            notes="Week 1 done",
        )
    ]
    csv_str = export_observations_to_csv(obs)
    assert "observation_id,decision_id,scenario_id" in csv_str
    assert "Week 1 done" in csv_str
