import asyncio
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)


class TaterClient:
    def __init__(self, hass: HomeAssistant, base_url: str, timeout: int, session=None):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or aiohttp_client.async_get_clientsession(hass)

    async def async_ping(self) -> bool:
        url = f"{self._base_url}/tater-ha/v1/health"
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.get(url) as resp:
                    return resp.status == 200
        except Exception as e:
            _LOGGER.warning("Health check failed: %s", e)
            return False

    async def async_generate_text(self, text: str, session_id: str) -> str:
        url = f"{self._base_url}/tater-ha/v1/message"
        payload = {
            "text": text,
            "session_id": session_id,
        }

        async with asyncio.timeout(self._timeout):
            async with self._session.post(url, json=payload) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"Tater HA error {resp.status}: {await resp.text()}")
                data = await resp.json()
                return data.get("response", "")
