"""Config flow for Octopus Energy integration."""
import logging

import voluptuous as vol
from octopus_energy import OctopusEnergyClient, MeterType, ApiAuthenticationError, ApiError

from homeassistant import config_entries, core, exceptions

from .const import (
    DOMAIN,
    CONF_ACCOUNT_ID,
    CONF_API_KEY,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_ACCOUNT_ID: str, CONF_API_KEY: str})


class OctopusEnergyConfigError(Exception):
    def __init__(self, *args: object, error_type: str) -> None:
        super().__init__(*args)
        self.error_type = error_type


async def validate_input(hass: core.HomeAssistant, user_input):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    try:
        async with OctopusEnergyRestClient(user_input[CONF_API_KEY]) as client:
            account_details = client.get_account_v1(user_input[CONF_ACCOUNT_ID])
        except ApiError:
            raise OctopusEnergyConfigError("")
    except HTTPError:
        raise CannotConnect
    except ApiAuthenticationError:
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Octopus Energy"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Octopus Energy."""

    VERSION = 1
    # TODO pick one of the available connection classes in homeassistant/config_entries.py
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except OctopusEnergyConfigError as e:
            errors["base"] = e.error_type
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
