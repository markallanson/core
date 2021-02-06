from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from octopus_energy import Consumption, EnergyType, Meter

from homeassistant.components.octopus_energy import (
    DOMAIN,
    HaasOctopusEnergyClientWrapper,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)


class OctopusEnergyEntity(Entity):
    def __init__(self, uid: str, name: str, icon: str):
        self._uid = uid
        self._name = name
        self._icon = icon

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN)},
            "manufacturer": "Octopus Energy",
            "name": "Energy Meter",
            "entry_type": "service",
        }

    @property
    def unique_id(self) -> str:
        return self._uid

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return self._icon


class OctopusEnergyMeterEntity(OctopusEnergyEntity):
    def __init__(self, client_wrapper: HaasOctopusEnergyClientWrapper, meter: Meter):
        super().__init__(
            f"{meter.energy_type.value}_{meter.serial_number}_meter",
            f"{meter.energy_type.value.title()} Meter ({meter.serial_number})",
            "mdi:flash"
            if meter.energy_type == EnergyType.ELECTRICITY
            else "mdi:gas-cylinder",
        )
        self._meter: Meter = meter
        self._client_wrapper: HaasOctopusEnergyClientWrapper = client_wrapper
        self._latest_consumption: Optional[Consumption] = None
        self._available = False

    @property
    def should_poll(self) -> bool:
        return True

    async def async_update(self) -> None:
        try:
            self._latest_consumption = await self._client_wrapper.get_consumption(
                self._meter, period_to=datetime.utcnow()
            )
            if self._latest_consumption.intervals:
                print(self._latest_consumption)
            self._available = (
                self._latest_consumption is not None
                and self._latest_consumption.intervals
            )
        except:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[Decimal]:
        """Return the state of the sensor."""
        if self._latest_consumption is None or self._latest_consumption.intervals:
            return Decimal(0)
        return self._latest_consumption.intervals[0].consumed_units

    @property
    def device_state_attributes(self) -> object:
        if self._latest_consumption is None:
            return None

        device_state_attributes = {
            "start_time": self._latest_consumption.intervals[0].interval_start,
            "end_time": self._latest_consumption.intervals[0].interval_end,
        }
        print(device_state_attributes)
        return device_state_attributes

    @property
    def unit_of_measurement(self) -> str:
        return (
            self._latest_consumption.unit_type.description
            if self._latest_consumption and self._latest_consumption.unit_type
            else "kWh"
        )
