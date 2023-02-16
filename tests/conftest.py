"""Fixtures for testing."""

from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
# pylint: disable=unused-argument
def auto_enable_custom_integrations(
    enable_custom_integrations: bool,
) -> Generator[None, None, None]:
    """Enable loading of custom integrations in tests."""
    yield
