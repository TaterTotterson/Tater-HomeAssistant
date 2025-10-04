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
            await self.async_set_unique_id("tater_agent_singleton")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Tater Conversation Agent", data=user_input)

        schema = vol.Schema({
            vol.Required("endpoint", default="http://10.4.20.173:8787/tater-ha/v1/message"): str
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        return await self.async_step_user(user_input)