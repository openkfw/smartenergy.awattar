"""Awattar state management"""

import logging

from awattar_api.awattar_api import AwattarApi
from datetime import datetime
from .const import (
    API,
    DOMAIN,
    INIT_STATE,
)

_LOGGER = logging.getLogger(__name__)


def init_state(
    url: str,
) -> dict[API:AwattarApi]:
    """
    Initialize the state with Awattar API.
    """

    return {
        API: AwattarApi(url),
    }


class StateFetcher:
    """Representation of the coordinator state handling. Whenever the coordinator is triggered,
    it will call the APIs and update status data."""

    coordinator = None

    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self):
        """Fetch Awattar forecast via API."""

        _LOGGER.debug("Updating the Awattar coordinator data...")

        awattar = self._hass.data[DOMAIN][INIT_STATE][API]
        data: dict = self.coordinator.data if self.coordinator.data else {}

        fetched_forecast: dict = await self._hass.async_add_executor_job(
            awattar.get_electricity_price
        )

        forecast_data = []

        for forecast_entry in fetched_forecast["data"]:
            # convert timestamp to human readable date
            forecast_data.append(
                {
                    "start_time": datetime.utcfromtimestamp(
                        forecast_entry["start_timestamp"] / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": datetime.utcfromtimestamp(
                        forecast_entry["end_timestamp"] / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "marketprice": forecast_entry["marketprice"],
                }
            )

        data["forecast"] = forecast_data
        _LOGGER.debug("Updated the Awattar coordinator data=%s", data)

        return data
