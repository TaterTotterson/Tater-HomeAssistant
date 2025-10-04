from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "tater_conversation"

class TaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Tater Conversation Agent", data=user_input)

        schema = vol.Schema({
            vol.Required("endpoint", default="http://tater-host:8787/tater-ha/v1/message"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        # Support YAML import if present
        return await self.async_step_user(user_input)

class TaterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("endpoint", default=self.config_entry.data.get("endpoint", "")): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)

async def async_get_options_flow(config_entry):
    return TaterOptionsFlowHandler(config_entry)