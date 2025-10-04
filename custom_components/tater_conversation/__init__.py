from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "tater_conversation"

async def _load_conversation_platform(hass: HomeAssistant, source_config: dict):
    # Load our conversation agent (conversation.py exposes async_get_agent)
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            "conversation", DOMAIN, {}, source_config
        )
    )

async def async_setup(hass: HomeAssistant, config: dict):
    if DOMAIN in config:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].update(config[DOMAIN])
        await _load_conversation_platform(hass, config)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)
    await _load_conversation_platform(hass, {DOMAIN: entry.data})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Nothing entity-based to unload; keep it simple.
    for k in list(hass.data.get(DOMAIN, {})):
        hass.data[DOMAIN].pop(k, None)
    return True