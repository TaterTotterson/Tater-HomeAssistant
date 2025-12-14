import logging
from typing import Any, Dict

from homeassistant.components.ai_task import (
    AITaskEntity,
    AITaskEntityFeature,
    GenDataTask,
    GenDataTaskResult,
)
from homeassistant.components.conversation import ChatLog
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([TaterAITaskEntity(hass, entry)], update_before_add=False)


class TaterAITaskEntity(AITaskEntity):
    _attr_supported_features = AITaskEntityFeature.GENERATE_DATA

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._client = hass.data[DOMAIN][entry.entry_id]

        name = entry.data.get(CONF_NAME, "Tater")
        self._attr_name = f"{name} AI Task"
        self._attr_unique_id = f"{entry.entry_id}_ai_task"

    async def _async_generate_data(
        self, task: GenDataTask, chat_log: ChatLog
    ) -> GenDataTaskResult:
        session_id = f"ai_task:{task.name or 'default'}"

        text = task.instructions.strip()

        # Keep AI Task requests deterministic & automation-safe
        if "keep it" not in text.lower():
            text += "\nKeep the response concise and suitable for automations."

        response_text = await self._client.async_generate_text(text, session_id)
        return GenDataTaskResult(data=response_text)
