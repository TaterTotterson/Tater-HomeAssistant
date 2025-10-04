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
    endpoint: str

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Tater conversation entity from a config entry."""
    endpoint = hass.data.get(DOMAIN, {}).get(
        "endpoint", "http://127.0.0.1:8787/tater-ha/v1/message"
    )
    _LOGGER.debug(
        "tater_conversation: async_setup_entry (conversation platform), endpoint=%s",
        endpoint,
    )
    async_add_entities([TaterConversationEntity(endpoint)], update_before_add=False)

class TaterConversationEntity(ConversationEntity):
    _attr_name = "Tater Conversation"
    _attr_icon = "mdi:chat-processing"
    _attr_unique_id = "tater_conversation_entity"

    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint

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
                # Give the bridge up to 60s (plugins like web_search can be slow)
                async with async_timeout.timeout(60):
                    async with session.post(self._endpoint, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        reply = data.get("response", "")
        except Exception as e:
            _LOGGER.error(
                "Tater Conversation HTTP error to %s: %s", self._endpoint, e
            )
            reply = f"Sorry, I couldn’t reach Tater: {e}"

        ir = IntentResponse(language=user_input.language)
        ir.async_set_speech(reply or "Sorry, I didn't catch that.")
        return ConversationResult(response=ir)