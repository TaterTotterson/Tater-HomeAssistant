# custom_components/tater_conversation/__init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery  # ✅ import the module

DOMAIN = "tater_conversation"
PLATFORMS: list[str] = ["conversation"]

async def async_setup(hass: HomeAssistant, config: dict):
    # Optional YAML support
    if DOMAIN in config:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].update(config[DOMAIN])
        # ✅ load conversation platform for YAML
        hass.async_create_task(
            discovery.async_load_platform(
                hass, "conversation", DOMAIN, {}, config
            )
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # UI (config_flow) support
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].update(entry.data)
    # ✅ load conversation platform for config entries
    hass.async_create_task(
        discovery.async_load_platform(
            hass, "conversation", DOMAIN, {}, {DOMAIN: entry.data}
        )
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Nothing entity-based to unload; just clear our stored config
    hass.data.pop(DOMAIN, None)
    return True