"""Fixtures for testing."""

import pytest
from typing import Generator


@pytest.fixture(autouse=True)
# pylint: disable=unused-argument
def auto_enable_custom_integrations(
    enable_custom_integrations: bool,
) -> Generator[None, None, None]:
    """
    Enable loading of custom integrations in tests.
    """
    yield
