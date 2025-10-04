from __future__ import annotations
import logging, time, aiohttp, async_timeout
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"
DEFAULT_ENDPOINT = "http://127.0.0.1:8787/tater-ha/v1/message"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data.get(DOMAIN, {})  # entry.data already copied there in __init__.py
    endpoint = data.get("endpoint", DEFAULT_ENDPOINT)
    coordinator = TaterPingCoordinator(hass, endpoint)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([TaterStatusSensor(coordinator)], True)

class TaterPingCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, endpoint: str):
        super().__init__(hass, _LOGGER, name="Tater Conversation Ping", update_interval=None)
        self.endpoint = endpoint

    async def _async_update_data(self) -> dict[str, Any]:
        # Manual trigger only; we’ll schedule updates from the entity
        return await self._ping_once()

    async def _ping_once(self) -> dict[str, Any]:
        st = time.monotonic()
        payload = {"text": "ping", "session_id": "ha-status"}
        status = "offline"
        latency = None
        last_error = None
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(5):
                    async with session.post(self.endpoint, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        _ = data.get("response", "")
            latency = int((time.monotonic() - st) * 1000)
            status = "online"
        except Exception as e:
            last_error = str(e)
        return {"status": status, "latency_ms": latency, "last_error": last_error, "endpoint": self.endpoint}

class TaterStatusSensor(SensorEntity):
    _attr_name = "Tater Conversation Status"
    _attr_unique_id = "tater_conversation_status"
    _attr_icon = "mdi:account-voice"

    def __init__(self, coordinator: TaterPingCoordinator):
        self._coordinator = coordinator
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    async def async_added_to_hass(self):
        await self._refresh()

    async def async_update(self):
        await self._refresh()

    async def _refresh(self):
        data = await self._coordinator._ping_once()
        self._attr_native_value = data["status"]
        self._attr_extra_state_attributes = {
            "endpoint": data["endpoint"],
            "latency_ms": data["latency_ms"],
            "last_error": data["last_error"],
        }
        self.async_write_ha_state()