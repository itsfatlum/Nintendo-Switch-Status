import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_URL

class NintendoSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Title shown in Integrations list
            return self.async_create_entry(title="Nintendo Switch Presence", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_URL): str})
        )