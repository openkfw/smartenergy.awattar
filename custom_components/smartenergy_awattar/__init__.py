"""Awattar integration"""

import logging
from datetime import timedelta
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_HOST
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
)
from awattar_api.awattar_api import AwattarApi

from .const import (
    API,
    DOMAIN,
    INIT_STATE,
    AWATTAR_COORDINATOR,
)
from .state import StateFetcher, init_state

_LOGGER: logging.Logger = logging.getLogger(__name__)

MIN_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL: timedelta = timedelta(seconds=10)

# Configuration validation
CONFIG_SCHEMA: vol.Schema = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(cv.string),
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
    awattar_api: dict[API:AwattarApi] = None

    if DOMAIN in config:
        hass.data[DOMAIN] = {}

        url = config[DOMAIN].get(CONF_HOST)

        _LOGGER.debug(
            "Configuring API for the Awattar url: '%s'",
            url,
        )
        awattar_api = init_state(url)
    else:
        _LOGGER.warning("Missing %s entry in the config", DOMAIN)

    _LOGGER.debug("Configured Awattar API")

    return awattar_api


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up Awattar platforms and services."""

    _LOGGER.debug("Setting up the Awattar integration")

    hass.data[DOMAIN] = hass.data[DOMAIN] if DOMAIN in hass.data else {}
    scan_interval: timedelta = DEFAULT_UPDATE_INTERVAL

    api: dict[API:AwattarApi] = _setup_apis(config, hass)
    hass.data[DOMAIN][INIT_STATE] = api

    await _setup_coordinator(
        StateFetcher, scan_interval, AWATTAR_COORDINATOR, hass
    ).async_refresh()

    # load platform with sensors
    hass.async_create_task(
        async_load_platform(
            hass,
            SENSOR_DOMAIN,
            DOMAIN,
            {},
            config,
        )
    )

    _LOGGER.debug("Setup for the Awattar integration completed")

    return True
