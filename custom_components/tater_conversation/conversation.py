from __future__ import annotations
from dataclasses import dataclass
import aiohttp
import async_timeout

from homeassistant.components import conversation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

DOMAIN = "tater_conversation"

@dataclass
class TaterConfig:
    endpoint: str

async def async_get_agent(hass: HomeAssistant) -> conversation.AbstractConversationAgent:
    # prefer UI config (config_entry) via hass.data; fallback to YAML if present
    cfg = TaterConfig(
        endpoint=hass.data.get(DOMAIN, {}).get("endpoint", "http://127.0.0.1:8787/tater-ha/v1/message")
    )
    return TaterAgent(hass, cfg)

class TaterAgent(conversation.AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, cfg: TaterConfig):
        self.hass = hass
        self.cfg = cfg
        self.supported_languages = ["*"]

    @property
    def attribution(self) -> dict[str, str]:
        return {"name": "Tater", "url": "https://example.invalid/tater"}

    async def async_process(self, user_input: conversation.ConversationInput) -> intent.IntentResponse:
        text = user_input.text or ""
        payload = {
            "text": text,
            "user_id": user_input.context.user_id if user_input.context else None,
            "device_id": getattr(user_input, "device_id", None),
            "area_id": getattr(user_input, "area_id", None),
            "session_id": user_input.conversation_id,
        }

        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(15):
                    async with session.post(self.cfg.endpoint, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        reply = data.get("response", "")
            except Exception as e:
                reply = f"Sorry, I couldn’t reach Tater: {e}"

        resp = intent.IntentResponse(language=user_input.language)
        resp.async_set_speech(reply)
        return resp