"""Config flow for Zalo Bot integration."""

from __future__ import annotations

from typing import Any

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_ZALO_SERVER,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ENABLE_NOTIFICATIONS,
    DEFAULT_ENABLE_NOTIFICATIONS,
)
from .server_session import normalize_server_url

THOI_GIAN_CHO = 10


class KhongKetNoiDuoc(Exception):
    """Không gọi được tới máy chủ Zalo."""


class SaiTaiKhoan(Exception):
    """Máy chủ Zalo từ chối tài khoản hoặc mật khẩu."""


def _thu_ket_noi(server: str, username: str, password: str) -> None:
    """Gọi thử /api/login để biết cấu hình có dùng được không.

    Bản cũ nhận input rồi tạo entry ngay, không kiểm gì cả. Gõ nhầm địa chỉ hay
    sai mật khẩu thì phải tới lúc gọi service đầu tiên mới biết — mà lúc đó lỗi
    hiện ra dưới dạng một thông báo khó hiểu, không phải một dòng đỏ ngay trong
    khung cấu hình.
    """
    try:
        response = requests.post(
            f"{server}/api/login",
            json={"username": username, "password": password},
            timeout=THOI_GIAN_CHO,
        )
    except requests.RequestException as err:
        raise KhongKetNoiDuoc from err

    if response.status_code in (401, 403):
        raise SaiTaiKhoan
    if response.status_code == 429:
        # Máy chủ giới hạn 10 lần sai / 15 phút cho mỗi IP.
        raise SaiTaiKhoan
    if response.status_code >= 400:
        raise KhongKetNoiDuoc

    try:
        data = response.json()
    except ValueError as err:
        raise KhongKetNoiDuoc from err

    if data.get("success") is not True:
        raise SaiTaiKhoan


def _khung_nhap(gia_tri: dict[str, Any]) -> vol.Schema:
    """Khung nhập dùng chung cho cả lần cấu hình đầu và lần sửa tuỳ chọn.

    Mật khẩu KHÔNG còn giá trị mặc định 'admin': máy chủ đã bỏ tài khoản
    admin/admin từ lâu, nên điền sẵn chỉ dẫn người dùng vào một lần đăng nhập
    chắc chắn thất bại — mà mỗi lần thất bại lại ăn một suất trong giới hạn 10
    lần sai / 15 phút của máy chủ.
    """
    return vol.Schema(
        {
            vol.Required(
                CONF_ZALO_SERVER,
                default=gia_tri.get(CONF_ZALO_SERVER, "http://127.0.0.1:3000"),
            ): str,
            vol.Required(CONF_USERNAME, default=gia_tri.get(CONF_USERNAME, "admin")): str,
            vol.Required(CONF_PASSWORD, default=gia_tri.get(CONF_PASSWORD, "")): str,
            vol.Optional(
                CONF_ENABLE_NOTIFICATIONS,
                default=gia_tri.get(
                    CONF_ENABLE_NOTIFICATIONS, DEFAULT_ENABLE_NOTIFICATIONS
                ),
            ): bool,
        }
    )


async def _kiem_va_chuan_hoa(hass, user_input: dict[str, Any]) -> dict[str, Any]:
    """Chuẩn hoá địa chỉ rồi thử kết nối. Ném KhongKetNoiDuoc / SaiTaiKhoan."""
    server = normalize_server_url(user_input[CONF_ZALO_SERVER])
    await hass.async_add_executor_job(
        _thu_ket_noi, server, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
    )
    du_lieu = dict(user_input)
    du_lieu[CONF_ZALO_SERVER] = server
    return du_lieu


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zalo Bot."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Bước cấu hình đầu tiên."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                du_lieu = await _kiem_va_chuan_hoa(self.hass, user_input)
            except KhongKetNoiDuoc:
                errors["base"] = "cannot_connect"
            except SaiTaiKhoan:
                errors["base"] = "invalid_auth"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Zalo Bot", data=du_lieu)

        return self.async_show_form(
            step_id="user",
            data_schema=_khung_nhap(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Sửa cấu hình đã lưu."""
        hien_tai = {**self.config_entry.data, **self.config_entry.options}
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                du_lieu = await _kiem_va_chuan_hoa(self.hass, user_input)
            except KhongKetNoiDuoc:
                errors["base"] = "cannot_connect"
            except SaiTaiKhoan:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(title="", data=du_lieu)

        return self.async_show_form(
            step_id="init",
            data_schema=_khung_nhap(user_input or hien_tai),
            errors=errors,
        )
