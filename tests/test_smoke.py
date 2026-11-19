"""Smoke tests verifying package metadata and environment setup."""

import archetype_symbolic


def test_package_version() -> None:
    assert archetype_symbolic.__version__ == "0.1.0"
