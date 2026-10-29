"""Additional edge-case tests to maximize branch coverage across all modules."""

import math
from pathlib import Path
import tempfile
import numpy as np
import pytest

from parallelme.distributions import sample_velocity
from parallelme.export import import_decision_from_json
from parallelme.models import Decision, Observation, Scenario, TrackConfig
from parallelme.persistence import Database
from parallelme.sensitivity import check_scenario_ranking_fragility, run_parameter_sweep
from parallelme.validation import (
    InfeasibleScenarioError,
    NumericSanityError,
    ValidationError,
    assert_finite_positive,
    validate_decision,
    validate_observation,
    validate_scenario,
    validate_scenarios_for_comparison,
    validate_simulation_parameters,
    validate_track_config,
)


def test_distributions_edge_cases():
    rng = np.random.default_rng(42)

    # Triangular sampling
    v_tri = sample_velocity(rng, size=(100,), mean=2.0, sd=0.5, dist_family="triangular")
    assert v_tri.shape == (100,)
    assert np.all(v_tri > 0)

    # Invalid mean / sd
    with pytest.raises(ValueError, match="mean must be positive"):
        sample_velocity(rng, size=(10,), mean=0.0, sd=0.5)

    with pytest.raises(ValueError, match="standard deviation must be positive"):
        sample_velocity(rng, size=(10,), mean=1.0, sd=-0.5)

    with pytest.raises(ValueError, match="Unsupported distribution family"):
        sample_velocity(rng, size=(10,), mean=1.0, sd=0.5, dist_family="cauchy")


def test_validation_type_checks():
    # Boolean masquerading as int/float
    with pytest.raises(ValidationError, match="must be a number"):
        assert_finite_positive(True, name="test_bool")

    # String passed to assert_finite_positive
    with pytest.raises(ValidationError, match="must be a number"):
        assert_finite_positive("123", name="test_str")

    # Decision boolean horizon
    with pytest.raises(ValidationError, match="must be an integer"):
        validate_decision(Decision(title="Test", time_horizon_weeks=True))

    # Decision non-string title
    with pytest.raises(ValidationError, match="non-empty string"):
        validate_decision(Decision(title=123))

    # Empty scenario name
    with pytest.raises(ValidationError, match="must be a non-empty string"):
        validate_scenario(Scenario(name="", allocations={"DSA": 5.0}))

    # Empty allocations in scenario
    with pytest.raises(ValidationError, match="must define at least one track allocation"):
        validate_scenario(Scenario(name="Empty", allocations={}))

    # Empty track name in scenario allocations
    with pytest.raises(ValidationError, match="Track name.*cannot be empty"):
        validate_scenario(Scenario(name="EmptyKey", allocations={"": 5.0}))

    # TrackConfig empty name
    with pytest.raises(ValidationError, match="non-empty string"):
        validate_track_config(TrackConfig(name=""))


def test_persistence_extended():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "ext.db"
        db = Database(str(db_path))

        d1 = Decision(title="Decision 1", max_weekly_hours=10.0, scenarios=[Scenario(name="S1", allocations={"T": 5.0})])
        d2 = Decision(title="Decision 2", max_weekly_hours=15.0, scenarios=[Scenario(name="S2", allocations={"T": 5.0})])
        db.save_decision(d1)
        db.save_decision(d2)

        # List decisions
        all_decs = db.list_decisions()
        assert len(all_decs) == 2

        # Delete observation
        obs = Observation(decision_id=d1.id, scenario_id="S1", week_number=1, actual_hours={"T": 4.0})
        db.save_observation(obs)
        assert len(db.list_observations(d1.id)) == 1

        db.delete_observation(obs.id)
        assert len(db.list_observations(d1.id)) == 0


def test_export_from_file_path():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding="utf-8") as f:
        f.write('{"id": "test", "title": "From File", "time_horizon_weeks": 4, "max_weekly_hours": 10.0, "scenarios": []}')
        f_path = f.name

    imported = import_decision_from_json(Path(f_path))
    assert imported.title == "From File"

    # Non-dict JSON root
    with pytest.raises(ValidationError, match="must be a root object"):
        import_decision_from_json("[1, 2, 3]")


def test_sensitivity_error_branches():
    sc = Scenario(name="S", allocations={"A": 10.0}, track_configs={"A": TrackConfig(name="A")})

    # Unknown track
    with pytest.raises(ValueError, match="not configured"):
        run_parameter_sweep(sc, 4, "NonExistent", "velocity_mean", [1.0])

    # Unknown param
    with pytest.raises(ValueError, match="has no parameter"):
        run_parameter_sweep(sc, 4, "A", "invalid_param_name", [1.0])

    # Ranking fragility with < 2 scenarios
    d = Decision(title="D")
    with pytest.raises(ValueError, match="requires at least 2 scenarios"):
        check_scenario_ranking_fragility(d, [sc], "A")
