import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from . import DOMAIN

CONF_SERVER = "zalo_server"


class ZaloBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zalo Bot."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Zalo Bot", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_SERVER, default="http://localhost:3000"): str,
            vol.Required(CONF_USERNAME, default="admin"): str,
            vol.Required(CONF_PASSWORD, default="admin"): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reauth(self, user_input=None):
        return await self.async_step_user(user_input)


class ZaloBotOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_SERVER, default=self.config_entry.data.get(CONF_SERVER, "http://localhost:3000")): str,
            vol.Required(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME, "admin")): str,
            vol.Required(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD, "admin")): str,
        })
        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)


def async_get_options_flow(config_entry):
    return ZaloBotOptionsFlowHandler(config_entry)
