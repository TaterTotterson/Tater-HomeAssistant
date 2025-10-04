from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tater_conversation"
PLATFORMS: list[str] = ["conversation"]

async def async_setup(hass: HomeAssistant, config: dict):
    # Optional YAML support: if you also want YAML, you could import it into an entry,
    # but simplest is UI-only via config_flow.
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)
    _LOGGER.debug("Setting up entry for %s: %s", DOMAIN, entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok