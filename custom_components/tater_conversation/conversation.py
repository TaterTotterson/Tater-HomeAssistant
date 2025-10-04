from __future__ import annotations
from dataclasses import dataclass
import logging
import aiohttp
import async_timeout

from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationInput,
)
from homeassistant.helpers.intent import IntentResponse
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"

@dataclass
class TaterConfig:
    endpoint: str

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Tater conversation entity from a config entry."""
    endpoint = hass.data.get(DOMAIN, {}).get("endpoint", "http://127.0.0.1:8787/tater-ha/v1/message")
    async_add_entities([TaterConversationEntity(endpoint)], update_before_add=False)

class TaterConversationEntity(ConversationEntity):
    """A conversation entity that sends text to the Tater endpoint and returns a reply."""

    _attr_name = "Tater Conversation"
    _attr_icon = "mdi:account-voice"
    _attr_has_entity_name = True

    def __init__(self, endpoint: str):
        super().__init__()
        self._endpoint = endpoint
        self.supported_languages = ["*"]

    async def async_process(self, user_input: ConversationInput) -> IntentResponse:
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
                async with async_timeout.timeout(15):
                    async with session.post(self._endpoint, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        reply = data.get("response", "")
        except Exception as e:
            _LOGGER.error("Tater Conversation HTTP error to %s: %s", self._endpoint, e)
            reply = f"Sorry, I couldn’t reach Tater: {e}"

        # Build and return an IntentResponse that Assist will speak/show
        response = IntentResponse(language=user_input.language)
        response.async_set_speech(reply)
        return response