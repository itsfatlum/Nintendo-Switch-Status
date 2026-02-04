import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_URL, CONF_USER_ID, CONF_INCLUDE_SPLATOON3
import re

class NintendoSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Extract user ID from API URL
            url = user_input[CONF_API_URL]
            user_id_match = re.search(r'/presence/([a-f0-9]{16})', url)
            if not user_id_match:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({vol.Required(CONF_API_URL): str}),
                    errors={"base": "invalid_url"}
                )
            
            user_id = user_id_match.group(1)
            include_splatoon3 = "include-splatoon3=1" in url
            
            data = {
                CONF_API_URL: url,
                CONF_USER_ID: user_id,
                CONF_INCLUDE_SPLATOON3: include_splatoon3,
            }
            
            # Title shown in Integrations list
            return self.async_create_entry(title=f"Nintendo Switch ({user_id})", data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_URL): str})
        )