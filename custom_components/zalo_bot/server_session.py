"""Phiên HTTP dùng chung để nói chuyện với Zalo Bot Server.

Lớp này thay cho `requests.Session()` trần và giải quyết hai chuyện:

1. **Hạn chờ.** Bản cũ gọi `session.post(url, json=payload)` ở gần một trăm chỗ mà
   không đặt `timeout`, tức là chờ vô hạn theo mặc định của `requests`. Các lời
   gọi đó chạy trong executor thread pool của Home Assistant, nên một máy chủ
   Zalo treo sẽ giữ chặt từng thread cho tới khi TCP tự bỏ cuộc. Đặt hạn chờ ở
   một chỗ duy nhất trong `request()` bao được hết mọi lời gọi.

2. **Đăng nhập lặp.** Bản cũ gọi `POST /api/login` đầy đủ trước MỖI service, dù
   `requests.Session` đã giữ sẵn cookie phiên. Máy chủ băm mật khẩu bằng PBKDF2
   600.000 vòng chạy đồng bộ — đo được 0,45 giây trên máy dev, 1,5–3 giây trên
   máy ARM — và trong lúc băm thì event loop của Node đứng hình, không nhận được
   tin Zalo nào. Nay chỉ đăng nhập lại khi phiên quá hạn hoặc khi máy chủ trả
   401.

Chỉ những yêu cầu đi tới ĐÚNG máy chủ Zalo mới được gắn đăng nhập. `chat_features`
còn dùng chung phiên này để tải tệp từ URL khác (thư mục www của Home Assistant);
những lời gọi đó không được kéo theo đăng nhập hay thử lại.
"""

from __future__ import annotations

import logging
import threading
import time
from urllib.parse import urlsplit

import requests

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60
DEFAULT_AUTH_TTL = 6 * 60 * 60


def normalize_server_url(value: str) -> str:
    """Chuẩn hoá địa chỉ máy chủ người dùng nhập trong config flow."""
    text = str(value or "").strip().rstrip("/")
    if text and not text.startswith(("http://", "https://")):
        text = f"http://{text}"
    return text


class ZaloServerSession(requests.Session):
    """Phiên requests tự đặt hạn chờ và tự giữ trạng thái đăng nhập."""

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        auth_ttl: int = DEFAULT_AUTH_TTL,
    ) -> None:
        super().__init__()
        self.server = normalize_server_url(server)
        self.username = username
        self.password = password
        self.timeout = timeout
        self._auth_ttl = auth_ttl
        self._auth_lock = threading.RLock()
        self._authenticated_at = 0.0

    # ------------------------------------------------------------------
    # Đăng nhập
    # ------------------------------------------------------------------

    def _con_han(self) -> bool:
        return bool(self._authenticated_at) and (
            time.monotonic() - self._authenticated_at < self._auth_ttl
        )

    def authenticate(self, force: bool = False) -> None:
        """Bảo đảm phiên đang có cookie đăng nhập hợp lệ.

        Ném ConnectionError khi máy chủ từ chối, để service gọi nó báo lỗi rõ
        ràng thay vì gửi tiếp một yêu cầu chắc chắn nhận 401.
        """
        if not force and self._con_han():
            return

        with self._auth_lock:
            # Kiểm lại sau khi giành được khoá: một luồng khác có thể vừa đăng
            # nhập xong trong lúc luồng này đang chờ.
            if not force and self._con_han():
                return

            response = super().request(
                "POST",
                f"{self.server}/api/login",
                json={"username": self.username, "password": self.password},
                timeout=10,
            )
            try:
                data = response.json()
            except ValueError as err:
                self._authenticated_at = 0.0
                raise ConnectionError(
                    "Máy chủ Zalo trả về dữ liệu đăng nhập không đọc được "
                    f"(HTTP {response.status_code})"
                ) from err

            if response.status_code != 200 or data.get("success") is not True:
                self._authenticated_at = 0.0
                ly_do = data.get("message") or data.get("error") or "không rõ lý do"
                raise ConnectionError(
                    f"Đăng nhập máy chủ Zalo thất bại (HTTP {response.status_code}): {ly_do}"
                )

            self._authenticated_at = time.monotonic()
            _LOGGER.debug("Đã đăng nhập máy chủ Zalo, giữ phiên %d giây", self._auth_ttl)

    def invalidate_auth(self) -> None:
        """Quên trạng thái đăng nhập; lần gọi sau sẽ đăng nhập lại."""
        self._authenticated_at = 0.0

    # ------------------------------------------------------------------
    # Gửi yêu cầu
    # ------------------------------------------------------------------

    def _la_may_chu_zalo(self, url: str) -> bool:
        dich = urlsplit(str(url))
        goc = urlsplit(self.server)
        return dich.scheme == goc.scheme and dich.netloc == goc.netloc

    def request(self, method, url, **kwargs):
        """Đặt hạn chờ mặc định, tự đăng nhập, và thử lại một lần khi gặp 401."""
        kwargs.setdefault("timeout", self.timeout)

        cua_may_chu = self._la_may_chu_zalo(url)
        la_duong_login = cua_may_chu and str(url).rstrip("/") == f"{self.server}/api/login"

        if cua_may_chu and not la_duong_login:
            self.authenticate()

        response = super().request(method, url, **kwargs)

        if cua_may_chu and not la_duong_login and response.status_code == 401:
            # Máy chủ khởi động lại thì kho phiên trống, cookie cũ hết giá trị.
            _LOGGER.debug("Máy chủ Zalo trả 401, đăng nhập lại rồi thử lại một lần")
            response.close()
            self.authenticate(force=True)
            response = super().request(method, url, **kwargs)

        return response
