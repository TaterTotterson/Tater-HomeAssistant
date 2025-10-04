# Tater-HomeAssistant

Home Assistant integration for **Tater**, turning your custom voice/AI assistant into a full conversation agent in HA.  
This lets you use Tater as the “Conversation agent” in HA’s Assist pipeline, send voice/text messages, and run plugins with `handle_homeassistant()` support.

## 🚀 Features

- Seamless Home Assistant integration via custom component  
- Works in HA’s **Conversation agent** pipeline (voice + text)  
- Routes queries to your Tater backend (FastAPI bridge)  
- Supports plugins that expose `handle_homeassistant(...)`  
- Plugin gating: only enabled + HA-compatible plugins run  
- Session context (history) maintained per conversation  
- Configurable bind port via HA UI  
- Timeout for plugin / LLM calls (default: 60 seconds)

## 📦 Installation (via HACS)

1. In HACS, go to **Integrations → … (3 dots menu) → Custom repositories**  
2. Add the repository URL:  
   https://github.com/TaterTotterson/Tater-HomeAssistant  
   - Category: **Integration**  
3. Back in the HACS tab, click **Integrations**, search for “Tater HomeAssistant” (or similar), and install.  
4. After install completes, **restart Home Assistant**.  
5. In **Settings → Devices & Services → + Add Integration** search for “Tater Conversation” and add it.  
6. Now you can go to **Settings → Voice Assistants → Add Assistant**, and select “Tater Conversation” as the agent.

## ⚙️ Configuration

All configuration for the Home Assistant bridge is managed directly from the **Tater WebUI** under  
**Settings → Platforms → Home Assistant Settings**.

Here you can set:

- **Bind Port** — the port the HA bridge listens on (default: `8787`)

After changing the port in the WebUI, make sure to:

- Expose the same port in your **Docker container** or **firewall** so Home Assistant can reach it.  
- Remember that the Streamlit WebUI itself typically runs on port `8501`, while the Home Assistant bridge runs on your chosen `bind_port`.

Example:
- WebUI → http://localhost:8501  
- HA Bridge → http://localhost:8787  

If you change the bind port in the WebUI, update your Home Assistant integration to point to the new port.

## 🧪 Testing the Bridge

Once installed and running:

Health check:

curl http://<ha-host>:<bind_port>/tater-ha/v1/health  
→ {"ok":true,"version":"1.3"}

Send a simple chat:
```
curl -X POST http://<ha-host>:<bind_port>/tater-ha/v1/message \
  -H "Content-Type: application/json" \
  -d '{"text":"hello tater"}'  
→ {"response":"Hello! 👋"}
```
In Home Assistant, talk to Tater via the Assist conversation UI or as voice input if your setup permits.

---

**Repository:** [Tater-HomeAssistant](https://github.com/TaterTotterson/Tater-HomeAssistant)  
**Part of:** [Tater](https://github.com/TaterTotterson/Tater)
