"""Sanity and environment verification tests."""

import parallelme


def test_package_version():
    """Verify package exposes expected version."""
    assert parallelme.__version__ == "0.1.0"
