"""Export and import utilities for ParallelMe decisions, runs, and observations.

Supports structured JSON export and tabular CSV summaries with strict
schema validation and error handling.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from parallelme.models import Decision, Observation, Scenario, SimulationRun
from parallelme.validation import ValidationError, validate_decision


def export_decision_to_json(decision: Decision) -> str:
    """Serialize a Decision and its scenarios to a formatted JSON string."""
    validate_decision(decision)
    return json.dumps(decision.to_dict(), indent=2)


def import_decision_from_json(json_content: Union[str, Path]) -> Decision:
    """Parse and validate a Decision from a JSON string or file path.

    Raises:
        ValidationError: If JSON is malformed or required schema attributes are missing.
    """
    if isinstance(json_content, Path) or (isinstance(json_content, str) and "\n" not in json_content and Path(json_content).is_file()):
        with open(json_content, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        raw_text = str(json_content)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}") from e

    if not isinstance(data, dict):
        raise ValidationError("JSON content must be a root object representing a Decision.")

    decision = Decision.from_dict(data)
    validate_decision(decision)
    return decision


def export_simulation_run_to_csv(run: SimulationRun) -> str:
    """Export aggregated scenario outcome metrics from a SimulationRun to CSV.

    Columns:
        scenario_id, scenario_name, track_name, mean, std, median, p10, p25, p75, p90, min, max, threshold_prob
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "scenario_id",
            "scenario_name",
            "metric_type",
            "track_or_resource",
            "mean",
            "std",
            "median",
            "p10",
            "p25",
            "p75",
            "p90",
            "min_val",
            "max_val",
            "threshold_prob",
        ]
    )

    for sc_id, result in run.results.items():
        # Write skill tracks
        for track_name, metric in result.track_summaries.items():
            writer.writerow(
                [
                    sc_id,
                    result.scenario_name,
                    "skill_mastery",
                    track_name,
                    metric.mean,
                    metric.std,
                    metric.median,
                    metric.p10,
                    metric.p25,
                    metric.p75,
                    metric.p90,
                    metric.min_val,
                    metric.max_val,
                    metric.threshold_prob if metric.threshold_prob is not None else "",
                ]
            )

        # Write total hours
        hrs = result.total_hours_summary
        writer.writerow(
            [
                sc_id,
                result.scenario_name,
                "resource_expenditure",
                "total_hours",
                hrs.mean,
                hrs.std,
                hrs.median,
                hrs.p10,
                hrs.p25,
                hrs.p75,
                hrs.p90,
                hrs.min_val,
                hrs.max_val,
                "",
            ]
        )

    return output.getvalue()


def export_observations_to_csv(observations: List[Observation]) -> str:
    """Export a list of empirical observations to tabular CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "observation_id",
            "decision_id",
            "scenario_id",
            "week_number",
            "actual_hours_json",
            "actual_units_json",
            "notes",
            "logged_at",
        ]
    )

    for obs in observations:
        writer.writerow(
            [
                obs.id,
                obs.decision_id,
                obs.scenario_id,
                obs.week_number,
                json.dumps(obs.actual_hours),
                json.dumps(obs.actual_units),
                obs.notes,
                obs.logged_at,
            ]
        )

    return output.getvalue()
