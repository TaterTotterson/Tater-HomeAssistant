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

After setup, the only configurable option is:

- **Bind Port** — the port the HA bridge listens on (default: `8787`)

You must also expose that port in your container or host firewall:

- Streamlit WebUI (if used) typically runs on port `8501`  
- HA bridge listens on the chosen `bind_port`

If you change `bind_port`, ensure the new port is exposed in Docker / firewall rules.

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

## 🛠️ Troubleshooting

| Problem | Check / Fix |
|----------|--------------|
| Bridge health returns error | Make sure `bind_port` is exposed and the Tater backend is running |
| Conversation agent greyed out in HA | Ensure `supported_languages = "*"` in `conversation.py` |
| Plugin returns “not available for Home Assistant” | Confirm plugin lists `"homeassistant"` in its `platforms` and implements `handle_homeassistant()` |
| Timeouts / “couldn’t reach Tater” responses | Increase timeouts, check logs, reduce plugin complexity or results count |

---

**Repository:** [Tater-HomeAssistant](https://github.com/TaterTotterson/Tater-HomeAssistant)  
**Part of:** [Tater](https://github.com/TaterTotterson/Tater)
