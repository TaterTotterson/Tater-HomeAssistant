from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "tater_conversation"
PLATFORMS = ["conversation"]

async def async_setup(hass: HomeAssistant, config: dict):
    # YAML (optional). If present, stash values so conversation.py can read them.
    if DOMAIN in config:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].update(config[DOMAIN])
        # Load conversation platform for YAML setups
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform("conversation", DOMAIN, {}, config)
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # UI / config_flow path
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)  # expose endpoint to conversation.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # clean up stored data for this entry
        for k in list(hass.data.get(DOMAIN, {})):
            hass.data[DOMAIN].pop(k, None)
    return unload_ok