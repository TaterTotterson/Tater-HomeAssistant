from homeassistant.core import HomeAssistant

DOMAIN = "tater_conversation"

async def async_setup(hass: HomeAssistant, config: dict):
    # Allow YAML config like:
    # tater_conversation:
    #   endpoint: "http://tater-host:8787/tater-ha/v1/message"
    if DOMAIN in config:
        hass.data[DOMAIN] = dict(config[DOMAIN])
    return True