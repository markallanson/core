"""Config flow for Octopus Energy integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_ACCOUNT_ID,
    CONF_API_KEY,
)
from .service import HaasOctopusEnergyClientWrapper, OctopusEnergyConfigError, CannotConnect, \
    InvalidAuth

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Octopus Energy."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    STEP_USER_DATA_SCHEMA = vol.Schema({
        vol.Optional(CONF_ACCOUNT_ID): str,
        vol.Optional(CONF_API_KEY): str,
    })

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=ConfigFlow.STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            client = HaasOctopusEnergyClientWrapper(
                user_input[CONF_ACCOUNT_ID], user_input[CONF_API_KEY]
            )
            await client.validate_login()
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
            # ensure we cannot be setup twice
            await self.async_set_unique_id(user_input[CONF_ACCOUNT_ID])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_ACCOUNT_ID, "octopus_energy_public"), data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=ConfigFlow.STEP_USER_DATA_SCHEMA, errors=errors
        )

