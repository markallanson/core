from datetime import datetime, timedelta
from typing import List

from aiohttp.web_exceptions import HTTPError
from octopus_energy import OctopusEnergyConsumerClient, ApiAuthenticationError, ApiNotFoundError, \
    ApiError, Meter, Consumption

from homeassistant import exceptions
from .const import ERR_NO_METERS


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class OctopusEnergyConfigError(Exception):
    def __init__(self, *args: object, error_type: str) -> None:
        super().__init__(*args)
        self.error_type = error_type


class HaasOctopusEnergyClientWrapper:
    """Home Assistant friendly client wrapper"""
    def __init__(self, account_id: str, api_key: str):
        self.client = OctopusEnergyConsumerClient(account_id, api_key)

    async def validate_login(self) -> None:
        """Validates the login details provided by the user."""
        try:
            meters = await self.get_meters()
            if not meters:
                raise OctopusEnergyConfigError(error_type=ERR_NO_METERS)
        except ApiAuthenticationError:
            raise InvalidAuth
        except ApiNotFoundError as e:
            raise OctopusEnergyConfigError(error_type=ERR_NO_METERS)
        except HTTPError or ApiError:
            raise CannotConnect

    async def get_meters(self) -> List[Meter]:
        """Gets the meters associated with the account"""
        return await self.client.get_meters()

    async def get_consumption(self, meter: Meter, period_to: datetime) -> Consumption:
        """Gets the consumption for a meter."""
        return await self.client.get_consumption(
            meter, period_from=period_to - timedelta(days=1), period_to=period_to
        )
