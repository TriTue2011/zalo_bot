"""Cảm biến nhị phân cho Zalo Bot."""
from __future__ import annotations

import logging
import aiohttp
import json
from datetime import timedelta
from typing import Any
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import DOMAIN, CONF_ZALO_SERVER, CONF_USERNAME, CONF_PASSWORD
from . import get_device_info

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Thiết lập cảm biến nhị phân."""
    config = hass.data[DOMAIN].get(entry.entry_id, {})
    zalo_server = config.get(CONF_ZALO_SERVER)
    username = config.get(CONF_USERNAME, "admin")
    password = config.get(CONF_PASSWORD, "admin")
    coordinator = ZaloLoginCoordinator(hass, zalo_server, username, password)
    await coordinator.async_config_entry_first_refresh()
    # Đóng phiên aiohttp khi gỡ tích hợp. Mỗi lần lưu cấu hình là entry được nạp
    # lại, tức là tạo thêm một phiên mới; không đăng ký đóng thì phiên cũ nằm lại
    # và Home Assistant báo "Unclosed client session" dồn dần.
    entry.async_on_unload(coordinator.async_close)
    async_add_entities([
        ZaloLoginBinarySensor(coordinator, entry),
        ZaloServerBinarySensor(coordinator, entry)
    ], True)


class ZaloLoginCoordinator(DataUpdateCoordinator):
    """Kiểm tra đăng nhập Zalo."""

    def __init__(self, hass: HomeAssistant, zalo_server: str, username: str, password: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Zalo Login",
            update_interval=SCAN_INTERVAL,
        )
        self.zalo_server = zalo_server
        self.username = username
        self.password = password
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        self.data = {"logged_in": False, "total": 0, "accounts": []}
        self.server_reachable = False
        self.login_success = False

    async def _con_phien(self) -> bool:
        """True nếu cookie phiên đang giữ vẫn còn được máy chủ chấp nhận."""
        try:
            async with self.session.get(
                f"{self.zalo_server}/api/check-auth",
                headers={"Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    return False
                return json.loads(await resp.text()).get("authenticated") is True
        except (aiohttp.ClientError, ValueError, TimeoutError):
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Kiểm tra đăng nhập qua API."""
        self.server_reachable = False
        try:
            try:
                async with self.session.get(
                    f"{self.zalo_server}", 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    self.server_reachable = True
            except:
                self.login_success = False
                return {"logged_in": False, "total": 0, "accounts": []}
            # Hỏi xem phiên cũ còn dùng được không TRƯỚC khi đăng nhập lại.
            #
            # Bản cũ gửi POST /api/login mỗi 60 giây. Máy chủ băm mật khẩu bằng
            # PBKDF2 600.000 vòng chạy đồng bộ (0,45 giây trên máy dev, 1,5–3
            # giây trên máy ARM) và trong lúc băm thì event loop của Node đứng
            # hình, không nhận được tin Zalo nào. Cookie phiên nằm trong cookie
            # jar của chính coordinator này và máy chủ đặt hạn 30 ngày, nên hầu
            # hết các lượt cập nhật không cần đăng nhập lại chút nào.
            #
            # Đăng nhập lại dồn dập còn ăn vào giới hạn 10 lần sai / 15 phút của
            # máy chủ khi mật khẩu bị cấu hình sai.
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            self.login_success = await self._con_phien()
            if not self.login_success:
                login_data = {"username": self.username, "password": self.password}
                async with self.session.post(
                    f"{self.zalo_server}/api/login",
                    json=login_data,
                    headers=headers
                ) as resp:
                    if resp.status != 200:
                        self.login_success = False
                        return {"logged_in": False, "total": 0, "accounts": []}
                    try:
                        login_resp = json.loads(await resp.text())
                        self.login_success = login_resp.get("success", False) is True
                    except (ValueError, aiohttp.ClientError):
                        self.login_success = False
            async with self.session.get(
                f"{self.zalo_server}/api/accounts",
                headers={"Accept": "application/json"}
            ) as resp:
                if resp.status != 200:
                    return {"logged_in": False, "total": 0, "accounts": []}
                try:
                    response = json.loads(await resp.text())
                    if response.get("success"):
                        return {
                            "logged_in": response.get("total", 0) > 0,
                            "total": response.get("total", 0),
                            "accounts": response.get("data", [])
                        }
                except:
                    pass
        except Exception:
            self.server_reachable = False
            self.login_success = False
        return {"logged_in": False, "total": 0, "accounts": []}
    async def async_close(self) -> None:
        """Đóng phiên aiohttp và dừng vòng cập nhật."""
        await self.session.close()
        # Lớp cha là DataUpdateCoordinator, không có async_close — tên đúng là
        # async_shutdown. Gọi sai tên thì chính hàm này ném AttributeError.
        await self.async_shutdown()


class ZaloLoginBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Cảm biến nhị phân cho trạng thái đăng nhập Zalo."""
    _attr_has_entity_name = True
    _attr_name = "Zalo Login"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    def __init__(
        self,
        coordinator: ZaloLoginCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_login_status"
        self._attr_device_info = get_device_info()

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("logged_in", False)
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "total_accounts": self.coordinator.data.get("total", 0),
            "accounts": self.coordinator.data.get("accounts", []),
        }
    _attr_icon = "mdi:account"


class ZaloServerBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Cảm biến nhị phân cho trạng thái kết nối Zalo Server."""
    _attr_has_entity_name = True
    _attr_name = "Zalo Server"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    def __init__(
        self,
        coordinator: ZaloLoginCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_server_status"
        self._attr_device_info = get_device_info()
    @property
    def is_on(self) -> bool:
        resp_status = getattr(self.coordinator, "login_success", False)
        return resp_status
    _attr_icon = "mdi:server"
