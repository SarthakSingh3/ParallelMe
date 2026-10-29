"""Unit tests for SQLite database persistence."""

import tempfile
from pathlib import Path

from parallelme.engine import run_simulation
from parallelme.models import Decision, Observation, Scenario, TrackConfig
from parallelme.persistence import Database


def test_sqlite_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path))

        # 1. Create and save decision
        sc1 = Scenario(name="DSA Track", allocations={"DSA": 15.0})
        sc2 = Scenario(name="AI Track", allocations={"AI": 15.0})
        decision = Decision(
            title="Summer Roadmap",
            description="Evaluating focus areas",
            time_horizon_weeks=10,
            max_weekly_hours=20.0,
            scenarios=[sc1, sc2],
        )

        db.save_decision(decision)

        # 2. Fetch decision
        fetched = db.get_decision(decision.id)
        assert fetched is not None
        assert fetched.title == "Summer Roadmap"
        assert len(fetched.scenarios) == 2

        # 3. Save simulation run
        run = run_simulation(decision, iterations=200, random_seed=42)
        db.save_run(run)

        fetched_run = db.get_run(run.id)
        assert fetched_run is not None
        assert fetched_run.iterations == 200
        assert fetched_run.random_seed == 42
        assert len(fetched_run.results) == 2

        # 4. Save and fetch observations
        obs = Observation(
            decision_id=decision.id,
            scenario_id=sc1.id,
            week_number=1,
            actual_hours={"DSA": 14.5},
            actual_units={"DSA": 15.0},
            notes="Good start",
        )
        db.save_observation(obs)

        obs_list = db.list_observations(decision.id)
        assert len(obs_list) == 1
        assert obs_list[0].week_number == 1
        assert obs_list[0].actual_hours["DSA"] == 14.5

        # 5. Delete decision (cascading delete)
        assert db.delete_decision(decision.id) is True
        assert db.get_decision(decision.id) is None
        assert len(db.list_runs(decision.id)) == 0
        assert len(db.list_observations(decision.id)) == 0
