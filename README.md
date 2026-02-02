# Nintendo Switch Status

**Nintendo Switch Status** is a Home Assistant custom integration that polls a public NXAPI presence URL and exposes:
- Online status (ONLINE / OFFLINE)
- Current game name
- Game image URL

## Installation via HACS
1. In HACS → Integrations → ⋮ → Custom repositories, add:
   `https://github.com/itsfatlum/nintendo-switch-status` (type: integration)
2. Install the integration.
3. Restart Home Assistant.
4. Settings → Devices & Services → Add Integration → **Nintendo Switch Status**
5. Paste your API URL (e.g. `https://nxapi-presence.fancy.org.uk/api/presence/03e0f77eb2a15cd9`)

## Configuration
No YAML required — the integration uses a UI config flow.

## Troubleshooting
- Ensure the API URL is reachable from your Home Assistant instance and returns JSON.
- Check Home Assistant logs for errors if sensors don’t appear.

## Contributing
PRs welcome. For branding (icons/logo in HA UI), open a PR to `home-assistant/brands`.