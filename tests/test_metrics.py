"""Unit tests for metric computation functions."""

import numpy as np
import pytest

from parallelme.metrics import compute_metric_summary


def test_compute_metric_summary_basic():
    arr = np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float64)
    summary = compute_metric_summary(arr, target_threshold=30.0)

    assert summary.mean == 30.0
    assert summary.median == 30.0
    assert summary.min_val == 10.0
    assert summary.max_val == 50.0
    assert summary.threshold_prob == pytest.approx(3 / 5)


def test_empty_array_raises():
    with pytest.raises(ValueError, match="Cannot compute metric summary on an empty array"):
        compute_metric_summary(np.array([], dtype=np.float64))


def test_single_element_array():
    arr = np.array([42.0])
    summary = compute_metric_summary(arr)
    assert summary.mean == 42.0
    assert summary.std == 0.0
    assert summary.median == 42.0
