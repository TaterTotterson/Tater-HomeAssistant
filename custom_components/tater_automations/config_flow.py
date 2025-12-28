from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            schema = vol.Schema({
                vol.Required(CONF_HOST, default="10.4.20.173"): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            })
            return self.async_show_form(step_id="user", data_schema=schema)

        await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Tater Automations", data=user_input)

    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        data = dict(self.config_entry.data)
        if user_input is None:
            schema = vol.Schema({
                vol.Required(CONF_HOST, default=data.get(CONF_HOST, "10.4.20.173")): str,
                vol.Required(CONF_PORT, default=data.get(CONF_PORT, DEFAULT_PORT)): int,
            })
            return self.async_show_form(step_id="init", data_schema=schema)

        new_data = dict(self.config_entry.data)
        new_data.update(user_input)
        return self.async_create_entry(title="", data=new_data)
