from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "tater_conversation"

class TaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            # create single entry (avoid duplicates)
            await self._abort_if_unique_id_configured()
            await self.async_set_unique_id("tater_agent_singleton")
            return self.async_create_entry(title="Tater Conversation Agent", data=user_input)

        schema = vol.Schema({
            vol.Required("endpoint", default="http://10.4.20.173:8787/tater-ha/v1/message"): str
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        # YAML import support
        return await self.async_step_user(user_input)

class TaterOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("endpoint", default=self.entry.data.get("endpoint", "")): str
        })
        return self.async_show_form(step_id="init", data_schema=schema)

async def async_get_options_flow(entry):
    return TaterOptionsFlow(entry)