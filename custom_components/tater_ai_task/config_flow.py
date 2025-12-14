from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_TIMEOUT,
    CONF_NAME,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
)
from .api import TaterClient


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            timeout = int(user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            session = aiohttp_client.async_get_clientsession(self.hass)
            client = TaterClient(self.hass, base_url, timeout, session=session)

            if not await client.async_ping():
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{DOMAIN}:{base_url}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_BASE_URL: base_url,
                        CONF_TIMEOUT: timeout,
                        CONF_NAME: name,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
