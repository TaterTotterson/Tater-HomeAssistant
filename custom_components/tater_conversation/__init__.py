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
    cfg = dict(entry.data)
    cfg.update(entry.options or {})
    hass.data[DOMAIN].update(cfg)
    _LOGGER.debug("Setting up entry for %s: %s", DOMAIN, cfg)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
