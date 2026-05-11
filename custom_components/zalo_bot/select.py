"""Zalo Bot select entities."""
import logging
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import CONF_MARKDOWN_COLOR, DEFAULT_MARKDOWN_COLOR, DOMAIN
from . import get_device_info

_LOGGER = logging.getLogger(__name__)

COLOR_OPTIONS = ["none", "red", "orange", "yellow", "green"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([ZaloBotMarkdownColorSelect(hass, config_entry)])


class ZaloBotMarkdownColorSelect(SelectEntity):
    """Select entity để chọn màu cho markdown bold."""

    _attr_has_entity_name = True
    _attr_name = "Markdown Color"
    _attr_icon = "mdi:palette"
    _attr_options = COLOR_OPTIONS

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        super().__init__()
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_markdown_color"
        self._attr_device_info = get_device_info()

    @property
    def current_option(self) -> str:
        return self.config_entry.data.get(CONF_MARKDOWN_COLOR, DEFAULT_MARKDOWN_COLOR)

    async def async_select_option(self, option: str) -> None:
        self.hass.data[DOMAIN][CONF_MARKDOWN_COLOR] = option
        data = {**self.config_entry.data}
        data[CONF_MARKDOWN_COLOR] = option
        self.hass.config_entries.async_update_entry(self.config_entry, data=data)
        self.async_write_ha_state()
        _LOGGER.info("Markdown color set to: %s", option)
