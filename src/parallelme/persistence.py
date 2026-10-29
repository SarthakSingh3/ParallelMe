"""Local SQLite persistence layer for decisions, scenarios, runs, and observations."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from parallelme.models import Decision, Observation, Scenario, SimulationRun


class Database:
    """SQLite database manager for ParallelMe."""

    def __init__(self, db_path: str = "parallelme.db"):
        self.db_path = str(Path(db_path).resolve()) if db_path != ":memory:" else ":memory:"
        self._init_schema()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that guarantees transaction commit and connection closure."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initialize required database tables if they do not exist."""
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    time_horizon_weeks INTEGER NOT NULL,
                    max_weekly_hours REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scenarios (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    allocations_json TEXT NOT NULL,
                    track_configs_json TEXT NOT NULL,
                    target_thresholds_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS simulation_runs (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    scenario_ids_json TEXT NOT NULL,
                    iterations INTEGER NOT NULL,
                    random_seed INTEGER NOT NULL,
                    snapshot_config_json TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    week_number INTEGER NOT NULL,
                    actual_hours_json TEXT NOT NULL,
                    actual_units_json TEXT NOT NULL,
                    notes TEXT,
                    logged_at TEXT NOT NULL,
                    FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_scenarios_decision_id ON scenarios(decision_id);
                CREATE INDEX IF NOT EXISTS idx_runs_decision_id ON simulation_runs(decision_id);
                CREATE INDEX IF NOT EXISTS idx_obs_decision_id ON observations(decision_id);
                """
            )

    # Decision CRUD
    def save_decision(self, decision: Decision) -> None:
        """Insert or replace a decision and its associated scenarios."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO decisions (id, title, description, time_horizon_weeks, max_weekly_hours, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    time_horizon_weeks=excluded.time_horizon_weeks,
                    max_weekly_hours=excluded.max_weekly_hours,
                    updated_at=excluded.updated_at;
                """,
                (
                    decision.id,
                    decision.title,
                    decision.description,
                    decision.time_horizon_weeks,
                    decision.max_weekly_hours,
                    decision.created_at,
                    decision.updated_at,
                ),
            )

            # Re-sync scenarios for this decision
            conn.execute("DELETE FROM scenarios WHERE decision_id = ?", (decision.id,))
            for sc in decision.scenarios:
                conn.execute(
                    """
                    INSERT INTO scenarios (id, decision_id, name, description, allocations_json, track_configs_json, target_thresholds_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        sc.id,
                        decision.id,
                        sc.name,
                        sc.description,
                        json.dumps(sc.allocations),
                        json.dumps({k: v.to_dict() for k, v in sc.track_configs.items()}),
                        json.dumps(sc.target_thresholds),
                        sc.created_at,
                    ),
                )

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Fetch a decision by ID including all child scenarios."""
        with self._connection() as conn:
            cur = conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
            row = cur.fetchone()
            if not row:
                return None

            sc_cur = conn.execute(
                "SELECT * FROM scenarios WHERE decision_id = ? ORDER BY created_at ASC",
                (decision_id,),
            )
            scenarios = []
            for sc_row in sc_cur.fetchall():
                scenarios.append(
                    Scenario.from_dict(
                        {
                            "id": sc_row["id"],
                            "decision_id": sc_row["decision_id"],
                            "name": sc_row["name"],
                            "description": sc_row["description"],
                            "allocations": json.loads(sc_row["allocations_json"]),
                            "track_configs": json.loads(sc_row["track_configs_json"]),
                            "target_thresholds": json.loads(sc_row["target_thresholds_json"]),
                            "created_at": sc_row["created_at"],
                        }
                    )
                )

            return Decision(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                time_horizon_weeks=row["time_horizon_weeks"],
                max_weekly_hours=row["max_weekly_hours"],
                scenarios=scenarios,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def list_decisions(self) -> List[Decision]:
        """List all decisions in the database."""
        with self._connection() as conn:
            cur = conn.execute("SELECT id FROM decisions ORDER BY updated_at DESC")
            decision_ids = [r["id"] for r in cur.fetchall()]

        decisions = []
        for did in decision_ids:
            d = self.get_decision(did)
            if d is not None:
                decisions.append(d)
        return decisions

    def delete_decision(self, decision_id: str) -> bool:
        """Delete a decision and all cascading scenarios, runs, and observations."""
        with self._connection() as conn:
            cur = conn.execute("DELETE FROM decisions WHERE id = ?", (decision_id,))
            return cur.rowcount > 0

    # Simulation Runs
    def save_run(self, run: SimulationRun) -> None:
        """Persist an immutable simulation run."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO simulation_runs (
                    id, decision_id, scenario_ids_json, iterations, random_seed,
                    snapshot_config_json, results_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run.id,
                    run.decision_id,
                    json.dumps(run.scenario_ids),
                    run.iterations,
                    run.random_seed,
                    json.dumps(run.snapshot_config),
                    json.dumps({k: v.to_dict() for k, v in run.results.items()}),
                    run.created_at,
                ),
            )

    def get_run(self, run_id: str) -> Optional[SimulationRun]:
        """Retrieve a saved simulation run."""
        with self._connection() as conn:
            cur = conn.execute("SELECT * FROM simulation_runs WHERE id = ?", (run_id,))
            row = cur.fetchone()
            if not row:
                return None
            return SimulationRun.from_dict(
                {
                    "id": row["id"],
                    "decision_id": row["decision_id"],
                    "scenario_ids": json.loads(row["scenario_ids_json"]),
                    "iterations": row["iterations"],
                    "random_seed": row["random_seed"],
                    "snapshot_config": json.loads(row["snapshot_config_json"]),
                    "results": json.loads(row["results_json"]),
                    "created_at": row["created_at"],
                }
            )

    def list_runs(self, decision_id: str) -> List[SimulationRun]:
        """List all historical runs for a decision."""
        with self._connection() as conn:
            cur = conn.execute(
                "SELECT id FROM simulation_runs WHERE decision_id = ? ORDER BY created_at DESC",
                (decision_id,),
            )
            run_ids = [r["id"] for r in cur.fetchall()]

        runs = []
        for rid in run_ids:
            r = self.get_run(rid)
            if r is not None:
                runs.append(r)
        return runs

    # Observations
    def save_observation(self, observation: Observation) -> None:
        """Save a weekly empirical observation."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO observations (
                    id, decision_id, scenario_id, week_number,
                    actual_hours_json, actual_units_json, notes, logged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    observation.id,
                    observation.decision_id,
                    observation.scenario_id,
                    observation.week_number,
                    json.dumps(observation.actual_hours),
                    json.dumps(observation.actual_units),
                    observation.notes,
                    observation.logged_at,
                ),
            )

    def list_observations(self, decision_id: str) -> List[Observation]:
        """List all empirical observations for a decision sorted by week."""
        with self._connection() as conn:
            cur = conn.execute(
                "SELECT * FROM observations WHERE decision_id = ? ORDER BY week_number ASC, logged_at ASC",
                (decision_id,),
            )
            observations = []
            for r in cur.fetchall():
                observations.append(
                    Observation.from_dict(
                        {
                            "id": r["id"],
                            "decision_id": r["decision_id"],
                            "scenario_id": r["scenario_id"],
                            "week_number": r["week_number"],
                            "actual_hours": json.loads(r["actual_hours_json"]),
                            "actual_units": json.loads(r["actual_units_json"]),
                            "notes": r["notes"],
                            "logged_at": r["logged_at"],
                        }
                    )
                )
            return observations

    def delete_observation(self, observation_id: str) -> bool:
        """Delete an observation by ID."""
        with self._connection() as conn:
            cur = conn.execute("DELETE FROM observations WHERE id = ?", (observation_id,))
            return cur.rowcount > 0
