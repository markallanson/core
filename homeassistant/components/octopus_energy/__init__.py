"""The Octopus Energy integration."""
import asyncio
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .config_flow import OctopusEnergyConfigError

from .const import DOMAIN, ERR_NO_METERS, CONF_ACCOUNT_ID, CONF_API_KEY, PLATFORM
from .service import HaasOctopusEnergyClientWrapper
from ...exceptions import ConfigEntryNotReady

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Octopus Energy component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Octopus Energy from a config entry."""
    try:
        client_wrapper = HaasOctopusEnergyClientWrapper(
            entry.data[CONF_ACCOUNT_ID], entry.data[CONF_API_KEY]
        )
        await client_wrapper.validate_login()
    except:
        _LOGGER.warning("Your authentication credentials are invalid or your account is inactive.")
        raise ConfigEntryNotReady
    else:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, PLATFORM)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

