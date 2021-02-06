# energy usage only has a granularity of 30 minutes, so there is no point in syncing more often
# than this.
import logging
from datetime import timedelta, datetime
from functools import partial

from octopus_energy import Meter

from homeassistant.components.octopus_energy import DOMAIN
from homeassistant.components.octopus_energy.const import DATA_COORDINATOR, CONF_API_KEY, \
    CONF_ACCOUNT_ID, PLATFORM
from homeassistant.components.octopus_energy.entities import OctopusEnergyMeterEntity
from homeassistant.components.octopus_energy.service import HaasOctopusEnergyClientWrapper
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

SCAN_INTERVAL = timedelta(seconds=1800)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    client_wrapper = HaasOctopusEnergyClientWrapper(
        entry.data.get(CONF_ACCOUNT_ID, None), entry.data.get(CONF_API_KEY, None)
    )

    # If the user configured an account id then setup their meters as entities
    if CONF_ACCOUNT_ID in entry.data:
        await setup_meters(hass, entry, async_add_entities, client_wrapper)


async def setup_meters(
    hass: HomeAssistantType,
    entry: ConfigEntry,
    async_add_entities,
    client_wrapper: HaasOctopusEnergyClientWrapper
):
    meters = await client_wrapper.get_meters()
    if not meters:
        _LOGGER.info("No meters available; will not setup any entities")
        return

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=PLATFORM,
        update_interval=SCAN_INTERVAL,
    )
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    async_add_entities([
        OctopusEnergyMeterEntity(coordinator, client_wrapper, meter) for meter in meters
    ] if coordinator else [], True)
