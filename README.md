# Tater-HomeAssistant

Home Assistant integrations for **Tater**, turning your custom voice/AI assistant into a first-class AI backend inside Home Assistant.

This repository provides **two separate Home Assistant integrations**, installable together via HACS:

- **Tater Conversation Agent** – use Tater as the Conversation Agent in HA’s Assist pipeline (voice + text)
- **Tater AI Task** – use Tater as an AI Task provider for automations, scripts, and structured AI responses

Both integrations communicate with the same Tater Home Assistant FastAPI bridge and share the same plugin system, history handling, and behavior.

---

## 🚀 Features

### 🗣️ Tater Conversation Agent

- Seamless Home Assistant integration via custom component  
- Works in HA’s **Conversation agent** pipeline (voice + text)  
- Routes queries to your Tater backend (FastAPI bridge)  
- Supports plugins that expose `handle_homeassistant(...)`  
- Plugin gating: only enabled + HA-compatible plugins run  
- Session context (history) maintained per conversation  
- Configurable bind port via HA UI (managed in Tater WebUI)  
- Timeout for plugin / LLM calls (default: 60 seconds)

### 🧠 Tater AI Task

- Exposes Tater as an **AI Task entity** (`ai_task.generate_data`)  
- Designed for automations, scripts, and dashboards  
- Uses the same Tater Home Assistant bridge (no API keys required)  
- Automation-safe, concise responses by default  
- Can execute plugins when an action is requested  
- Independent integration from the Conversation Agent  
- Ideal for summaries, notifications, and deterministic AI output

---

## 📦 Installation (via HACS)

1. In Home Assistant, open **HACS → … (3 dots menu) → Custom repositories**  
2. Add the custom repository URL:  
   **https://github.com/TaterTotterson/Tater-HomeAssistant**  
   - Category: **Integration**  
3. Back in HACS, search for **Tater Conversation Agent** and/or **Tater AI Task** and click **Download**.  
4. After installation completes, **restart Home Assistant**.  
5. Go to **Settings → Devices & Services → + Add Integration** and add:
   - **Tater Conversation Agent** (for Assist / voice / chat)
   - **Tater AI Task** (for automations and scripts)

You may install **one or both** integrations, depending on your needs.

---

## ⚙️ Configuration

All configuration for the Home Assistant bridge is managed from the **Tater WebUI** under:

**Settings → Platforms → Home Assistant Settings**

Here you can configure:

- **Bind Port** — the port the HA bridge listens on (default: `8787`)  
- Session history length and TTL  
- Voice PE LED entities (optional)

After changing the bind port in the WebUI:

- Ensure the same port is exposed in your **Docker container** or **firewall**  
- Update the Home Assistant integration to point to the new port  

Example:

- Tater WebUI → http://localhost:8501  
- HA Bridge → http://localhost:8787  

---

## 🧠 Using Tater AI Task (Example)

Example automation action:
```
action: ai_task.generate_data
target:
entity_id: ai_task.tater_ai_task
data:
instructions: >
What happened in the front yard today?
Keep it under 255 characters.
```
The response is returned in `{{ result.data }}` and can be used in notifications, sensors, or dashboards.

---

## 📝 Notes

- No API keys are required for Home Assistant ↔ Tater communication  
- Plugin availability is controlled from the Tater WebUI  
- Both integrations are local-first and self-hosted  
- Designed to work alongside Tater’s Discord, IRC, WebUI, and automation platforms  

---

**Repository:** https://github.com/TaterTotterson/Tater-HomeAssistant  
**Part of:** https://github.com/TaterTotterson/Tater
