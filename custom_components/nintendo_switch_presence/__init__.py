from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_API_URL, CONF_USER_ID, CONF_INCLUDE_SPLATOON3
from .coordinator import NintendoSwitchCoordinator

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api_url = entry.data[CONF_API_URL]
    user_id = entry.data.get(CONF_USER_ID)
    include_splatoon3 = entry.data.get(CONF_INCLUDE_SPLATOON3, False)
    
    coordinator = NintendoSwitchCoordinator(hass, api_url, user_id, include_splatoon3)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True