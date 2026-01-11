from __future__ import annotations

import logging
from dataclasses import dataclass

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


@dataclass
class TaterConfig:
    name: str
    endpoint: str


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up one conversation entity per config entry."""
    name = entry.title or entry.data.get("name") or "Tater Conversation"
    endpoint = entry.data.get("endpoint", "http://127.0.0.1:8787/tater-ha/v1/message")

    _LOGGER.debug(
        "tater_conversation: async_setup_entry (conversation platform), name=%s endpoint=%s",
        name, endpoint,
    )

    async_add_entities(
        [TaterConversationEntity(hass=hass, name=name, endpoint=endpoint, unique_id=entry.entry_id)],
        update_before_add=False,
    )


class TaterConversationEntity(ConversationEntity):
    _attr_icon = "mdi:chat-processing"

    def __init__(self, hass: HomeAssistant, name: str, endpoint: str, unique_id: str) -> None:
        self.hass = hass
        self._attr_name = name
        self._endpoint = endpoint
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
                    async with session.post(self._endpoint, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        reply = data.get("response", "")
        except Exception as e:
            _LOGGER.error("Tater Conversation HTTP error to %s: %s", self._endpoint, e)
            reply = f"Sorry, I couldn’t reach Tater: {e}"

        ir = IntentResponse(language=user_input.language)
        ir.async_set_speech(reply or "Sorry, I didn't catch that.")
        return ConversationResult(response=ir)
