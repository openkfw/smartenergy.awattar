"""Shelly Cloud integration"""

import logging
from datetime import timedelta
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
)

from .const import (
    DOMAIN,
    GREEN_ENERGY_COORDINATOR,
    CONF_GREEN_ENERGY_URL,
    CONF_GREEN_ENERGY_FORECAST
)
from .state import StateFetcher, init_state

_LOGGER = logging.getLogger(__name__)

MIN_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)

# Configuration validation
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_GREEN_ENERGY_URL): vol.All(cv.string),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _setup_coordinator(
    state_fetcher_class: StateFetcher,
    scan_interval: timedelta,
    coordinator_name: str,
    hass: HomeAssistantType,
) -> DataUpdateCoordinator:
    _LOGGER.debug("Configuring coordinator=%s", coordinator_name)

    state_fetcher = state_fetcher_class(hass)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=state_fetcher.fetch_states,
        update_interval=scan_interval,
    )
    state_fetcher.coordinator = coordinator
    hass.data[DOMAIN][coordinator_name] = coordinator

    return coordinator


def _setup_apis(config: ConfigType, hass: HomeAssistantType) -> dict:
    green_energy_api = None

    if DOMAIN in config:
        hass.data[DOMAIN] = {}
        scan_interval = config[DOMAIN].get
        (CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        _LOGGER.debug("Scan interval set to=%s", scan_interval)

        url = config[DOMAIN].get(CONF_GREEN_ENERGY_URL)

        _LOGGER.debug(
            "Configuring API for the GreenEnergy url: '%s'",
            url,
        )
        green_energy_api = init_state(url)
    else:
        raise ValueError("Missing {DOMAIN} entry in the config")

    _LOGGER.debug("Configured GreenEnergy API")

    return green_energy_api


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up GreenEnergy platforms and services."""

    _LOGGER.debug("Setting up the GreenEnergy integration")

    scan_interval = DEFAULT_UPDATE_INTERVAL
    apis = _setup_apis(config, hass)
    hass.data[DOMAIN] = apis

    await _setup_coordinator(
        StateFetcher, scan_interval, GREEN_ENERGY_COORDINATOR, hass
    ).async_refresh()

    forecast_data: list[str] = hass.data
    [DOMAIN][GREEN_ENERGY_COORDINATOR].data["forecast"]

    # load platform with sensors
    hass.async_create_task(
        async_load_platform(
            hass,
            SENSOR_DOMAIN,
            DOMAIN,
            {
                CONF_GREEN_ENERGY_FORECAST: forecast_data,
            },
            config,
        )
    )

    _LOGGER.debug("Setup for the GreenEnergy integration completed")

    return True
