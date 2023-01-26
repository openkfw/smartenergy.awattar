"""Shelly Cloud state management"""

import logging

from green_energy_api.green_energy_api import GreenEnergyApi
from datetime import datetime
from .const import (
    API,
    DOMAIN,
    INIT_STATE,
)

_LOGGER = logging.getLogger(__name__)


def init_state(
    url: str,
) -> dict[API:GreenEnergyApi]:
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

    async def fetch_states(self):
        """Fetch green energy forecast via API."""

        _LOGGER.debug("Updating the GreenEnergy coordinator data...")

        green_energy = self._hass.data[DOMAIN][INIT_STATE][API]
        data: dict = self.coordinator.data if self.coordinator.data else {}

        fetched_forecast: dict = await self._hass.async_add_executor_job(
            green_energy.get_electricity_price
        )
        forecast_data = []
        for forecast_entry in fetched_forecast["data"]:
            # convert timestamp to human readable date
            timestamp = datetime.utcfromtimestamp(
                forecast_entry["start_timestamp"]
                / 1000  # unix timestamp in milliseconds
            ).strftime("%Y-%m-%d %H:%M:%S")
            forecast_data.append(
                {
                    timestamp: {
                        "timestamp": timestamp,
                        "marketprice": forecast_entry["marketprice"],
                    }
                }
            )

        data["forecast"]: list[dict[dict]] = forecast_data

        _LOGGER.debug("Updated the GreenEnergy coordinator data=%s", data)

        return data
