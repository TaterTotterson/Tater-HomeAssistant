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
        [TaterConversationEntity(name=name, endpoint=endpoint, unique_id=entry.entry_id)],
        update_before_add=False,
    )

class TaterConversationEntity(ConversationEntity):
    _attr_icon = "mdi:chat-processing"

    def __init__(self, name: str, endpoint: str, unique_id: str) -> None:
        self._attr_name = name
        self._endpoint = endpoint
        self._attr_unique_id = unique_id

    @property
    def supported_languages(self):  # return "*" to indicate all languages
        return "*"

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Send the user text to Tater and return the LLM reply as speech."""
        text = user_input.text or ""
        payload = {
            "text": text,
            "user_id": user_input.context.user_id if user_input.context else None,
            "device_id": getattr(user_input, "device_id", None),
            "area_id": getattr(user_input, "area_id", None),
            "session_id": user_input.conversation_id,
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