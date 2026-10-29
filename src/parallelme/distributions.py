"""Probability distribution samplers for stochastic simulation.

Wraps NumPy's modern Generator API with validated parameterizations
grounded in real-world productivity distributions.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np


def sample_schedule_factor(
    rng: np.random.Generator,
    size: Tuple[int, ...],
    left: float = 0.5,
    mode: float = 1.0,
    right: float = 1.1,
) -> np.ndarray:
    """Sample weekly schedule execution factor from a triangular distribution.

    A value of 1.0 indicates exact planned execution. Values < 1.0 represent
    time lost to external disruptions. Values > 1.0 represent surge weeks.
    """
    return rng.triangular(left=left, mode=mode, right=right, size=size)


def sample_velocity(
    rng: np.random.Generator,
    size: Tuple[int, ...],
    mean: float,
    sd: float,
    dist_family: str = "lognormal",
) -> np.ndarray:
    """Sample learning velocity (units mastered per effective hour).

    Supports:
        - 'lognormal': Positive, right-skewed distribution parameterized by
          expected value (mean) and standard deviation (sd).
        - 'triangular': Bounded asymmetric distribution around the mode.
    """
    if mean <= 0:
        raise ValueError("Velocity mean must be positive.")
    if sd <= 0:
        raise ValueError("Velocity standard deviation must be positive.")

    if dist_family == "lognormal":
        # Solve for underlying normal parameters mu and sigma
        variance = sd**2
        sigma_sq = math.log(1.0 + (variance / (mean**2)))
        sigma = math.sqrt(sigma_sq)
        mu = math.log(mean) - 0.5 * sigma_sq
        return rng.lognormal(mean=mu, sigma=sigma, size=size)

    elif dist_family == "triangular":
        left = max(0.05, mean - 1.5 * sd)
        right = mean + 1.5 * sd
        return rng.triangular(left=left, mode=mean, right=right, size=size)

    else:
        raise ValueError(f"Unsupported distribution family: {dist_family}")
