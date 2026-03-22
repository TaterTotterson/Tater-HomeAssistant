from __future__ import annotations
from typing import Any
import re
from urllib.parse import urlparse
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "tater_conversation"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_KEY = "api_key"
CONF_ENDPOINT = "endpoint"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_PATH = "/tater-ha/v1/message"

def _slugify_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-_]", "", s)
    return s or "tater"


def _normalize_host(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return DEFAULT_HOST
    candidate = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(candidate)
    host = str(parsed.hostname or "").strip()
    return host or raw


def _coerce_port(value: Any, fallback: int = DEFAULT_PORT) -> int:
    try:
        port = int(str(value).strip())
    except Exception:
        return int(fallback)
    if 1 <= port <= 65535:
        return int(port)
    return int(fallback)


def _endpoint_from_host_port(host: str, port: int) -> str:
    return f"http://{host}:{port}{DEFAULT_PATH}"


def _split_endpoint(endpoint: Any) -> tuple[str, int]:
    raw = str(endpoint or "").strip()
    if not raw:
        return DEFAULT_HOST, DEFAULT_PORT
    candidate = raw if "://" in raw else f"http://{raw}"
    parsed = urlparse(candidate)
    host = str(parsed.hostname or "").strip() or DEFAULT_HOST
    port = int(parsed.port or DEFAULT_PORT)
    return host, port

class TaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            host = _normalize_host(user_input.get(CONF_HOST))
            port = _coerce_port(user_input.get(CONF_PORT), DEFAULT_PORT)
            api_key = str(user_input.get(CONF_API_KEY, "") or "").strip()
            endpoint = _endpoint_from_host_port(host, port)
            unique_id = f"tater_conversation_{_slugify_name(f'{host}_{port}')}"

            # Allow multiple entries, but prevent duplicate host+port
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Tater Conversation",
                data={
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_ENDPOINT: endpoint,
                    CONF_API_KEY: api_key,
                },
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_API_KEY, default=""): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TaterOptionsFlow(config_entry)


class TaterOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        cfg = dict(self.config_entry.data)
        cfg.update(self.config_entry.options or {})
        raw_host = cfg.get(CONF_HOST)
        raw_port = cfg.get(CONF_PORT)
        if raw_host is None or raw_port is None:
            endpoint_host, endpoint_port = _split_endpoint(cfg.get(CONF_ENDPOINT))
            host = _normalize_host(raw_host if raw_host is not None else endpoint_host)
            port = _coerce_port(raw_port if raw_port is not None else endpoint_port, DEFAULT_PORT)
        else:
            host = _normalize_host(raw_host)
            port = _coerce_port(raw_port, DEFAULT_PORT)

        if user_input is None:
            schema = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=host or DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=port or DEFAULT_PORT): int,
                    vol.Optional(CONF_API_KEY, default=cfg.get(CONF_API_KEY, "")): str,
                }
            )
            return self.async_show_form(step_id="init", data_schema=schema)

        next_host = _normalize_host(user_input.get(CONF_HOST))
        next_port = _coerce_port(user_input.get(CONF_PORT), DEFAULT_PORT)
        next_api_key = str(user_input.get(CONF_API_KEY, "") or "").strip()

        return self.async_create_entry(
            title="",
            data={
                CONF_HOST: next_host,
                CONF_PORT: next_port,
                CONF_ENDPOINT: _endpoint_from_host_port(next_host, next_port),
                CONF_API_KEY: next_api_key,
            },
        )
