from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT, SERVICE_CALL_TOOL

PLATFORMS: list[str] = []

async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    session = aiohttp_client.async_get_clientsession(hass)

    async def _call_tool(call: ServiceCall):
        tool = (call.data.get("tool") or "").strip()
        arguments = call.data.get("arguments") or {}

        if not tool:
            raise HomeAssistantError("Missing required field: tool")

        if not isinstance(arguments, dict):
            raise HomeAssistantError("arguments must be an object/dict")

        url = f"http://{host}:{port}/tater-ha/v1/tools/{tool}"
        payload = {"arguments": arguments}

        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    raise HomeAssistantError(f"Tater tool call failed ({resp.status}): {text[:200]}")
                # Return value is not used by automations directly, but shows in traces/logs
                try:
                    return json.loads(text) if text else {"ok": True}
                except Exception:
                    return {"ok": True, "raw": text}
        except asyncio.TimeoutError as e:
            raise HomeAssistantError("Tater tool call timed out") from e
        except Exception as e:
            raise HomeAssistantError(f"Tater tool call error: {e}") from e

    hass.services.async_register(DOMAIN, SERVICE_CALL_TOOL, _call_tool)
    return True

async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    hass.services.async_remove(DOMAIN, SERVICE_CALL_TOOL)
    return True
