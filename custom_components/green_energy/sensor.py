"""Platform for Shelly Cloud sensor integration."""
import logging

from abc import ABC, abstractmethod
from typing import Callable
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    DiscoveryInfoType,
)
from homeassistant.components.sensor import (
    SensorEntity,
    DOMAIN as SENSOR_DOMAIN,
)
from .const import (
    CONF_GREEN_ENERGY_FORECAST,
    GREEN_ENERGY_COORDINATOR,
    DOMAIN,
    MANUFACTURER,
    UNIT,
)

_LOGGER = logging.getLogger(__name__)


class BaseSensor(ABC):
    """Representation of a Base sensor."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        coordinator,
        entity_id,
        timestamp,
        marketprice,
    ):
        """Initialize the Base sensor."""
        super().__init__(coordinator)
        self._entity_id: str = entity_id
        self._timestamp: str = timestamp
        self._marketprice: float = marketprice
        self._name: str = timestamp
        self._unit: str = UNIT

    @property
    def name(self):
        """The name of the sensor is the timestamp."""
        return self._name

    @property
    @abstractmethod
    def state(self):
        """Return the state of the sensor."""

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit


class ForecastSensor(BaseSensor, CoordinatorEntity, SensorEntity):
    """Representation of a sensor on the forecast of the energy prices integration."""

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entity_id)},
            "name": self._timestamp,
            "manufacturer": MANUFACTURER,
            "model": "",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        for forecast_entry in self.coordinator.data["forecast"]:
            if self._timestamp in forecast_entry:
                return forecast_entry[self._timestamp]["marketprice"]


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def _setup_entities(
    forecast_data: list[dict],
    sensor_class: type,
    hass: HomeAssistantType,
    async_add_entities: Callable,
) -> list:
    for forecast_entry in forecast_data:
        timestamp = list(forecast_entry.keys())[0]
        marketprice = forecast_entry[timestamp]["marketprice"]
        _LOGGER.debug(
            "Creating card entry for %s with a price of %s Eur/MWh",
            forecast_entry[timestamp]["timestamp"],
            marketprice,
        )
        async_add_entities(
            [
                sensor_class(
                    hass.data[DOMAIN][GREEN_ENERGY_COORDINATOR],
                    f"{SENSOR_DOMAIN}.{DOMAIN}_forecast_{timestamp}",
                    timestamp,
                    marketprice,
                ),
            ]
        )


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType = None,
):
    """Set up Green Energy Sensor platform."""
    _LOGGER.debug("Setting up the Shelly Cloud sensor platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    forecast_data: list[dict] = discovery_info[CONF_GREEN_ENERGY_FORECAST]

    _setup_entities(
        forecast_data,
        ForecastSensor,
        hass,
        async_add_entities,
    )
