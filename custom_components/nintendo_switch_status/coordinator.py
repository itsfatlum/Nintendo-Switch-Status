from datetime import timedelta
import logging
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class NintendoSwitchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_url: str):
        self.api_url = api_url
        super().__init__(
            hass,
            _LOGGER,
            name="nintendo_switch_status",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, timeout=10) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as err:
            _LOGGER.exception("Error fetching Nintendo Switch presence data")
            raise