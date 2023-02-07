"""Fixtures for testing."""

import pytest


@pytest.fixture(autouse=True)
# pylint: disable=unused-argument
def auto_enable_custom_integrations(enable_custom_integrations):
    """
    Enable loading of custom integrations in tests.
    """
    yield
