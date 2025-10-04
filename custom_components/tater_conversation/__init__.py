# custom_components/tater_conversation/__init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"
PLATFORMS: list[str] = ["conversation"]

async def async_setup(hass: HomeAssistant, config: dict):
    # YAML (optional)
    if DOMAIN in config:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].update(config[DOMAIN])
        _LOGGER.debug("Loaded YAML config for %s: %s", DOMAIN, hass.data[DOMAIN])
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)
    _LOGGER.debug("Setting up config entry for %s: %s", DOMAIN, entry.data)

    # Forward to the conversation platform (loads conversation.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("Forwarded entry to platforms: %s", PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok