"""Statistical metric computation for simulation outcome arrays."""

from __future__ import annotations

from typing import Optional

import numpy as np

from parallelme.models import MetricSummary


def compute_metric_summary(
    values: np.ndarray,
    target_threshold: Optional[float] = None,
) -> MetricSummary:
    """Compute summary statistics for a 1D array of simulated outcome values.

    Args:
        values: 1D NumPy array of simulated final values across N iterations.
        target_threshold: Optional benchmark value to evaluate probability of attainment.

    Returns:
        MetricSummary containing mean, std, median, percentiles, min, max, and threshold probability.
    """
    if values.size == 0:
        raise ValueError("Cannot compute metric summary on an empty array.")

    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if values.size > 1 else 0.0
    median = float(np.median(values))

    # Percentiles: 10th, 25th, 75th, 90th
    p10 = float(np.percentile(values, 10))
    p25 = float(np.percentile(values, 25))
    p75 = float(np.percentile(values, 75))
    p90 = float(np.percentile(values, 90))

    min_val = float(np.min(values))
    max_val = float(np.max(values))

    threshold_prob = None
    if target_threshold is not None:
        threshold_prob = float(np.mean(values >= target_threshold))

    return MetricSummary(
        mean=mean,
        std=std,
        median=median,
        p10=p10,
        p25=p25,
        p75=p75,
        p90=p90,
        min_val=min_val,
        max_val=max_val,
        threshold_prob=threshold_prob,
    )
