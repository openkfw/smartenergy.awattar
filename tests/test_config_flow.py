"""Test the go-e Charger Cloud config flow and options flow."""

import pytest
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import (
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
    FlowResult,
)
from homeassistant.helpers.typing import HomeAssistantType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.smartenergy_awattar.const import DOMAIN

CONFIG_1: dict = {"country": "de", "scan_interval": 10}
CONFIG_2: dict = {"country": "at", "scan_interval": 20}
CONFIG_INVALID_INTERVAL_MIN: dict = {"country": "de", "scan_interval": -10}
CONFIG_INVALID_INTERVAL_MAX: dict = {"country": "de", "scan_interval": 60001}


async def _initialize_and_assert_flow(hass: HomeAssistantType) -> FlowResult:
    result_init = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result_init["type"] == RESULT_TYPE_FORM
    assert result_init["errors"] is None

    return result_init


async def _initialize_and_assert_options(
    hass: HomeAssistantType, data: dict
) -> FlowResult:
    config_entry = MockConfigEntry(
        domain=DOMAIN, unique_id="awattar", data=data, entry_id="test"
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result_init = await hass.config_entries.options.async_init(config_entry.entry_id)

    return result_init


async def _assert_invalid_scan_interval(
    flow_id: str,
    data: dict,
    configure_fn,
    err_msg: str,
) -> None:
    """Test an error is created when scan interval is invalid."""
    with pytest.raises(Exception) as exception_info:
        await configure_fn(
            flow_id,
            data,
        )
    assert str(exception_info.value) == err_msg


async def test_config_flow_init(hass: HomeAssistantType) -> None:
    """Test we can configure the integration via config flow."""
    with patch(
        f"custom_components.{DOMAIN}.state.AwattarApi.get_electricity_price",
        return_value={"data": []},
    ):
        result_init = await _initialize_and_assert_flow(hass)
        result_configure = await hass.config_entries.flow.async_configure(
            result_init["flow_id"],
            CONFIG_1,
        )
        await hass.async_block_till_done()

    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == "Awattar"
    assert result_configure["data"] == CONFIG_1


async def test_config_flow_invalid_scan_interval(hass: HomeAssistantType) -> None:
    """Test an error is created when scan interval is invalid."""
    with patch(
        f"custom_components.{DOMAIN}.state.AwattarApi.get_electricity_price",
        return_value={"data": []},
    ):
        result_init = await _initialize_and_assert_flow(hass)
    # min is 1
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CONFIG_INVALID_INTERVAL_MIN,
        hass.config_entries.flow.async_configure,
        "value must be at least 10 for dictionary value @ data['scan_interval']",
    )
    # max is 60000
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CONFIG_INVALID_INTERVAL_MAX,
        hass.config_entries.flow.async_configure,
        "value must be at most 60000 for dictionary value @ data['scan_interval']",
    )


async def test_options_flow_init(hass) -> None:
    """Test we can configure the integration via options flow."""
    with patch(
        f"custom_components.{DOMAIN}.state.AwattarApi.get_electricity_price",
        return_value={"data": []},
    ):
        result_init = await _initialize_and_assert_options(hass, CONFIG_1)

        result_configure = await hass.config_entries.options.async_configure(
            result_init["flow_id"],
            CONFIG_2,
        )

    assert result_configure["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result_configure["title"] == ""
    assert result_configure["result"] is True
    assert result_configure["data"] == CONFIG_2


async def test_options_flow_invalid_scan_interval(hass: HomeAssistantType) -> None:
    """Test an error is created when scan interval is invalid."""
    with patch(
        f"custom_components.{DOMAIN}.state.AwattarApi.get_electricity_price",
        return_value={"data": []},
    ):
        result_init = await _initialize_and_assert_options(hass, CONFIG_1)
    # min is 1
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CONFIG_INVALID_INTERVAL_MIN,
        hass.config_entries.options.async_configure,
        "value must be at least 10 for dictionary value @ data['scan_interval']",
    )
    # max is 60000
    await _assert_invalid_scan_interval(
        result_init["flow_id"],
        CONFIG_INVALID_INTERVAL_MAX,
        hass.config_entries.options.async_configure,
        "value must be at most 60000 for dictionary value @ data['scan_interval']",
    )
