"""Platform for Awattar sensor integration."""
import logging
from abc import ABC
from typing import Callable

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import AWATTAR_COORDINATOR, DOMAIN, MANUFACTURER, UNIT

_LOGGER = logging.getLogger(__name__)


class BaseSensor(ABC):
    """Representation of a Base sensor."""

    def __init__(
        self,
        coordinator,
        entity_id,
    ):
        """Initialize the Base sensor."""
        super().__init__(coordinator)
        self._entity_id: str = entity_id
        self._name: str = "Awattar forecast"
        self._unit: str = UNIT

    @property
    def name(self):
        """The name of the sensor is the timestamp."""
        return self._name

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
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "model": "",
        }

    @property
    def capability_attributes(self):
        """Update the value of the entity."""
        forecast = self.coordinator.data["forecast"]
        return {
            "forecast": forecast,
        }


def _setup_entities(
    hass: HomeAssistantType,
    async_add_entities: Callable,
) -> list:
    async_add_entities(
        [
            ForecastSensor(
                hass.data[DOMAIN][AWATTAR_COORDINATOR],
                f"{SENSOR_DOMAIN}.{DOMAIN}_forecast",
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
    """Set up Awattar Sensor platform."""
    _LOGGER.debug("Setting up the Awattar sensor platform")

    if discovery_info is None:
        _LOGGER.error("Missing discovery_info, skipping setup")
        return

    _setup_entities(hass, async_add_entities)
