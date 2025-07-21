"""Config flow for Zalo Bot integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback


from .const import (
    DOMAIN,
    CONF_ZALO_SERVER,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ENABLE_NOTIFICATIONS,
    DEFAULT_ENABLE_NOTIFICATIONS
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zalo Bot."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Zalo Bot",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ZALO_SERVER): str,
                vol.Required(CONF_USERNAME, default="admin"): str,
                vol.Required(CONF_PASSWORD, default="admin"): str,
                vol.Optional(CONF_ENABLE_NOTIFICATIONS, default=DEFAULT_ENABLE_NOTIFICATIONS): bool,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_ZALO_SERVER,
                    default=self.config_entry.data.get(CONF_ZALO_SERVER)
                ): str,
                vol.Required(
                    CONF_USERNAME,
                    default=self.config_entry.data.get(CONF_USERNAME, "admin")
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=self.config_entry.data.get(CONF_PASSWORD, "admin")
                ): str,
                vol.Optional(
                    CONF_ENABLE_NOTIFICATIONS,
                    default=self.config_entry.data.get(
                        CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS
                    )
                ): bool,
            })
        )
