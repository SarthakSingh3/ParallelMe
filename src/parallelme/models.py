"""Domain models for ParallelMe decision simulation and observation tracking.

These models represent decisions, alternative scenarios, simulation configurations,
aggregated outcome metrics, and empirical observations.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TrackConfig:
    """Configuration and distributional assumptions for a single skill track.

    Attributes:
        name: Skill track name (e.g. 'DSA', 'AI/ML').
        baseline_skill: Starting mastery units (>= 0.0).
        velocity_mean: Expected concepts/problems mastered per effective hour (> 0.0).
        velocity_sd: Standard deviation of velocity for lognormal, or spread (> 0.0).
        velocity_dist: Distribution family ('lognormal' or 'triangular').
        retention_decay: Fraction of accumulated skill lost per idle week (0.0 to 0.05).
        diminishing_returns: Non-linear decay factor as skill accumulates (>= 0.0).
    """

    name: str
    baseline_skill: float = 0.0
    velocity_mean: float = 1.0
    velocity_sd: float = 0.25
    velocity_dist: str = "lognormal"
    retention_decay: float = 0.01
    diminishing_returns: float = 0.005

    def to_dict(self) -> Dict[str, Any]:
        """Convert TrackConfig to a serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TrackConfig:
        """Create TrackConfig from dictionary."""
        return cls(
            name=str(data["name"]),
            baseline_skill=float(data.get("baseline_skill", 0.0)),
            velocity_mean=float(data.get("velocity_mean", 1.0)),
            velocity_sd=float(data.get("velocity_sd", 0.25)),
            velocity_dist=str(data.get("velocity_dist", "lognormal")),
            retention_decay=float(data.get("retention_decay", 0.01)),
            diminishing_returns=float(data.get("diminishing_returns", 0.005)),
        )


@dataclass
class Scenario:
    """An alternative course of action within a Decision.

    Attributes:
        id: Unique UUID string.
        decision_id: Associated Decision UUID string.
        name: Human-readable scenario name (e.g. '100% DSA Focus').
        description: Rationale and context for this alternative.
        allocations: Planned weekly hours per track, e.g. {'dsa': 15.0, 'ai': 0.0}.
        track_configs: Distribution assumptions per track name.
        target_thresholds: Target mastery benchmark per track, e.g. {'dsa': 100.0}.
        created_at: ISO 8601 UTC timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = ""
    name: str = ""
    description: str = ""
    allocations: Dict[str, float] = field(default_factory=dict)
    track_configs: Dict[str, TrackConfig] = field(default_factory=dict)
    target_thresholds: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def total_planned_hours(self) -> float:
        """Sum of all allocated weekly hours."""
        return sum(self.allocations.values())

    def to_dict(self) -> Dict[str, Any]:
        """Convert Scenario to a serializable dictionary."""
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "name": self.name,
            "description": self.description,
            "allocations": {k: float(v) for k, v in self.allocations.items()},
            "track_configs": {
                k: cfg.to_dict() if isinstance(cfg, TrackConfig) else cfg
                for k, cfg in self.track_configs.items()
            },
            "target_thresholds": {k: float(v) for k, v in self.target_thresholds.items()},
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Scenario:
        """Create Scenario from dictionary."""
        configs = {}
        for k, v in data.get("track_configs", {}).items():
            configs[k] = TrackConfig.from_dict(v) if isinstance(v, dict) else v

        return cls(
            id=str(data.get("id", str(uuid.uuid4()))),
            decision_id=str(data.get("decision_id", "")),
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            allocations={k: float(v) for k, v in data.get("allocations", {}).items()},
            track_configs=configs,
            target_thresholds={k: float(v) for k, v in data.get("target_thresholds", {}).items()},
            created_at=str(data.get("created_at", utc_now_iso())),
        )


@dataclass
class Decision:
    """The root decision context with a shared capacity budget and time horizon.

    Attributes:
        id: Unique UUID string.
        title: Short title (e.g. '90-Day Study Allocation').
        description: Problem context, goals, and constraints.
        time_horizon_weeks: Number of weeks for the planning period (1 to 52).
        max_weekly_hours: Maximum total hours/week available across all activities.
        scenarios: List of alternative scenarios.
        created_at: ISO 8601 UTC timestamp.
        updated_at: ISO 8601 UTC timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    time_horizon_weeks: int = 12
    max_weekly_hours: float = 20.0
    scenarios: List[Scenario] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Decision and child scenarios to serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "time_horizon_weeks": self.time_horizon_weeks,
            "max_weekly_hours": self.max_weekly_hours,
            "scenarios": [s.to_dict() for s in self.scenarios],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Decision:
        """Create Decision from dictionary."""
        scenarios = [
            Scenario.from_dict(s) if isinstance(s, dict) else s
            for s in data.get("scenarios", [])
        ]
        return cls(
            id=str(data.get("id", str(uuid.uuid4()))),
            title=str(data.get("title", "")),
            description=str(data.get("description", "")),
            time_horizon_weeks=int(data.get("time_horizon_weeks", 12)),
            max_weekly_hours=float(data.get("max_weekly_hours", 20.0)),
            scenarios=scenarios,
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass
class MetricSummary:
    """Descriptive statistics for a simulated outcome metric."""

    mean: float
    std: float
    median: float
    p10: float
    p25: float
    p75: float
    p90: float
    min_val: float
    max_val: float
    threshold_prob: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MetricSummary to dictionary."""
        return {
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "median": round(self.median, 4),
            "p10": round(self.p10, 4),
            "p25": round(self.p25, 4),
            "p75": round(self.p75, 4),
            "p90": round(self.p90, 4),
            "min_val": round(self.min_val, 4),
            "max_val": round(self.max_val, 4),
            "threshold_prob": round(self.threshold_prob, 4) if self.threshold_prob is not None else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetricSummary:
        """Create MetricSummary from dictionary."""
        return cls(
            mean=float(data["mean"]),
            std=float(data["std"]),
            median=float(data["median"]),
            p10=float(data["p10"]),
            p25=float(data["p25"]),
            p75=float(data["p75"]),
            p90=float(data["p90"]),
            min_val=float(data["min_val"]),
            max_val=float(data["max_val"]),
            threshold_prob=float(data["threshold_prob"]) if data.get("threshold_prob") is not None else None,
        )


@dataclass
class ScenarioResult:
    """Aggregated simulation output for a single scenario."""

    scenario_id: str
    scenario_name: str
    track_summaries: Dict[str, MetricSummary]
    total_hours_summary: MetricSummary

    def to_dict(self) -> Dict[str, Any]:
        """Convert ScenarioResult to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "track_summaries": {k: v.to_dict() for k, v in self.track_summaries.items()},
            "total_hours_summary": self.total_hours_summary.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScenarioResult:
        """Create ScenarioResult from dictionary."""
        return cls(
            scenario_id=str(data["scenario_id"]),
            scenario_name=str(data["scenario_name"]),
            track_summaries={
                k: MetricSummary.from_dict(v) for k, v in data["track_summaries"].items()
            },
            total_hours_summary=MetricSummary.from_dict(data["total_hours_summary"]),
        )


@dataclass
class SimulationRun:
    """Immutable snapshot of a completed simulation run."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = ""
    scenario_ids: List[str] = field(default_factory=list)
    iterations: int = 1000
    random_seed: int = 42
    snapshot_config: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, ScenarioResult] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        """Convert SimulationRun to dictionary."""
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "scenario_ids": self.scenario_ids,
            "iterations": self.iterations,
            "random_seed": self.random_seed,
            "snapshot_config": self.snapshot_config,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SimulationRun:
        """Create SimulationRun from dictionary."""
        return cls(
            id=str(data["id"]),
            decision_id=str(data["decision_id"]),
            scenario_ids=[str(s) for s in data.get("scenario_ids", [])],
            iterations=int(data["iterations"]),
            random_seed=int(data["random_seed"]),
            snapshot_config=dict(data.get("snapshot_config", {})),
            results={
                k: ScenarioResult.from_dict(v) for k, v in data.get("results", {}).items()
            },
            created_at=str(data.get("created_at", utc_now_iso())),
        )


@dataclass
class Observation:
    """An empirical observation recorded during real-world execution.

    Attributes:
        id: Unique observation UUID.
        decision_id: Associated decision.
        scenario_id: Active scenario being tracked.
        week_number: The week index (1 to T).
        actual_hours: Hours logged per track for that week.
        actual_units: Actual measurable units achieved for that week.
        notes: Qualitative notes, reflections, or external disruption logs.
        logged_at: ISO 8601 UTC timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = ""
    scenario_id: str = ""
    week_number: int = 1
    actual_hours: Dict[str, float] = field(default_factory=dict)
    actual_units: Dict[str, float] = field(default_factory=dict)
    notes: str = ""
    logged_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Observation to dictionary."""
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "scenario_id": self.scenario_id,
            "week_number": self.week_number,
            "actual_hours": {k: float(v) for k, v in self.actual_hours.items()},
            "actual_units": {k: float(v) for k, v in self.actual_units.items()},
            "notes": self.notes,
            "logged_at": self.logged_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Observation:
        """Create Observation from dictionary."""
        return cls(
            id=str(data.get("id", str(uuid.uuid4()))),
            decision_id=str(data["decision_id"]),
            scenario_id=str(data["scenario_id"]),
            week_number=int(data["week_number"]),
            actual_hours={k: float(v) for k, v in data.get("actual_hours", {}).items()},
            actual_units={k: float(v) for k, v in data.get("actual_units", {}).items()},
            notes=str(data.get("notes", "")),
            logged_at=str(data.get("logged_at", utc_now_iso())),
        )
