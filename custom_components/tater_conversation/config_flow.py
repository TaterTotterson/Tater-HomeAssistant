from __future__ import annotations
from typing import Any
import re
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "tater_conversation"

def _slugify_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-_]", "", s)
    return s or "tater"

class TaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            name = user_input["name"]
            endpoint = user_input["endpoint"]
            unique_id = f"tater_conversation_{_slugify_name(name)}"

            # Allow multiple entries, but prevent duplicate names
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=name, data={"name": name, "endpoint": endpoint})

        schema = vol.Schema({
            vol.Required("name", default="Tater Conversation"): str,
            vol.Required("endpoint", default="http://127.0.0.1:8787/tater-ha/v1/message"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)