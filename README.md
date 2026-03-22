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

1. In Home Assistant, open **HACS → … (3 dots menu) → Custom repositories**  
2. Add the custom repository URL:  
   **https://github.com/TaterTotterson/Tater-HomeAssistant**  
   - Category: **Integration**  
3. Back in the HACS, search for **Tater Conversation Agent** and click **Download** to install it.  
4. After the installation completes, **restart Home Assistant**.  
5. Go to **Settings → Devices & Services → + Add Integration**, search for **Tater Conversation**, and add it.  
6. When prompted for the endpoint URL, enter your Tater bridge endpoint (usually):  
   **http://YOUR_TATER_HOST:8787/tater-ha/v1/message**  
   - Replace `YOUR_TATER_HOST` with your server or Docker host IP (e.g., `http://10.4.20.173:8787/tater-ha/v1/message`)  
   - If API key auth is enabled on the Tater portal, enter the same key in the integration's **API Key** field.
   - If portal API auth is disabled, leave **API Key** blank.
7. Once added, open **Settings → Voice Assistants → Add Assistant**, and choose **Tater Conversation** as your **Conversation Agent**.

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

In Home Assistant, talk to Tater via the Assist conversation UI or as voice input if your setup permits.

---

**Repository:** [Tater-HomeAssistant](https://github.com/TaterTotterson/Tater-HomeAssistant)  
**Part of:** [Tater](https://github.com/TaterTotterson/Tater)
