from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"

async def _load_conv(hass: HomeAssistant, source_cfg: dict):
    _LOGGER.debug("Loading conversation platform for %s", DOMAIN)
    # Tell the conversation integration to load our platform module:
    # custom_components/<DOMAIN>/conversation.py (expects async_get_agent)
    hass.async_create_task(
        discovery.async_load_platform(hass, "conversation", DOMAIN, {}, source_cfg)
    )

async def async_setup(hass: HomeAssistant, config: dict):
    if DOMAIN in config:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].update(config[DOMAIN])
        await _load_conv(hass, config)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)
    await _load_conv(hass, {DOMAIN: entry.data})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Nothing entity-based to unload; just clear stored config
    hass.data.pop(DOMAIN, None)
    return True