"""Shelly Cloud state management"""

import logging

from green_energy.green_energy import GreenEnergyApi

from .const import (
    DOMAIN,
    API,
)

_LOGGER = logging.getLogger(__name__)


def init_state(url: str,) -> dict:
    """
    Initialize the state with Green Energy API.
    """

    return {
        API: GreenEnergyApi(url),
    }


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self) -> dict:
        """Fetch green energy forecast via API."""

        _LOGGER.debug("Updating the GreenEnergy coordinator data...")

        green_energy = self._hass.data[DOMAIN][API]
        data: dict = self.coordinator.data if self.coordinator.data else {}

        _LOGGER.debug("Current GreenEnergy coordinator data=%s", data)

        fetched_forecast: dict = await self._hass.async_add_executor_job(
            green_energy.get_electricity_price
        )

        data["forecast"] = fetched_forecast

        _LOGGER.debug("Updated the GreenEnergy coordinator data=%s", data)

        return data
