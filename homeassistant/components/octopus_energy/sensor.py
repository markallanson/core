# energy usage only has a granularity of 30 minutes, so there is no point in syncing more often
# than this.
from datetime import datetime, timedelta
from functools import partial
import logging

from octopus_energy import Meter

from homeassistant.components.octopus_energy import DOMAIN
from homeassistant.components.octopus_energy.const import (
    CONF_ACCOUNT_ID,
    CONF_API_KEY,
    DATA_COORDINATOR,
    PLATFORM,
)
from homeassistant.components.octopus_energy.entities import OctopusEnergyMeterEntity
from homeassistant.components.octopus_energy.service import (
    HaasOctopusEnergyClientWrapper,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

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
        await setup_meters(hass, async_add_entities, client_wrapper)


async def setup_meters(
    hass: HomeAssistantType,
    async_add_entities,
    client_wrapper: HaasOctopusEnergyClientWrapper,
):
    meters = await client_wrapper.get_meters()
    if not meters:
        _LOGGER.info("No meters available; will not setup any entities")
        return

    hass.data.setdefault(DOMAIN, {})
    async_add_entities(
        [OctopusEnergyMeterEntity(client_wrapper, meter) for meter in meters], True
    )
