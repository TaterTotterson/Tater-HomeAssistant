from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

import aiohttp
import async_timeout

from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationInput,
    ConversationResult,
)
from homeassistant.helpers.intent import IntentResponse
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import area_registry as ar

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_PATH = "/tater-ha/v1/message"


@dataclass
class TaterConfig:
    name: str
    host: str
    port: int
    endpoint: str
    api_key: str


def _normalize_host(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return DEFAULT_HOST
    candidate = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(candidate)
    return str(parsed.hostname or "").strip() or raw


def _coerce_port(value, fallback: int = DEFAULT_PORT) -> int:
    try:
        port = int(str(value).strip())
    except Exception:
        return int(fallback)
    if 1 <= port <= 65535:
        return int(port)
    return int(fallback)


def _split_endpoint(endpoint: str) -> tuple[str, int]:
    raw = str(endpoint or "").strip()
    if not raw:
        return DEFAULT_HOST, DEFAULT_PORT
    candidate = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(candidate)
    host = str(parsed.hostname or "").strip() or DEFAULT_HOST
    port = int(parsed.port or DEFAULT_PORT)
    return host, port


def _build_endpoint(cfg: dict) -> str:
    host = cfg.get("host")
    port = cfg.get("port")
    if host is None or port is None:
        endpoint_host, endpoint_port = _split_endpoint(cfg.get("endpoint", ""))
        host = endpoint_host if host is None else host
        port = endpoint_port if port is None else port
    host = _normalize_host(str(host or ""))
    port = _coerce_port(port, DEFAULT_PORT)
    return f"http://{host}:{port}{DEFAULT_PATH}"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up one conversation entity per config entry."""
    cfg = dict(entry.data)
    cfg.update(entry.options or {})
    name = cfg.get("name") or entry.title or "Tater Conversation"
    endpoint = _build_endpoint(cfg)
    api_key = str(cfg.get("api_key") or "").strip()

    _LOGGER.debug(
        "tater_conversation: async_setup_entry (conversation platform), name=%s endpoint=%s",
        name, endpoint,
    )

    async_add_entities(
        [
            TaterConversationEntity(
                hass=hass,
                name=name,
                endpoint=endpoint,
                api_key=api_key,
                unique_id=entry.entry_id,
            )
        ],
        update_before_add=False,
    )


class TaterConversationEntity(ConversationEntity):
    _attr_icon = "mdi:chat-processing"

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        endpoint: str,
        api_key: str,
        unique_id: str,
    ) -> None:
        self.hass = hass
        self._attr_name = name
        self._endpoint = endpoint
        self._api_key = api_key
        self._attr_unique_id = unique_id

    @property
    def supported_languages(self):  # return "*" to indicate all languages
        return "*"

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Send the user text to Tater and return the LLM reply as speech."""
        text = user_input.text or ""

        # Base context from HA conversation input (if present)
        user_id = user_input.context.user_id if user_input.context else None
        device_id = getattr(user_input, "device_id", None)
        area_id = getattr(user_input, "area_id", None)
        session_id = user_input.conversation_id

        # Resolve device + area names (more useful for Tater than IDs)
        device_name = None
        area_name = None

        try:
            device_reg = dr.async_get(self.hass)
            area_reg = ar.async_get(self.hass)

            dev = device_reg.async_get(device_id) if device_id else None
            if dev:
                device_name = dev.name_by_user or dev.name

                # If area_id wasn't provided, fall back to the device's assigned area
                if not area_id:
                    area_id = dev.area_id

            if area_id:
                area = area_reg.async_get_area(area_id)
                if area:
                    area_name = area.name
        except Exception as e:
            _LOGGER.debug("tater_conversation: failed resolving device/area names: %s", e)

        # Keep existing fields for compatibility, add richer 'context' too
        payload = {
            "text": text,
            "user_id": user_id,
            "device_id": device_id,
            "area_id": area_id,
            "session_id": session_id,
            "context": {
                "device_id": device_id,
                "device_name": device_name,
                "area_id": area_id,
                "area_name": area_name,
                "language": user_input.language,
            },
        }

        reply = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(60):
                    request_kwargs = {"json": payload}
                    if self._api_key:
                        request_kwargs["headers"] = {"X-Tater-Token": self._api_key}
                    async with session.post(self._endpoint, **request_kwargs) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        reply = data.get("response", "")
        except aiohttp.ClientResponseError as e:
            _LOGGER.error("Tater Conversation HTTP error to %s: %s", self._endpoint, e)
            if e.status in (401, 403):
                reply = "Tater authentication failed. Check the API key in this integration."
            else:
                reply = f"Sorry, I couldn’t reach Tater: {e}"
        except Exception as e:
            _LOGGER.error("Tater Conversation HTTP error to %s: %s", self._endpoint, e)
            reply = f"Sorry, I couldn’t reach Tater: {e}"

        ir = IntentResponse(language=user_input.language)
        ir.async_set_speech(reply or "Sorry, I didn't catch that.")
        return ConversationResult(response=ir)
