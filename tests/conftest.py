"""Shared fixtures."""

import pytest


@pytest.fixture(scope="session")
def wordnet():
    """Ensure oewn:2024 is available; auto-download on first use."""
    import wn
    try:
        return wn.Wordnet("oewn:2024")
    except wn.Error:
        wn.download("oewn:2024")
        return wn.Wordnet("oewn:2024")
