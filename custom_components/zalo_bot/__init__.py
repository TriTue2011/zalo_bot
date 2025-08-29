"""Zalo Bot integration."""
import asyncio
import logging
import os
import shutil
import socket
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv, device_registry as dr
from .const import (
    CONF_ENABLE_NOTIFICATIONS,
    CONF_ZALO_SERVER,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_ENABLE_NOTIFICATIONS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Định nghĩa CONFIG_SCHEMA để chỉ ra rằng tích hợp này chỉ sử dụng config entry
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.SWITCH]
SIGNAL_NOTIFICATION_TOGGLE = f"{DOMAIN}_notification_toggle"

# Schema cho các service
SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_SEND_FILE_SCHEMA = vol.Schema({
    vol.Required("file_path_or_url"): cv.string,
    vol.Optional("message"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_SEND_IMAGE_SCHEMA = vol.Schema({
    vol.Required("image_path"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA = vol.Schema({})

SERVICE_GET_ACCOUNT_DETAILS_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_FIND_USER_SCHEMA = vol.Schema({
    vol.Optional("phone", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_USER_INFO_SCHEMA = vol.Schema({
    vol.Optional("user_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Optional("user_id", default=""): cv.string,
    vol.Optional("message", default="Xin chào, hãy kết bạn với tôi!"): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_CREATE_GROUP_SCHEMA = vol.Schema({
    vol.Optional("members", default=""): cv.string,
    vol.Optional("name", default=""): cv.string,
    vol.Optional("avatar_path", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_GROUP_INFO_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_ADD_USER_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("member_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA = vol.Schema({
    vol.Optional("group_id", default=""): cv.string,
    vol.Optional("member_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGE_TO_USER_SCHEMA = vol.Schema({
    vol.Optional("image_path", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGES_TO_USER_SCHEMA = vol.Schema({
    vol.Optional("image_paths", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("image_path", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA = vol.Schema({
    vol.Optional("image_paths", default=""): cv.string,
    vol.Optional("thread_id", default=""): cv.string,
    vol.Optional("account_selection", default=""): cv.string,
})

SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA = vol.Schema({})

SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
    vol.Optional("message_webhook_url", default=""): cv.string,
    vol.Optional("group_event_webhook_url", default=""): cv.string,
    vol.Optional("reaction_webhook_url", default=""): cv.string,
})

SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
    vol.Optional("own_id", default=""): cv.string,
})

SERVICE_GET_PROXIES_SCHEMA = vol.Schema({})

SERVICE_ADD_PROXY_SCHEMA = vol.Schema({
    vol.Optional("proxy_url", default=""): cv.string,
})

SERVICE_REMOVE_PROXY_SCHEMA = vol.Schema({
    vol.Optional("proxy_url", default=""): cv.string,
})

# Thêm schema cho các service mới
SERVICE_ACCEPT_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_BLOCK_USER_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UNBLOCK_USER_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_STICKER_SCHEMA = vol.Schema({
    vol.Required("sticker_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_UNDO_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("msg_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_CREATE_REMINDER_SCHEMA = vol.Schema({
    vol.Required("title"): cv.string,
    vol.Required("content"): cv.string,
    vol.Required("remind_time"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_REMOVE_REMINDER_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

SERVICE_CHANGE_GROUP_NAME_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("name"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_GROUP_AVATAR_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("image_path"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_VOICE_SCHEMA = vol.Schema({
    vol.Required("voice_path"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
    vol.Optional("type", default="0"): cv.string,
})

# Schema cho các API mới bổ sung
SERVICE_GET_ALL_FRIENDS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_RECEIVED_FRIEND_REQUESTS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_SENT_FRIEND_REQUESTS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_UNDO_FRIEND_REQUEST_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_FRIEND_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_FRIEND_ALIAS_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("alias"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_FRIEND_ALIAS_SCHEMA = vol.Schema({
    vol.Required("friend_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_ALL_GROUPS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_GROUP_DEPUTY_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_GROUP_DEPUTY_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_GROUP_OWNER_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("member_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DISPERSE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_ENABLE_GROUP_LINK_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DISABLE_GROUP_LINK_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_JOIN_GROUP_SCHEMA = vol.Schema({
    vol.Required("link"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_LEAVE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Optional("silent", default=False): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_PROFILE_SCHEMA = vol.Schema({
    vol.Optional("name"): cv.string,
    vol.Optional("dob"): cv.string,
    vol.Optional("gender", default="0"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_SETTINGS_SCHEMA = vol.Schema({
    vol.Required("setting_type"): cv.string,
    vol.Required("status"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_MUTE_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("duration"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_PINNED_CONVERSATION_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("pinned"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

# Các schema cho API mới bổ sung thêm
SERVICE_GET_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_UNREAD_MARK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_ARCHIVED_CHAT_LIST_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_AUTO_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_AUTO_DELETE_CHAT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("ttl"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_HIDDEN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_SET_HIDDEN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("hidden"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_HIDDEN_CONVERS_PIN_SCHEMA = vol.Schema({
    vol.Required("pin"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_RESET_HIDDEN_CONVERS_PIN_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_MUTE_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_PIN_CONVERSATIONS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_REACTION_SCHEMA = vol.Schema({
    vol.Required("icon"): cv.string,
    vol.Required("thread_id"): cv.string,
    vol.Required("msg_id"): cv.string,
    vol.Required("cli_msg_id"): cv.string,
    vol.Required("type"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_DELETE_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("msg_id"): cv.string,
    vol.Required("cli_msg_id"): cv.string,
    vol.Required("uid_from"): cv.string,
    vol.Required("type"): cv.string,
    vol.Optional("only_me", default=True): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_FORWARD_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Required("thread_ids"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_PARSE_LINK_SCHEMA = vol.Schema({
    vol.Required("link"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_CARD_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_LINK_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("link"): cv.string,
    vol.Optional("message", default=""): cv.string,
    vol.Optional("thumbnail", default=""): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_STICKERS_SCHEMA = vol.Schema({
    vol.Required("query"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_STICKERS_DETAIL_SCHEMA = vol.Schema({
    vol.Required("sticker_album"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_VIDEO_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("video_path_or_url"): cv.string,
    vol.Optional("thumbnail_url", default=""): cv.string,
    vol.Optional("message", default=""): cv.string,
    vol.Optional("width", default=1280): cv.positive_int,
    vol.Optional("height", default=720): cv.positive_int,
    vol.Optional("ttl", default=0): cv.positive_int,
    vol.Optional("type", default="0"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CREATE_NOTE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Optional("pin_act", default=True): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_EDIT_NOTE_GROUP_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("topic_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LIST_BOARD_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CREATE_POLL_SCHEMA = vol.Schema({
    vol.Required("group_id"): cv.string,
    vol.Required("question"): cv.string,
    vol.Required("options"): cv.string,
    vol.Optional("allow_multi_choices", default=False): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_POLL_DETAIL_SCHEMA = vol.Schema({
    vol.Required("poll_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_LOCK_POLL_SCHEMA = vol.Schema({
    vol.Required("poll_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_EDIT_REMINDER_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("topic_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_REMINDER_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LIST_REMINDER_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_REMINDER_RESPONSES_SCHEMA = vol.Schema({
    vol.Required("reminder_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_ADD_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("keyword"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_REMOVE_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("item_ids"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_UPDATE_QUICK_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("item_id"): cv.string,
    vol.Required("keyword"): cv.string,
    vol.Required("title"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_LABELS_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_BLOCK_VIEW_FEED_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("is_block_feed"): cv.boolean,
    vol.Required("account_selection"): cv.string,
})

SERVICE_CHANGE_ACCOUNT_AVATAR_SCHEMA = vol.Schema({
    vol.Required("avatar_source"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_GET_AVATAR_LIST_SCHEMA = vol.Schema({
    vol.Required("account_selection"): cv.string,
})

SERVICE_LAST_ONLINE_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

SERVICE_SEND_TYPING_EVENT_SCHEMA = vol.Schema({
    vol.Required("thread_id"): cv.string,
    vol.Required("account_selection"): cv.string,
})

session = requests.Session()
zalo_server = None
WWW_DIR = None
PUBLIC_DIR = None


def get_video_duration_ms(video_path):
    """
    Lấy duration chính xác của video bằng ffprobe

    Args:
        video_path: Đường dẫn đến file video

    Returns:
        int: Duration tính bằng milliseconds
    """
    if not os.path.isfile(video_path):
        _LOGGER.warning(f"Video file not found: {video_path}")
        return 10000

    try:
        import subprocess
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            duration_seconds = float(data['format']['duration'])
            duration_ms = max(int(duration_seconds * 1000), 1000)
            _LOGGER.info(
                f"ffprobe detected duration: {duration_seconds:.2f}s = "
                f"{duration_ms}ms for {os.path.basename(video_path)}"
            )
            return duration_ms
        else:
            _LOGGER.warning(f"ffprobe failed for {video_path}: {result.stderr}")
            return 10000

    except Exception as e:
        _LOGGER.warning(f"ffprobe error for {video_path}: {e}")
        return 10000


def find_free_port():
    """Tìm một cổng trống."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def serve_file_temporarily(file_path, duration=60):
    """
    Phục vụ một tệp thông qua HTTP tạm thời và trả về URL

    :param file_path: Đường dẫn đến tệp cần phục vụ
    :param duration: Thời gian (giây) máy chủ chạy trước khi đóng
    :return: URL đến tệp đang được phục vụ
    """
    # Tạo thư mục ảo với chỉ một tệp
    file_name = os.path.basename(file_path)
    encoded_filename = urllib.parse.quote(file_name)

    # Tìm một cổng trống
    port = find_free_port()

    # Chuẩn bị máy chủ
    class SingleFileHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == f"/{encoded_filename}" or self.path == "/":
                try:
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        content_type = "image/jpeg"  # Mặc định
                        if file_path.endswith(".png"):
                            content_type = "image/png"
                        elif file_path.endswith(".gif"):
                            content_type = "image/gif"
                        elif file_path.endswith(".webp"):
                            content_type = "image/webp"
                        elif file_path.endswith(".mp4"):
                            content_type = "video/mp4"
                        elif file_path.endswith(".avi"):
                            content_type = "video/avi"
                        elif file_path.endswith(".mov"):
                            content_type = "video/quicktime"
                        elif file_path.endswith(".webm"):
                            content_type = "video/webm"
                        elif file_path.endswith(".mp3"):
                            content_type = "audio/mpeg"
                        elif file_path.endswith(".wav"):
                            content_type = "audio/wav"
                        self.send_header("Content-type", content_type)
                        # Thêm Content-Length để hỗ trợ HEAD request
                        file_size = os.path.getsize(file_path)
                        self.send_header("Content-Length", str(file_size))
                        self.end_headers()
                        self.wfile.write(file.read())
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi phục vụ tệp: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Internal Server Error")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File Not Found")

        def do_HEAD(self):
            # Hỗ trợ HEAD request để kiểm tra file có tồn tại không
            if self.path == f"/{encoded_filename}" or self.path == "/":
                try:
                    if os.path.isfile(file_path):
                        self.send_response(200)
                        content_type = "image/jpeg"  # Mặc định
                        if file_path.endswith(".png"):
                            content_type = "image/png"
                        elif file_path.endswith(".gif"):
                            content_type = "image/gif"
                        elif file_path.endswith(".webp"):
                            content_type = "image/webp"
                        elif file_path.endswith(".mp4"):
                            content_type = "video/mp4"
                        elif file_path.endswith(".avi"):
                            content_type = "video/avi"
                        elif file_path.endswith(".mov"):
                            content_type = "video/quicktime"
                        elif file_path.endswith(".webm"):
                            content_type = "video/webm"
                        elif file_path.endswith(".mp3"):
                            content_type = "audio/mpeg"
                        elif file_path.endswith(".wav"):
                            content_type = "audio/wav"
                        self.send_header("Content-type", content_type)
                        # Thêm Content-Length cho HEAD request
                        file_size = os.path.getsize(file_path)
                        self.send_header("Content-Length", str(file_size))
                        self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi xử lý HEAD request: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Tắt log để không làm ảnh hưởng đến log của Home Assistant
            pass

    # Tạo máy chủ và chạy trong một thread riêng
    httpd = HTTPServer(("0.0.0.0", port), SingleFileHandler)

    # Lấy địa chỉ IP local
    try:
        # Cố gắng lấy IP trong mạng LAN
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Kết nối đến Google DNS
        local_ip = s.getsockname()[0]
        s.close()
    except (socket.error, OSError) as e:
        # Fallback nếu không thể xác định
        _LOGGER.warning(f"Không thể xác định IP LAN: {e}, dùng hostname")
        local_ip = socket.gethostbyname(socket.gethostname())

    # URL để truy cập tệp
    url = f"http://{local_ip}:{port}/{encoded_filename}"

    # Chạy máy chủ trong thread riêng
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Lên lịch đóng máy chủ sau một khoảng thời gian
    def close_server():
        time.sleep(duration)
        httpd.shutdown()
        httpd.server_close()
        _LOGGER.debug(f"Máy chủ tạm thời cho {file_name} đã dừng")

    shutdown_thread = threading.Thread(target=close_server)
    shutdown_thread.daemon = True
    shutdown_thread.start()

    _LOGGER.debug(f"Đang phục vụ {file_name} tại {url} trong {duration} giây")
    return url


# Hàm tiện ích để hiển thị kết quả từ server trong UI
async def show_result_notification(hass, service_name, resp, error=None):
    try:
        # Kiểm tra xem thông báo có được bật không
        notifications_enabled = True
        for entry_id in hass.data.get(DOMAIN, {}):
            if CONF_ENABLE_NOTIFICATIONS in hass.data[DOMAIN][entry_id]:
                notifications_enabled = hass.data[DOMAIN][entry_id][CONF_ENABLE_NOTIFICATIONS]
                break

        # Nếu thông báo bị tắt, chỉ ghi log và không hiển thị thông báo
        if not notifications_enabled:
            if error:
                _LOGGER.info(f"Thông báo bị tắt. Lỗi khi thực hiện {service_name}: {str(error)}")
            elif resp:
                _LOGGER.info(
                    f"Thông báo bị tắt. Kết quả {service_name}: "
                    f"{resp.text if hasattr(resp, 'text') else str(resp)}"
                )
            return

        if error:
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Lỗi khi thực hiện {service_name}: {str(error)}",
                    "title": f"Zalo Bot - Lỗi {service_name}",
                    "notification_id": f"zalo_bot_{service_name}_error_{int(time.time())}"
                }
            )
            return

        try:
            resp_json = resp.json()
            success = resp_json.get("success", False)

            # Lấy thông tin chi tiết từ kết quả API
            message = resp_json.get("message", "")
            data = resp_json.get("data", {})

            # Nếu có dữ liệu và không có message, tạo thông tin chi tiết hơn
            if success and data:
                details = []

                # Thông tin người dùng
                if "display_name" in data:
                    details.append(f"Tên: {data.get('display_name', '')}")
                if "zalo_name" in data:
                    details.append(f"Zalo Name: {data.get('zalo_name', '')}")
                if "uid" in data:
                    details.append(f"UID: {data.get('uid', '')}")
                if "gender" in data:
                    gender = "Nam" if data.get("gender") == 1 else "Nữ" if data.get("gender") == 2 else "Không xác định"
                    details.append(f"Giới tính: {gender}")
                if "sdob" in data:
                    details.append(f"Ngày sinh: {data.get('sdob', '')}")

                # Thông tin tài khoản sử dụng
                if "usedAccount" in resp_json and isinstance(resp_json["usedAccount"], dict):
                    acc = resp_json["usedAccount"]
                    if "phoneNumber" in acc:
                        details.append(f"SĐT Bot: {acc.get('phoneNumber', '')}")
                    if "ownId" in acc:
                        details.append(f"ID Bot: {acc.get('ownId', '')}")

                # Nếu là danh sách
                if not details and isinstance(data, list) and len(data) > 0:
                    details.append(f"Tìm thấy {len(data)} kết quả")

                # Nếu vẫn không có chi tiết cụ thể, thử lấy các giá trị đơn giản
                if not details:
                    count = 0
                    for key, value in data.items():
                        if count < 5 and isinstance(value, (str, int, float, bool)):
                            details.append(f"{key}: {value}")
                            count += 1

                message = "\n".join(details) if details else "Thành công"

            # Nếu vẫn không có message, dùng giá trị mặc định
            if not message:
                message = "Không có thông tin chi tiết"

            if success:
                await hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "message": f"Thực hiện {service_name} thành công!\n\n{message}",
                        "title": f"Zalo Bot - {service_name} thành công",
                        "notification_id": f"zalo_bot_{service_name}_{int(time.time())}"
                    }
                )
            else:
                await hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "message": f"Thực hiện {service_name} thất bại!\nLỗi: {message}",
                        "title": f"Zalo Bot - {service_name} thất bại",
                        "notification_id": f"zalo_bot_{service_name}_{int(time.time())}"
                    }
                )
        except Exception as e:
            _LOGGER.error("Lỗi khi tạo thông báo: %s", e)
            await hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Lỗi khi hiển thị kết quả: {str(e)}",
                    "title": "Zalo Bot - Lỗi hiển thị",
                    "notification_id": f"zalo_bot_notification_error_{int(time.time())}"
                }
            )
    except Exception as e:
        _LOGGER.error("Lỗi trong show_result_notification: %s", e)


def copy_to_public(src_path, zalo_server):
    if not os.path.isfile(src_path):
        _LOGGER.error("Tệp ảnh không tìm thấy: %s", src_path)
        return None
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    filename = os.path.basename(src_path)
    dst_path = os.path.join(PUBLIC_DIR, filename)
    shutil.copy(src_path, dst_path)
    url_path = f"/local/zalo_bot/{filename}"
    _LOGGER.info("Đã sao chép ảnh từ %s đến %s, URL truy cập: %s", src_path, dst_path, url_path)
    return url_path


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})

    # Lưu trữ dữ liệu cấu hình từ entry
    config = dict(entry.data)

    # Đảm bảo có cài đặt enable_notifications
    if CONF_ENABLE_NOTIFICATIONS not in config:
        config[CONF_ENABLE_NOTIFICATIONS] = DEFAULT_ENABLE_NOTIFICATIONS

    # Khởi tạo session và các biến toàn cục
    global session, zalo_server, WWW_DIR, PUBLIC_DIR
    session = requests.Session()

    # Lấy thông tin cấu hình
    zalo_server = config.get(CONF_ZALO_SERVER)
    admin_user = config.get(CONF_USERNAME, "admin")
    admin_pass = config.get(CONF_PASSWORD, "admin")

    # Cập nhật dữ liệu trong hass.data
    hass.data[DOMAIN][entry.entry_id] = config

    # Kiểm tra xem zalo_server có giá trị không
    if not zalo_server:
        _LOGGER.error("Không tìm thấy URL máy chủ Zalo Bot. Vui lòng kiểm tra cấu hình.")
        return False

    # Thiết lập đường dẫn thư mục
    config_dir = hass.config.path()
    WWW_DIR = os.path.join(config_dir, "www")
    PUBLIC_DIR = os.path.join(WWW_DIR, "zalo_bot")

    # Khởi tạo các platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    def zalo_login():
        resp = session.post(f"{zalo_server}/api/login", json={
            "username": admin_user,
            "password": admin_pass
        })
        if resp.status_code == 200 and resp.json().get("success"):
            _LOGGER.info("Đăng nhập quản trị viên Zalo thành công")
        else:
            _LOGGER.error("Đăng nhập quản trị viên Zalo thất bại: %s", resp.text)

    try:
        pass

    except Exception:
        pass

    async def async_send_message_service(call):
        _LOGGER.debug("Dịch vụ async_send_message_service được gọi với dữ liệu: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")
            # Sửa lại type: nếu là group thì dùng 1 (số), nếu là user thì 0
            payload = {
                "message": call.data["message"],
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": 1 if msg_type == "1" else 0
            }
            _LOGGER.debug("Gửi POST đến %s/api/sendMessageByAccount với payload: %s",
                          zalo_server, payload)
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendMessageByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi tin nhắn: %s", resp.text)
            await show_result_notification(hass, "gửi tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Exception trong async_send_message_service: %s", e, exc_info=True)
            await show_result_notification(hass, "gửi tin nhắn", None, error=e)

    async def async_send_file_service(call):
        _LOGGER.debug("Dịch vụ async_send_file_service được gọi với dữ liệu: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")
            file_path = call.data["file_path_or_url"]
            public_url = None

            if file_path.startswith("http://") or file_path.startswith("https://"):
                public_url = file_path
            else:
                if not os.path.isfile(file_path):
                    error_msg = f"Không tìm thấy tệp: {file_path}"
                    await show_result_notification(hass, "gửi file", None, error=error_msg)
                    return

                try:
                    is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
                    if is_local_server:
                        public_url = await hass.async_add_executor_job(copy_to_public, file_path, zalo_server)
                        if not public_url:
                            error_msg = "Không thể copy tệp đến thư mục public"
                            await show_result_notification(hass, "gửi file", None, error=error_msg)
                            return
                        if public_url.startswith("/local/"):
                            filename = os.path.basename(file_path)
                            public_url = f"{zalo_server}/{filename}"
                    else:
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ tệp: {file_path}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, file_path, 90
                        )
                except Exception as e:
                    error_msg = f"Lỗi khi xử lý tệp: {str(e)}"
                    _LOGGER.error(error_msg)
                    await show_result_notification(hass, "gửi file", None, error=error_msg)
                    return

            if not public_url:
                await show_result_notification(hass, "gửi file", None, error="Không thể tạo URL công khai cho tệp.")
                return

            payload = {
                "fileUrl": public_url,
                "message": call.data.get("message", ""),
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": "group" if msg_type == "1" else "user"
            }
            _LOGGER.debug("Gửi POST đến %s/api/sendFileByAccount với payload: %s",
                          zalo_server, payload)
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendFileByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi file: %s", resp.text)
            await show_result_notification(hass, "gửi file", resp)
        except Exception as e:
            _LOGGER.error("Exception trong async_send_file_service: %s", e, exc_info=True)
            await show_result_notification(hass, "gửi file", None, error=e)

    async def async_send_image_service(call):
        _LOGGER.debug("Dịch vụ async_send_image_service được gọi với dữ liệu: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")
            image_path = call.data["image_path"]

            if image_path.startswith("http://") or image_path.startswith("https://"):
                public_url = image_path
            else:
                # Kiểm tra tệp tồn tại
                if not os.path.isfile(image_path):
                    error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                    await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                    return

                # Thử copy vào thư mục public (phương pháp cũ) hoặc sử dụng máy chủ tạm thời
                try:
                    # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
                    is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

                    if is_local_server:
                        # Sử dụng phương pháp cũ khi server chạy cùng máy
                        public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                        if not public_url:
                            error_msg = "Không thể copy ảnh đến thư mục public"
                            await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                            return

                        if public_url.startswith("/local/"):
                            filename = os.path.basename(image_path)
                            public_url = f"{zalo_server}/{filename}"
                    else:
                        # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                        )
                except Exception as e:
                    error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                    _LOGGER.error(error_msg)
                    await show_result_notification(hass, "gửi ảnh", None, error=error_msg)
                    return

            payload = {
                "imagePath": public_url,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": "group" if msg_type == "1" else "user"
            }
            _LOGGER.debug("Gửi POST đến %s/api/sendImageByAccount với payload: %s",
                          zalo_server, payload)
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImageByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi ảnh: %s", resp.text)
            await show_result_notification(hass, "gửi ảnh", resp)
        except Exception as e:
            _LOGGER.error("Exception trong async_send_image_service: %s", e, exc_info=True)
            await show_result_notification(hass, "gửi ảnh", None, error=e)

    async def async_send_video_service(call):
        _LOGGER.debug("Dịch vụ async_send_video được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")
            video_path = call.data["video_path_or_url"]
            public_url = None

            # Kiểm tra nếu input là URL hay file local
            if video_path.startswith("http://") or video_path.startswith("https://"):
                public_url = video_path
            else:
                # Xử lý file local
                if not os.path.isfile(video_path):
                    error_msg = f"Không tìm thấy tệp video: {video_path}"
                    await show_result_notification(hass, "gửi video", None, error=error_msg)
                    return

                try:
                    # Luôn dùng HTTP server tạm thời
                    _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ tệp video: {video_path}")
                    public_url = await hass.async_add_executor_job(
                        serve_file_temporarily, video_path, 90
                    )
                except Exception as e:
                    error_msg = f"Lỗi khi xử lý tệp video: {str(e)}"
                    _LOGGER.error(error_msg)
                    await show_result_notification(hass, "gửi video", None, error=error_msg)
                    return

            if not public_url:
                await show_result_notification(hass, "gửi video", None, error="Không thể tạo URL công khai cho video.")
                return

            # Xử lý thumbnail URL nếu là file local
            thumbnail_url = call.data.get("thumbnail_url", public_url)
            if thumbnail_url and not (thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://")):
                # Thumbnail là file local, cần tạo URL tạm thời
                if os.path.isfile(thumbnail_url):
                    try:
                        # Luôn dùng HTTP server tạm thời cho thumbnail
                        thumbnail_url = await hass.async_add_executor_job(
                            serve_file_temporarily, thumbnail_url, 90
                        )
                    except Exception as e:
                        _LOGGER.warning("Không thể xử lý thumbnail file local: %s, dùng URL video làm thumbnail", e)
                        thumbnail_url = public_url
                else:
                    _LOGGER.warning("Không tìm thấy thumbnail file: %s, dùng URL video làm thumbnail", thumbnail_url)
                    thumbnail_url = public_url

            # Luôn auto-detect duration (không cho user nhập)
            if video_path.startswith("http://") or video_path.startswith("https://"):
                # Nếu là URL, để duration mặc định 10000ms
                duration = 10000
            else:
                # Nếu là file local, auto-detect duration
                try:
                    duration = get_video_duration_ms(video_path)
                    _LOGGER.info(f"Auto-detect video duration: {duration}ms từ file {video_path}")
                except Exception as e:
                    _LOGGER.warning(f"Không thể auto-detect duration từ {video_path}: {e}, dùng 10000ms")
                    duration = 10000

            options = {
                "videoUrl": public_url,
                "thumbnailUrl": thumbnail_url,
                "msg": call.data.get("message", ""),
                "duration": int(duration),
                "width": int(call.data.get("width", 1280)),
                "height": int(call.data.get("height", 720)),
                "ttl": int(call.data.get("ttl", 0))
            }

            # Backend expect type: ThreadType enum (0 = User, 1 = Group)
            thread_type_num = 1 if msg_type == "1" else 0

            payload = {
                "threadId": str(call.data["thread_id"]),  # Đảm bảo là string
                "accountSelection": str(call.data["account_selection"]),  # Đảm bảo là string
                "options": options,
                "type": thread_type_num  # Backend expect số ThreadType enum
            }

            _LOGGER.info("Video URL để gửi: %s", public_url)
            _LOGGER.info("Thumbnail URL để gửi: %s", thumbnail_url)

            # Kiểm tra xem URL có accessible không
            try:
                # Đợi một chút để server tạm thời sẵn sàng
                await asyncio.sleep(0.1)
                test_resp = await hass.async_add_executor_job(
                    lambda: session.head(public_url, timeout=10)
                )
                _LOGGER.info("Test video URL accessibility - Status: %s, Headers: %s",
                             test_resp.status_code, dict(test_resp.headers))
                if test_resp.status_code != 200:
                    _LOGGER.warning("Video URL không accessible từ backend: %s", test_resp.status_code)
                    # Thử lại với GET request nếu HEAD không hoạt động
                    try:
                        test_resp_get = await hass.async_add_executor_job(
                            lambda: session.get(public_url, timeout=10, stream=True)
                        )
                        _LOGGER.info("Test video URL với GET - Status: %s", test_resp_get.status_code)
                        test_resp_get.close()
                    except Exception as get_error:
                        _LOGGER.error("GET test cũng thất bại: %s", get_error)
            except Exception as e:
                _LOGGER.error("Không thể test video URL accessibility: %s", e)

            _LOGGER.debug("Options đầy đủ: %s", options)
            _LOGGER.debug("Gửi payload đến sendVideoByAccount: %s", payload)
            url = f"{zalo_server}/api/sendVideoByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Response status: %s", resp.status_code)
            _LOGGER.info("Response headers: %s", dict(resp.headers))
            _LOGGER.info("Response text: %s", resp.text)

            try:
                response_json = resp.json()
                _LOGGER.info("Response JSON: %s", response_json)
                if not response_json.get('success', False):
                    error_detail = response_json.get('error', 'Unknown error')
                    _LOGGER.error("Backend trả về lỗi: %s", error_detail)
            except Exception as json_error:
                _LOGGER.error("Không thể parse JSON response: %s", json_error)

            await show_result_notification(hass, "gửi video", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_video: %s", e)
            await show_result_notification(hass, "gửi video", None, error=e)
    hass.services.async_register(
        DOMAIN, "send_message", async_send_message_service, schema=SERVICE_SEND_MESSAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "send_file", async_send_file_service, schema=SERVICE_SEND_FILE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "send_image", async_send_image_service, schema=SERVICE_SEND_IMAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "send_video", async_send_video_service, schema=SERVICE_SEND_VIDEO_SCHEMA
    )

    # Các schema mới cho các dịch vụ bổ sung
    SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA = vol.Schema({})

    SERVICE_GET_ACCOUNT_DETAILS_SCHEMA = vol.Schema({
        vol.Required("own_id"): str,
    })

    SERVICE_FIND_USER_SCHEMA = vol.Schema({
        vol.Required("phone"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_GET_USER_INFO_SCHEMA = vol.Schema({
        vol.Required("user_id"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_SEND_FRIEND_REQUEST_SCHEMA = vol.Schema({
        vol.Required("user_id"): str,
        vol.Required("account_selection"): str,
        vol.Optional("message", default="Xin chào, hãy kết bạn với tôi!"): str,
    })

    SERVICE_CREATE_GROUP_SCHEMA = vol.Schema({
        vol.Required("members"): str,  # Danh sách ngăn cách bởi dấu phẩy
        vol.Optional("name"): str,
        vol.Optional("avatar_path"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_GET_GROUP_INFO_SCHEMA = vol.Schema({
        vol.Optional("group_id", default=""): str,
        vol.Optional("account_selection", default=""): str,
    })

    SERVICE_ADD_USER_TO_GROUP_SCHEMA = vol.Schema({
        vol.Required("group_id"): str,
        vol.Required("member_id"): str,  # Danh sách ngăn cách bởi dấu phẩy
        vol.Required("account_selection"): str,
    })

    SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA = vol.Schema({
        vol.Required("group_id"): str,
        vol.Required("member_id"): str,  # Danh sách ngăn cách bởi dấu phẩy
        vol.Required("account_selection"): str,
    })

    SERVICE_SEND_IMAGE_TO_USER_SCHEMA = vol.Schema({
        vol.Required("image_path"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_SEND_IMAGES_TO_USER_SCHEMA = vol.Schema({
        vol.Required("image_paths"): str,  # Danh sách URL ngăn cách bởi dấu phẩy
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA = vol.Schema({
        vol.Required("image_path"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA = vol.Schema({
        vol.Required("image_paths"): str,  # Danh sách URL ngăn cách bởi dấu phẩy
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
    })

    SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA = vol.Schema({})

    SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
        vol.Required("own_id"): str,
    })

    SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
        vol.Required("own_id"): str,
        vol.Optional("message_webhook_url"): str,
        vol.Optional("group_event_webhook_url"): str,
        vol.Optional("reaction_webhook_url"): str,
    })

    SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA = vol.Schema({
        vol.Required("own_id"): str,
    })

    SERVICE_GET_PROXIES_SCHEMA = vol.Schema({})

    SERVICE_ADD_PROXY_SCHEMA = vol.Schema({
        vol.Required("proxy_url"): str,
    })

    SERVICE_REMOVE_PROXY_SCHEMA = vol.Schema({
        vol.Required("proxy_url"): str,
    })

    # Triển khai đầy đủ cho tất cả các dịch vụ mới để khắc phục schema không sử dụng
    async def async_get_logged_accounts_service(call):
        _LOGGER.debug("Dịch vụ async_get_logged_accounts được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            resp = await hass.async_add_executor_job(
                lambda: session.get(f"{zalo_server}/api/accounts")
            )
            _LOGGER.info("Phản hồi lấy danh sách tài khoản: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách tài khoản", resp)
        except Exception as e:
            _LOGGER.error(
                "Lỗi trong async_get_logged_accounts: %s", e
            )
            await show_result_notification(hass, "lấy danh sách tài khoản", None, error=e)

    hass.services.async_register(
        DOMAIN,
        "get_logged_accounts",
        async_get_logged_accounts_service,
        schema=SERVICE_GET_LOGGED_ACCOUNTS_SCHEMA,
    )

    async def async_get_account_details_service(call):
        _LOGGER.debug("Dịch vụ async_get_account_details được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            own_id = call.data["own_id"]
            resp = await hass.async_add_executor_job(
                lambda: session.get(f"{zalo_server}/api/accounts/{own_id}")
            )
            _LOGGER.info("Phản hồi lấy chi tiết tài khoản: %s", resp.text)
            await show_result_notification(hass, "lấy chi tiết tài khoản", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_account_details: %s", e)
            await show_result_notification(hass, "lấy chi tiết tài khoản", None, error=e)

    # Đăng ký service lấy chi tiết tài khoản Zalo (giới hạn 120 ký tự)
    hass.services.async_register(
        DOMAIN, "get_account_details", async_get_account_details_service,
        schema=SERVICE_GET_ACCOUNT_DETAILS_SCHEMA
    )

    async def async_find_user_service(call):
        _LOGGER.debug("Dịch vụ async_find_user được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "phone": call.data["phone"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/findUserByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tìm người dùng: %s", resp.text)
            await show_result_notification(hass, "tìm người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_find_user: %s", e)
            await show_result_notification(hass, "tìm người dùng", None, error=e)

    hass.services.async_register(DOMAIN, "find_user", async_find_user_service, schema=SERVICE_FIND_USER_SCHEMA)

    async def async_get_user_info_service(call):
        _LOGGER.debug("Dịch vụ async_get_user_info được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "userId": call.data["user_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getUserInfoByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy thông tin người dùng: %s", resp.text)
            await show_result_notification(hass, "lấy thông tin người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_user_info: %s", e)
            await show_result_notification(
                hass,
                "lấy thông tin người dùng",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "get_user_info",
        async_get_user_info_service,
        schema=SERVICE_GET_USER_INFO_SCHEMA
    )

    async def async_send_friend_request_service(call):
        _LOGGER.debug("Dịch vụ async_send_friend_request được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "userId": call.data["user_id"],
                "message": call.data["message"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendFriendRequestByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi lời mời kết bạn: %s", resp.text)
            await show_result_notification(hass, "gửi lời mời kết bạn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_friend_request: %s", e)
            await show_result_notification(
                hass,
                "gửi lời mời kết bạn",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "send_friend_request",
        async_send_friend_request_service,
        schema=SERVICE_SEND_FRIEND_REQUEST_SCHEMA
    )

    async def async_create_group_service(call):
        _LOGGER.debug("Dịch vụ async_create_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            members_list = call.data["members"].split(",") if call.data["members"] else []
            payload = {
                "members": members_list,
                "name": call.data.get("name"),
                "avatarPath": call.data.get("avatar_path"),
                "accountSelection": call.data[
                    "account_selection"
                ]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/createGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tạo nhóm: %s", resp.text)
            await show_result_notification(hass, "tạo nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_create_group: %s", e)
            await show_result_notification(hass, "tạo nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "create_group", async_create_group_service, schema=SERVICE_CREATE_GROUP_SCHEMA)

    async def async_get_group_info_service(call):
        _LOGGER.debug("Dịch vụ async_get_group_info được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            group_id = call.data.get("group_id", "")
            account_selection = call.data.get("account_selection", "") or "default"  # Logic mặc định
            group_id_list = (
                group_id.split(",") if group_id else []
            )
            payload = {
                "groupId": group_id_list,
                "accountSelection": account_selection
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getGroupInfoByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy thông tin nhóm: %s", resp.text)
            await show_result_notification(hass, "lấy thông tin nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_group_info: %s", e)
            await show_result_notification(
                hass,
                "lấy thông tin nhóm",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "get_group_info",
        async_get_group_info_service,
        schema=SERVICE_GET_GROUP_INFO_SCHEMA
    )

    async def async_add_user_to_group_service(call):
        _LOGGER.debug("Dịch vụ async_add_user_to_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            member_id_list = (
                call.data["member_id"].split(",")
                if "," in call.data["member_id"]
                else [call.data["member_id"]]
            )
            payload = {
                "groupId": call.data["group_id"],
                "memberId": member_id_list,
                "accountSelection": call.data[
                    "account_selection"
                ]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/addUserToGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi thêm người dùng vào nhóm: %s", resp.text)
            await show_result_notification(hass, "thêm người dùng vào nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_user_to_group: %s", e)
            await show_result_notification(
                hass,
                "thêm người dùng vào nhóm",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "add_user_to_group",
        async_add_user_to_group_service,
        schema=SERVICE_ADD_USER_TO_GROUP_SCHEMA
    )

    async def async_remove_user_from_group_service(call):
        _LOGGER.debug("Dịch vụ async_remove_user_from_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            # Xử lý member_id_list: luôn trả về list, kể cả khi chỉ có 1 ID
            member_id_list = (
                call.data["member_id"].split(",")
                if "," in call.data["member_id"]
                else [call.data["member_id"]]
            )
            payload = {
                "groupId": call.data["group_id"],
                "memberId": member_id_list,
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeUserFromGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi xóa người dùng khỏi nhóm: %s", resp.text)
            await show_result_notification(hass, "xóa người dùng khỏi nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_user_from_group: %s", e)
            await show_result_notification(
                hass,
                "xóa người dùng khỏi nhóm",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "remove_user_from_group",
        async_remove_user_from_group_service,
        schema=SERVICE_REMOVE_USER_FROM_GROUP_SCHEMA
    )

    async def async_send_image_to_user_service(call):
        _LOGGER.debug("Dịch vụ async_send_image_to_user được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            image_path = call.data["image_path"]

            if image_path.startswith("http"):
                public_url = image_path
            else:
                # Kiểm tra tệp tồn tại
                if not os.path.isfile(image_path):
                    error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                    await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                    return

                # Thử copy vào thư mục public (phương pháp cũ) hoặc sử dụng máy chủ tạm thời
                try:
                    # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
                    is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

                    if is_local_server:
                        # Sử dụng phương pháp cũ khi server chạy cùng máy
                        public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                        if not public_url:
                            error_msg = "Không thể copy ảnh đến thư mục public"
                            await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                            return

                        if public_url.startswith("/local/"):
                            public_url = f"{zalo_server}{public_url.replace('/local', '')}"
                    else:
                        # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                        )
                except Exception as e:
                    error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                    _LOGGER.error(error_msg)
                    await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=error_msg)
                    return

            payload = {
                "imagePath": public_url,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImageToUserByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi ảnh cho người dùng: %s", resp.text)
            await show_result_notification(hass, "gửi ảnh cho người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_image_to_user: %s", e)
            # Hiển thị thông báo kết quả gửi ảnh cho người dùng khi gặp lỗi
            await show_result_notification(hass, "gửi ảnh cho người dùng", None, error=str(e))

    hass.services.async_register(
        DOMAIN,
        "send_image_to_user",
        async_send_image_to_user_service,
        schema=SERVICE_SEND_IMAGE_TO_USER_SCHEMA
    )

    async def async_send_image_to_group_service(call):
        _LOGGER.debug("Dịch vụ async_send_image_to_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            image_path = call.data["image_path"]

            if image_path.startswith("http"):
                public_url = image_path
            else:
                # Kiểm tra tệp tồn tại
                if not os.path.isfile(image_path):
                    error_msg = f"Không tìm thấy tệp ảnh: {image_path}"
                    await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                    return

                # Thử copy vào thư mục public (phương pháp cũ) hoặc sử dụng máy chủ tạm thời
                try:
                    # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
                    is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

                    if is_local_server:
                        # Sử dụng phương pháp cũ khi server chạy cùng máy
                        public_url = await hass.async_add_executor_job(copy_to_public, image_path, zalo_server)
                        if not public_url:
                            error_msg = "Không thể copy ảnh đến thư mục public"
                            await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                            return

                        if public_url.startswith("/local/"):
                            public_url = f"{zalo_server}{public_url.replace('/local', '')}"
                    else:
                        # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                        _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {image_path}")
                        public_url = await hass.async_add_executor_job(
                            serve_file_temporarily, image_path, 90  # 90 giây là đủ để gửi
                        )
                except Exception as e:
                    error_msg = f"Lỗi khi xử lý ảnh: {str(e)}"
                    _LOGGER.error(error_msg)
                    await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=error_msg)
                    return

            payload = {
                "imagePath": public_url,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImageToGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi ảnh cho nhóm: %s", resp.text)
            await show_result_notification(hass, "gửi ảnh cho nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_image_to_group: %s", e)
            # Hiển thị thông báo kết quả khi có lỗi trong quá trình gửi ảnh cho nhóm
            await show_result_notification(hass, "gửi ảnh cho nhóm", None, error=str(e))

    hass.services.async_register(
        DOMAIN,
        "send_image_to_group",
        async_send_image_to_group_service,
        schema=SERVICE_SEND_IMAGE_TO_GROUP_SCHEMA
    )

    async def async_send_images_to_user_service(call):
        _LOGGER.debug("Dịch vụ async_send_images_to_user được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            image_paths = call.data["image_paths"].split(",")
            processed_paths = []

            # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
            is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

            for img in image_paths:
                img = img.strip()
                if img.startswith("http"):
                    # Đối với URL trực tiếp, thêm trực tiếp vào danh sách
                    processed_paths.append(img)
                else:
                    # Kiểm tra tệp tồn tại
                    if not os.path.isfile(img):
                        _LOGGER.warning(f"Không tìm thấy tệp ảnh: {img}, bỏ qua")
                        continue

                    try:
                        if is_local_server:
                            # Sử dụng phương pháp cũ khi server chạy cùng máy
                            public_url = await hass.async_add_executor_job(copy_to_public, img, zalo_server)
                            if public_url:
                                if public_url.startswith("/local/"):
                                    fixed_url = f"{zalo_server}{public_url.replace('/local', '')}"
                                    processed_paths.append(fixed_url)
                            else:
                                _LOGGER.warning(f"Không thể copy ảnh: {img}, bỏ qua")
                        else:
                            # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                            _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {img}")
                            public_url = await hass.async_add_executor_job(
                                serve_file_temporarily, img, 120  # 120 giây cho nhiều ảnh
                            )
                            processed_paths.append(public_url)
                    except Exception as e:
                        _LOGGER.error(f"Lỗi khi xử lý ảnh {img}: {str(e)}")
                        continue

            if not processed_paths:
                error_msg = "Không có ảnh nào được xử lý thành công"
                await show_result_notification(hass, "gửi nhiều ảnh cho người dùng", None, error=error_msg)
                return

            payload = {
                "imagePaths": processed_paths,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImagesToUserByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi nhiều ảnh cho người dùng: %s", resp.text)
            await show_result_notification(hass, "gửi nhiều ảnh cho người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_images_to_user: %s", e)
            # Hiển thị thông báo kết quả khi có lỗi trong quá trình gửi nhiều ảnh cho người dùng
            await show_result_notification(
                hass,
                "gửi nhiều ảnh cho người dùng",
                None,
                error=str(e)
            )

    hass.services.async_register(
        DOMAIN,
        "send_images_to_user",
        async_send_images_to_user_service,
        schema=SERVICE_SEND_IMAGES_TO_USER_SCHEMA
    )

    async def async_send_images_to_group_service(call):
        _LOGGER.debug("Dịch vụ async_send_images_to_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            image_paths = call.data["image_paths"].split(",")
            processed_paths = []

            # Kiểm tra nếu zalo_server chạy trên cùng máy (localhost)
            is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)

            for img in image_paths:
                img = img.strip()
                if img.startswith("http"):
                    # Đối với URL trực tiếp, thêm trực tiếp vào danh sách
                    processed_paths.append(img)
                else:
                    # Kiểm tra tệp tồn tại
                    if not os.path.isfile(img):
                        _LOGGER.warning(f"Không tìm thấy tệp ảnh: {img}, bỏ qua")
                        continue

                    try:
                        if is_local_server:
                            # Sử dụng phương pháp cũ khi server chạy cùng máy
                            public_url = await hass.async_add_executor_job(copy_to_public, img, zalo_server)
                            if public_url:
                                if public_url.startswith("/local/"):
                                    fixed_url = f"{zalo_server}{public_url.replace('/local', '')}"
                                    processed_paths.append(fixed_url)
                            else:
                                _LOGGER.warning(f"Không thể copy ảnh: {img}, bỏ qua")
                        else:
                            # Sử dụng máy chủ HTTP tạm thời khi server chạy trên máy khác
                            _LOGGER.info(f"Sử dụng máy chủ HTTP tạm thời để phục vụ ảnh: {img}")
                            public_url = await hass.async_add_executor_job(
                                serve_file_temporarily, img, 120  # 120 giây cho nhiều ảnh
                            )
                            processed_paths.append(public_url)
                    except Exception as e:
                        _LOGGER.error(f"Lỗi khi xử lý ảnh {img}: {str(e)}")
                        continue

            if not processed_paths:
                error_msg = "Không có ảnh nào được xử lý thành công"
                await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", None, error=error_msg)
                return

            payload = {
                "imagePaths": processed_paths,
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendImagesToGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi nhiều ảnh cho nhóm: %s", resp.text)
            await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_images_to_group: %s", e)
            # Hiển thị thông báo kết quả khi gửi nhiều ảnh cho nhóm thất bại
            await show_result_notification(hass, "gửi nhiều ảnh cho nhóm", None, error=str(e))

    hass.services.async_register(
        DOMAIN,
        "send_images_to_group",
        async_send_images_to_group_service,
        schema=SERVICE_SEND_IMAGES_TO_GROUP_SCHEMA
    )

    async def async_get_account_webhooks_service(call):
        _LOGGER.debug("Dịch vụ async_get_account_webhooks được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            resp = await hass.async_add_executor_job(
                lambda: session.get(f"{zalo_server}/api/account-webhooks")
            )
            _LOGGER.info("Phản hồi lấy danh sách webhook: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách webhook", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_account_webhooks: %s", e)
            # Hiển thị thông báo kết quả khi lấy danh sách webhook thất bại
            await show_result_notification(hass, "lấy danh sách webhook", None, error=str(e))

    hass.services.async_register(
        DOMAIN,
        "get_account_webhooks",
        async_get_account_webhooks_service,
        schema=SERVICE_GET_ACCOUNT_WEBHOOKS_SCHEMA
    )

    async def async_get_account_webhook_service(call):
        _LOGGER.debug("Dịch vụ async_get_account_webhook được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            own_id = call.data["own_id"]
            resp = await hass.async_add_executor_job(
                lambda: session.get(f"{zalo_server}/api/account-webhook/{own_id}")
            )
            _LOGGER.info("Phản hồi lấy thông tin webhook: %s", resp.text)
            await show_result_notification(hass, "lấy thông tin webhook", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_account_webhook: %s", e)
            await show_result_notification(
                hass,
                "lấy thông tin webhook",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "get_account_webhook",
        async_get_account_webhook_service,
        schema=SERVICE_GET_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def async_set_account_webhook_service(call):
        _LOGGER.debug("Dịch vụ async_set_account_webhook được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "ownId": call.data["own_id"],
                "messageWebhookUrl": call.data.get("message_webhook_url"),
                "groupEventWebhookUrl": call.data.get("group_event_webhook_url"),
                "reactionWebhookUrl": call.data.get("reaction_webhook_url")
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/account-webhook", json=payload)
            )
            _LOGGER.info("Phản hồi cài đặt webhook: %s", resp.text)
            await show_result_notification(hass, "cài đặt webhook", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_set_account_webhook: %s", e)
            await show_result_notification(
                hass,
                "cài đặt webhook",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "set_account_webhook",
        async_set_account_webhook_service,
        schema=SERVICE_SET_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def async_delete_account_webhook_service(call):
        _LOGGER.debug("Dịch vụ async_delete_account_webhook được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            own_id = call.data["own_id"]
            resp = await hass.async_add_executor_job(
                lambda: session.delete(f"{zalo_server}/api/account-webhook/{own_id}")
            )
            _LOGGER.info("Phản hồi xóa webhook: %s", resp.text)
            await show_result_notification(hass, "xóa webhook", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_delete_account_webhook: %s", e)
            await show_result_notification(
                hass,
                "xóa webhook",
                None,
                error=e
            )

    hass.services.async_register(
        DOMAIN,
        "delete_account_webhook",
        async_delete_account_webhook_service,
        schema=SERVICE_DELETE_ACCOUNT_WEBHOOK_SCHEMA
    )

    async def async_get_proxies_service(call):
        _LOGGER.debug("Dịch vụ async_get_proxies được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            resp = await hass.async_add_executor_job(
                lambda: session.get(f"{zalo_server}/api/proxies")
            )
            _LOGGER.info("Phản hồi lấy danh sách proxy: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách proxy", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_proxies: %s", e)
            await show_result_notification(hass, "lấy danh sách proxy", None, error=e)

    hass.services.async_register(DOMAIN, "get_proxies", async_get_proxies_service, schema=SERVICE_GET_PROXIES_SCHEMA)

    async def async_add_proxy_service(call):
        _LOGGER.debug("Dịch vụ async_add_proxy được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "proxyUrl": call.data["proxy_url"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/proxies", json=payload)
            )
            _LOGGER.info("Phản hồi thêm proxy: %s", resp.text)
            await show_result_notification(hass, "thêm proxy", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_proxy: %s", e)
            await show_result_notification(hass, "thêm proxy", None, error=e)

    hass.services.async_register(DOMAIN, "add_proxy", async_add_proxy_service, schema=SERVICE_ADD_PROXY_SCHEMA)

    async def async_remove_proxy_service(call):
        _LOGGER.debug("Dịch vụ async_remove_proxy được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "proxyUrl": call.data["proxy_url"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.delete(f"{zalo_server}/api/proxies", json=payload)
            )
            _LOGGER.info("Phản hồi xóa proxy: %s", resp.text)
            await show_result_notification(hass, "xóa proxy", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_proxy: %s", e)
            await show_result_notification(hass, "xóa proxy", None, error=e)

    hass.services.async_register(DOMAIN, "remove_proxy", async_remove_proxy_service, schema=SERVICE_REMOVE_PROXY_SCHEMA)

    # Thêm triển khai đầy đủ cho các service mới
    async def async_accept_friend_request_service(call):
        _LOGGER.debug("Dịch vụ async_accept_friend_request được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "userId": call.data["user_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/acceptFriendRequestByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi chấp nhận lời mời kết bạn: %s", resp.text)
            await show_result_notification(hass, "chấp nhận lời mời kết bạn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_accept_friend_request: %s", e)
            await show_result_notification(hass, "chấp nhận lời mời kết bạn", None, error=e)

    # Đăng ký service accept_friend_request, đảm bảo không quá 120 ký tự/dòng
    hass.services.async_register(
        DOMAIN, "accept_friend_request",
        async_accept_friend_request_service,
        schema=SERVICE_ACCEPT_FRIEND_REQUEST_SCHEMA
    )

    async def async_block_user_service(call):
        _LOGGER.debug("Dịch vụ async_block_user được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "userId": call.data["user_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/blockUserByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi chặn người dùng: %s", resp.text)
            await show_result_notification(hass, "chặn người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_block_user: %s", e)
            await show_result_notification(hass, "chặn người dùng", None, error=e)

    hass.services.async_register(DOMAIN, "block_user", async_block_user_service, schema=SERVICE_BLOCK_USER_SCHEMA)

    async def async_unblock_user_service(call):
        _LOGGER.debug("Dịch vụ async_unblock_user được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "userId": call.data["user_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/unblockUserByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi bỏ chặn người dùng: %s", resp.text)
            await show_result_notification(hass, "bỏ chặn người dùng", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_unblock_user: %s", e)
            await show_result_notification(hass, "bỏ chặn người dùng", None, error=e)

    hass.services.async_register(DOMAIN, "unblock_user", async_unblock_user_service, schema=SERVICE_UNBLOCK_USER_SCHEMA)

    async def async_send_sticker_service(call):
        _LOGGER.debug("Dịch vụ async_send_sticker được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")

            # Tạo đối tượng sticker đúng định dạng
            sticker_id = int(call.data["sticker_id"])
            sticker = {
                "id": sticker_id,
                "cateId": 526,  # Giá trị mặc định
                "type": 1       # Giá trị mặc định
            }

            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"],
                "sticker": sticker,
                "type": 1 if msg_type == "1" else 0
            }

            _LOGGER.debug("Gửi payload đến sendStickerByAccount: %s", payload)

            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendStickerByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi sticker: %s", resp.text)
            await show_result_notification(hass, "gửi sticker", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_sticker: %s", e)
            await show_result_notification(hass, "gửi sticker", None, error=e)

    hass.services.async_register(DOMAIN, "send_sticker", async_send_sticker_service, schema=SERVICE_SEND_STICKER_SCHEMA)

    async def async_undo_message_service(call):
        _LOGGER.debug("Dịch vụ async_undo_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            msg_type = call.data.get("type", "0")
            payload = {
                "msgId": call.data["msg_id"],
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": 1 if msg_type == "1" else 0
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/undoMessageByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi hủy tin nhắn: %s", resp.text)
            await show_result_notification(hass, "hủy tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_undo_message: %s", e)
            await show_result_notification(hass, "hủy tin nhắn", None, error=e)

    hass.services.async_register(DOMAIN, "undo_message", async_undo_message_service, schema=SERVICE_UNDO_MESSAGE_SCHEMA)

    async def async_create_reminder_service(call):
        _LOGGER.debug("Dịch vụ async_create_reminder được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": call.data.get("type", "0"),
                "options": {
                    "title": call.data["title"],
                    "content": call.data["content"],
                    "remindTime": call.data["remind_time"]
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/createReminderByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tạo lời nhắc: %s", resp.text)
            await show_result_notification(hass, "tạo lời nhắc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_create_reminder: %s", e)
            await show_result_notification(hass, "tạo lời nhắc", None, error=e)

    hass.services.async_register(DOMAIN, "create_reminder", async_create_reminder_service,
                                 schema=SERVICE_CREATE_REMINDER_SCHEMA)

    async def async_remove_reminder_service(call):
        _LOGGER.debug("Dịch vụ async_remove_reminder được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "reminderId": call.data["reminder_id"],
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "type": call.data.get("type", "0")
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeReminderByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi xóa lời nhắc: %s", resp.text)
            await show_result_notification(hass, "xóa lời nhắc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_reminder: %s", e)
            await show_result_notification(hass, "xóa lời nhắc", None, error=e)

    hass.services.async_register(DOMAIN, "remove_reminder", async_remove_reminder_service,
                                 schema=SERVICE_REMOVE_REMINDER_SCHEMA)

    async def async_change_group_name_service(call):
        _LOGGER.debug("Dịch vụ async_change_group_name được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "groupId": call.data["group_id"],
                "name": call.data["name"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/changeGroupNameByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi đổi tên nhóm: %s", resp.text)
            await show_result_notification(hass, "đổi tên nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_change_group_name: %s", e)
            await show_result_notification(hass, "đổi tên nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "change_group_name", async_change_group_name_service,
                                 schema=SERVICE_CHANGE_GROUP_NAME_SCHEMA)

    async def async_change_group_avatar_service(call):
        _LOGGER.debug("Dịch vụ async_change_group_avatar được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "groupId": call.data["group_id"],
                "imagePath": call.data["image_path"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/changeGroupAvatarByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi đổi ảnh đại diện nhóm: %s", resp.text)
            await show_result_notification(hass, "đổi ảnh đại diện nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_change_group_avatar: %s", e)
            await show_result_notification(hass, "đổi ảnh đại diện nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "change_group_avatar", async_change_group_avatar_service,
                                 schema=SERVICE_CHANGE_GROUP_AVATAR_SCHEMA)

    async def async_send_voice_service(call):
        _LOGGER.debug("Dịch vụ async_send_voice được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Nếu là đường dẫn cục bộ, tạo URL tạm thời
            voice_path = call.data["voice_path"]
            voice_url = voice_path
            local_server = None

            if not voice_path.startswith(("http://", "https://")):
                if os.path.isfile(voice_path):
                    voice_url, local_server = await hass.async_add_executor_job(
                        serve_file_temporarily, voice_path
                    )
                else:
                    raise Exception(f"Không tìm thấy file âm thanh: {voice_path}")

            try:
                payload = {
                    "threadId": call.data["thread_id"],
                    "accountSelection": call.data["account_selection"],
                    "options": {
                        "voiceUrl": voice_url
                    }
                }
                resp = await hass.async_add_executor_job(
                    lambda: session.post(f"{zalo_server}/api/sendVoiceByAccount", json=payload)
                )
                _LOGGER.info("Phản hồi gửi tin nhắn thoại: %s", resp.text)
                await show_result_notification(hass, "gửi tin nhắn thoại", resp)
            finally:
                # Đảm bảo luôn đóng server nếu đã tạo
                if local_server:
                    local_server.shutdown()
                    local_server.server_close()
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_voice: %s", e)
            await show_result_notification(hass, "gửi tin nhắn thoại", None, error=e)

    hass.services.async_register(DOMAIN, "send_voice", async_send_voice_service,
                                 schema=SERVICE_SEND_VOICE_SCHEMA)

    # Đăng ký các service mới
    async def async_get_all_friends_service(call):
        _LOGGER.debug("Dịch vụ async_get_all_friends được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getAllFriendsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách bạn bè: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách bạn bè", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_all_friends: %s", e)
            await show_result_notification(hass, "lấy danh sách bạn bè", None, error=e)

    hass.services.async_register(DOMAIN, "get_all_friends", async_get_all_friends_service,
                                 schema=SERVICE_GET_ALL_FRIENDS_SCHEMA)

    async def async_get_received_friend_requests_service(call):
        _LOGGER.debug("Dịch vụ async_get_received_friend_requests được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getReceivedFriendRequestsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy lời mời kết bạn đã nhận: %s", resp.text)
            await show_result_notification(hass, "lấy lời mời kết bạn đã nhận", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_received_friend_requests: %s", e)
            await show_result_notification(hass, "lấy lời mời kết bạn đã nhận", None, error=e)

    hass.services.async_register(DOMAIN, "get_received_friend_requests",
                                 async_get_received_friend_requests_service,
                                 schema=SERVICE_GET_RECEIVED_FRIEND_REQUESTS_SCHEMA)

    async def async_get_sent_friend_requests_service(call):
        _LOGGER.debug("Dịch vụ async_get_sent_friend_requests được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getSentFriendRequestByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy lời mời kết bạn đã gửi: %s", resp.text)
            await show_result_notification(hass, "lấy lời mời kết bạn đã gửi", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_sent_friend_requests: %s", e)
            await show_result_notification(hass, "lấy lời mời kết bạn đã gửi", None, error=e)

    hass.services.async_register(DOMAIN, "get_sent_friend_requests",
                                 async_get_sent_friend_requests_service,
                                 schema=SERVICE_GET_SENT_FRIEND_REQUESTS_SCHEMA)

    async def async_undo_friend_request_service(call):
        _LOGGER.debug("Dịch vụ async_undo_friend_request được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "friendId": call.data["friend_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/undoFriendRequestByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi thu hồi lời mời kết bạn: %s", resp.text)
            await show_result_notification(hass, "thu hồi lời mời kết bạn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_undo_friend_request: %s", e)
            await show_result_notification(hass, "thu hồi lời mời kết bạn", None, error=e)

    hass.services.async_register(DOMAIN, "undo_friend_request",
                                 async_undo_friend_request_service,
                                 schema=SERVICE_UNDO_FRIEND_REQUEST_SCHEMA)

    async def async_remove_friend_service(call):
        _LOGGER.debug("Dịch vụ async_remove_friend được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "friendId": call.data["friend_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeFriendByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi hủy kết bạn: %s", resp.text)
            await show_result_notification(hass, "hủy kết bạn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_friend: %s", e)
            await show_result_notification(hass, "hủy kết bạn", None, error=e)

    hass.services.async_register(DOMAIN, "remove_friend", async_remove_friend_service,
                                 schema=SERVICE_REMOVE_FRIEND_SCHEMA)

    async def async_change_friend_alias_service(call):
        _LOGGER.debug("Dịch vụ async_change_friend_alias được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "friendId": call.data["friend_id"],
                "alias": call.data["alias"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/changeFriendAliasByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi đổi biệt danh bạn bè: %s", resp.text)
            await show_result_notification(hass, "đổi biệt danh bạn bè", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_change_friend_alias: %s", e)
            await show_result_notification(hass, "đổi biệt danh bạn bè", None, error=e)

    hass.services.async_register(DOMAIN, "change_friend_alias",
                                 async_change_friend_alias_service,
                                 schema=SERVICE_CHANGE_FRIEND_ALIAS_SCHEMA)

    async def async_remove_friend_alias_service(call):
        _LOGGER.debug("Dịch vụ async_remove_friend_alias được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "friendId": call.data["friend_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeFriendAliasByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi xóa biệt danh bạn bè: %s", resp.text)
            await show_result_notification(hass, "xóa biệt danh bạn bè", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_friend_alias: %s", e)
            await show_result_notification(hass, "xóa biệt danh bạn bè", None, error=e)

    hass.services.async_register(DOMAIN, "remove_friend_alias",
                                 async_remove_friend_alias_service,
                                 schema=SERVICE_REMOVE_FRIEND_ALIAS_SCHEMA)

    async def async_get_all_groups_service(call):
        _LOGGER.debug("Dịch vụ async_get_all_groups được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getAllGroupsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách nhóm: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_all_groups: %s", e)
            await show_result_notification(hass, "lấy danh sách nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "get_all_groups", async_get_all_groups_service,
                                 schema=SERVICE_GET_ALL_GROUPS_SCHEMA)

    async def async_add_group_deputy_service(call):
        _LOGGER.debug("Dịch vụ async_add_group_deputy được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"],
                "memberId": call.data["member_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/addGroupDeputyByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi thêm phó nhóm: %s", resp.text)
            await show_result_notification(hass, "thêm phó nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_group_deputy: %s", e)
            await show_result_notification(hass, "thêm phó nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "add_group_deputy", async_add_group_deputy_service,
                                 schema=SERVICE_ADD_GROUP_DEPUTY_SCHEMA)

    async def async_remove_group_deputy_service(call):
        _LOGGER.debug("Dịch vụ async_remove_group_deputy được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"],
                "memberId": call.data["member_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeGroupDeputyByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi xóa phó nhóm: %s", resp.text)
            await show_result_notification(hass, "xóa phó nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_group_deputy: %s", e)
            await show_result_notification(hass, "xóa phó nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "remove_group_deputy",
                                 async_remove_group_deputy_service,
                                 schema=SERVICE_REMOVE_GROUP_DEPUTY_SCHEMA)

    async def async_change_group_owner_service(call):
        _LOGGER.debug("Dịch vụ async_change_group_owner được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"],
                "memberId": call.data["member_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/changeGroupOwnerByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi chuyển quyền sở hữu nhóm: %s", resp.text)
            await show_result_notification(hass, "chuyển quyền sở hữu nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_change_group_owner: %s", e)
            await show_result_notification(hass, "chuyển quyền sở hữu nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "change_group_owner",
                                 async_change_group_owner_service,
                                 schema=SERVICE_CHANGE_GROUP_OWNER_SCHEMA)

    async def async_disperse_group_service(call):
        _LOGGER.debug("Dịch vụ async_disperse_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/disperseGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi giải tán nhóm: %s", resp.text)
            await show_result_notification(hass, "giải tán nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_disperse_group: %s", e)
            await show_result_notification(hass, "giải tán nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "disperse_group", async_disperse_group_service,
                                 schema=SERVICE_DISPERSE_GROUP_SCHEMA)

    async def async_enable_group_link_service(call):
        _LOGGER.debug("Dịch vụ async_enable_group_link được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/enableGroupLinkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi kích hoạt link nhóm: %s", resp.text)
            await show_result_notification(hass, "kích hoạt link nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_enable_group_link: %s", e)
            await show_result_notification(hass, "kích hoạt link nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "enable_group_link",
                                 async_enable_group_link_service,
                                 schema=SERVICE_ENABLE_GROUP_LINK_SCHEMA)

    async def async_disable_group_link_service(call):
        _LOGGER.debug("Dịch vụ async_disable_group_link được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/disableGroupLinkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi vô hiệu hóa link nhóm: %s", resp.text)
            await show_result_notification(hass, "vô hiệu hóa link nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_disable_group_link: %s", e)
            await show_result_notification(hass, "vô hiệu hóa link nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "disable_group_link",
                                 async_disable_group_link_service,
                                 schema=SERVICE_DISABLE_GROUP_LINK_SCHEMA)

    async def async_join_group_service(call):
        _LOGGER.debug("Dịch vụ async_join_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "link": call.data["link"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/joinGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tham gia nhóm: %s", resp.text)
            await show_result_notification(hass, "tham gia nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_join_group: %s", e)
            await show_result_notification(hass, "tham gia nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "join_group", async_join_group_service,
                                 schema=SERVICE_JOIN_GROUP_SCHEMA)

    async def async_leave_group_service(call):
        _LOGGER.debug("Dịch vụ async_leave_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"],
                "silent": call.data.get("silent", False)
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/leaveGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi rời nhóm: %s", resp.text)
            await show_result_notification(hass, "rời nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_leave_group: %s", e)
            await show_result_notification(hass, "rời nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "leave_group", async_leave_group_service,
                                 schema=SERVICE_LEAVE_GROUP_SCHEMA)

    async def async_update_profile_service(call):
        _LOGGER.debug("Dịch vụ async_update_profile được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }

            if "name" in call.data:
                payload["name"] = call.data["name"]
            if "dob" in call.data:
                payload["dob"] = call.data["dob"]
            if "gender" in call.data:
                payload["gender"] = int(call.data["gender"])

            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/updateProfileByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi cập nhật thông tin cá nhân: %s", resp.text)
            await show_result_notification(hass, "cập nhật thông tin cá nhân", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_update_profile: %s", e)
            await show_result_notification(hass, "cập nhật thông tin cá nhân", None, error=e)

    hass.services.async_register(DOMAIN, "update_profile", async_update_profile_service,
                                 schema=SERVICE_UPDATE_PROFILE_SCHEMA)

    async def async_update_settings_service(call):
        _LOGGER.debug("Dịch vụ async_update_settings được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "type": call.data["setting_type"],
                "status": int(call.data["status"])
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/updateSettingsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi cập nhật cài đặt: %s", resp.text)
            await show_result_notification(hass, "cập nhật cài đặt", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_update_settings: %s", e)
            await show_result_notification(hass, "cập nhật cài đặt", None, error=e)

    hass.services.async_register(DOMAIN, "update_settings", async_update_settings_service,
                                 schema=SERVICE_UPDATE_SETTINGS_SCHEMA)

    async def async_set_mute_service(call):
        _LOGGER.debug("Dịch vụ async_set_mute được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Xác định hành động dựa trên duration
            duration = int(call.data.get("duration", 0))
            action = "mute" if duration > 0 else "unmute"

            # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
            mute_type = call.data.get("type", "0")
            mute_type_num = 1 if mute_type.lower() == "group" else 0

            payload = {
                "params": {
                    "action": action,
                    "duration": duration
                },
                "threadId": call.data["thread_id"],  # Sửa từ threadID thành threadId
                "type": mute_type_num,
                "accountSelection": call.data["account_selection"]
            }

            _LOGGER.debug("Gửi payload đến setMuteByAccount: %s", payload)
            url = f"{zalo_server}/api/setMuteByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi cài đặt tắt thông báo: %s", resp.text)
            await show_result_notification(hass, "cài đặt tắt thông báo", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_set_mute: %s", e)
            await show_result_notification(hass, "cài đặt tắt thông báo", None, error=e)

    hass.services.async_register(DOMAIN, "set_mute", async_set_mute_service,
                                 schema=SERVICE_SET_MUTE_SCHEMA)

    async def async_set_pinned_conversation_service(call):
        _LOGGER.debug("Dịch vụ async_set_pinned_conversation được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Đảm bảo pinned là giá trị boolean
            pinned_str = str(call.data.get("pinned", "true")).lower()
            pinned = pinned_str == "true" or pinned_str == "1" or pinned_str == "yes"

            # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
            conv_type = call.data.get("type", "0")
            conv_type_num = 1 if conv_type.lower() == "group" else 0

            payload = {
                "accountSelection": call.data["account_selection"],
                "pinned": pinned,
                "threadId": call.data["thread_id"],
                "type": conv_type_num
            }

            _LOGGER.debug("Gửi payload đến setPinnedConversationsByAccount: %s", payload)
            url = f"{zalo_server}/api/setPinnedConversationsByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi ghim/bỏ ghim cuộc trò chuyện: %s", resp.text)
            await show_result_notification(hass, "ghim/bỏ ghim cuộc trò chuyện", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_set_pinned_conversation: %s", e)
            await show_result_notification(hass, "ghim/bỏ ghim cuộc trò chuyện", None, error=e)

    hass.services.async_register(DOMAIN, "set_pinned_conversation",
                                 async_set_pinned_conversation_service,
                                 schema=SERVICE_SET_PINNED_CONVERSATION_SCHEMA)

    # Đăng ký các service bổ sung

    async def async_get_unread_mark_service(call):
        _LOGGER.debug("Dịch vụ async_get_unread_mark được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getUnreadMarkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách cuộc trò chuyện chưa đọc: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện chưa đọc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_unread_mark: %s", e)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện chưa đọc", None, error=e)

    hass.services.async_register(DOMAIN, "get_unread_mark", async_get_unread_mark_service,
                                 schema=SERVICE_GET_UNREAD_MARK_SCHEMA)

    async def async_add_unread_mark_service(call):
        _LOGGER.debug("Dịch vụ async_add_unread_mark được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/addUnreadMarkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi đánh dấu chưa đọc: %s", resp.text)
            await show_result_notification(hass, "đánh dấu chưa đọc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_unread_mark: %s", e)
            await show_result_notification(hass, "đánh dấu chưa đọc", None, error=e)

    hass.services.async_register(DOMAIN, "add_unread_mark", async_add_unread_mark_service,
                                 schema=SERVICE_ADD_UNREAD_MARK_SCHEMA)

    async def async_remove_unread_mark_service(call):
        _LOGGER.debug("Dịch vụ async_remove_unread_mark được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/removeUnreadMarkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi bỏ đánh dấu chưa đọc: %s", resp.text)
            await show_result_notification(hass, "bỏ đánh dấu chưa đọc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_unread_mark: %s", e)
            await show_result_notification(hass, "bỏ đánh dấu chưa đọc", None, error=e)

    hass.services.async_register(DOMAIN, "remove_unread_mark", async_remove_unread_mark_service,
                                 schema=SERVICE_REMOVE_UNREAD_MARK_SCHEMA)

    async def async_delete_chat_service(call):
        _LOGGER.debug("Dịch vụ async_delete_chat được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/deleteChatByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi xóa cuộc trò chuyện: %s", resp.text)
            await show_result_notification(hass, "xóa cuộc trò chuyện", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_delete_chat: %s", e)
            await show_result_notification(hass, "xóa cuộc trò chuyện", None, error=e)

    hass.services.async_register(DOMAIN, "delete_chat", async_delete_chat_service,
                                 schema=SERVICE_DELETE_CHAT_SCHEMA)

    async def async_get_archived_chat_list_service(call):
        _LOGGER.debug("Dịch vụ async_get_archived_chat_list được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getArchivedChatListByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách cuộc trò chuyện lưu trữ: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện lưu trữ", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_archived_chat_list: %s", e)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện lưu trữ", None, error=e)

    hass.services.async_register(DOMAIN, "get_archived_chat_list", async_get_archived_chat_list_service,
                                 schema=SERVICE_GET_ARCHIVED_CHAT_LIST_SCHEMA)

    async def async_get_auto_delete_chat_service(call):
        _LOGGER.debug("Dịch vụ async_get_auto_delete_chat được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getAutoDeleteChatByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách tự động xóa tin nhắn: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách tự động xóa tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_auto_delete_chat: %s", e)
            await show_result_notification(hass, "lấy danh sách tự động xóa tin nhắn", None, error=e)

    hass.services.async_register(DOMAIN, "get_auto_delete_chat", async_get_auto_delete_chat_service,
                                 schema=SERVICE_GET_AUTO_DELETE_CHAT_SCHEMA)

    async def async_update_auto_delete_chat_service(call):
        _LOGGER.debug("Dịch vụ async_update_auto_delete_chat được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"],
                "ttl": int(call.data["ttl"])
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/updateAutoDeleteChatByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi cập nhật tự động xóa tin nhắn: %s", resp.text)
            await show_result_notification(hass, "cập nhật tự động xóa tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_update_auto_delete_chat: %s", e)
            await show_result_notification(hass, "cập nhật tự động xóa tin nhắn", None, error=e)

    hass.services.async_register(DOMAIN, "update_auto_delete_chat", async_update_auto_delete_chat_service,
                                 schema=SERVICE_UPDATE_AUTO_DELETE_CHAT_SCHEMA)

    async def async_get_hidden_conversations_service(call):
        _LOGGER.debug("Dịch vụ async_get_hidden_conversations được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getHiddenConversationsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách cuộc trò chuyện ẩn: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện ẩn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_hidden_conversations: %s", e)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện ẩn", None, error=e)

    hass.services.async_register(DOMAIN, "get_hidden_conversations", async_get_hidden_conversations_service,
                                 schema=SERVICE_GET_HIDDEN_CONVERSATIONS_SCHEMA)

    async def async_set_hidden_conversations_service(call):
        _LOGGER.debug("Dịch vụ async_set_hidden_conversations được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"],
                "hidden": call.data["hidden"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/setHiddenConversationsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi ẩn/hiện cuộc trò chuyện: %s", resp.text)
            await show_result_notification(hass, "ẩn/hiện cuộc trò chuyện", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_set_hidden_conversations: %s", e)
            await show_result_notification(hass, "ẩn/hiện cuộc trò chuyện", None, error=e)

    hass.services.async_register(DOMAIN, "set_hidden_conversations", async_set_hidden_conversations_service,
                                 schema=SERVICE_SET_HIDDEN_CONVERSATIONS_SCHEMA)

    async def async_update_hidden_convers_pin_service(call):
        _LOGGER.debug("Dịch vụ async_update_hidden_convers_pin được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "pin": call.data["pin"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/updateHiddenConversPinByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi cập nhật PIN cho cuộc trò chuyện ẩn: %s", resp.text)
            await show_result_notification(hass, "cập nhật PIN cho cuộc trò chuyện ẩn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_update_hidden_convers_pin: %s", e)
            await show_result_notification(hass, "cập nhật PIN cho cuộc trò chuyện ẩn", None, error=e)

    hass.services.async_register(DOMAIN, "update_hidden_convers_pin", async_update_hidden_convers_pin_service,
                                 schema=SERVICE_UPDATE_HIDDEN_CONVERS_PIN_SCHEMA)

    async def async_reset_hidden_convers_pin_service(call):
        _LOGGER.debug("Dịch vụ async_reset_hidden_convers_pin được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/resetHiddenConversPinByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi đặt lại PIN cho cuộc trò chuyện ẩn: %s", resp.text)
            await show_result_notification(hass, "đặt lại PIN cho cuộc trò chuyện ẩn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_reset_hidden_convers_pin: %s", e)
            await show_result_notification(hass, "đặt lại PIN cho cuộc trò chuyện ẩn", None, error=e)

    hass.services.async_register(DOMAIN, "reset_hidden_convers_pin", async_reset_hidden_convers_pin_service,
                                 schema=SERVICE_RESET_HIDDEN_CONVERS_PIN_SCHEMA)

    async def async_get_mute_service(call):
        _LOGGER.debug("Dịch vụ async_get_mute được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getMuteByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách cuộc trò chuyện tắt thông báo: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện tắt thông báo", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_mute: %s", e)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện tắt thông báo", None, error=e)

    hass.services.async_register(DOMAIN, "get_mute", async_get_mute_service,
                                 schema=SERVICE_GET_MUTE_SCHEMA)

    async def async_get_pin_conversations_service(call):
        _LOGGER.debug("Dịch vụ async_get_pin_conversations được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getPinConversationsByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách cuộc trò chuyện ghim: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện ghim", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_pin_conversations: %s", e)
            await show_result_notification(hass, "lấy danh sách cuộc trò chuyện ghim", None, error=e)

    hass.services.async_register(DOMAIN, "get_pin_conversations", async_get_pin_conversations_service,
                                 schema=SERVICE_GET_PIN_CONVERSATIONS_SCHEMA)

    async def async_add_reaction_service(call):
        _LOGGER.debug("Dịch vụ async_add_reaction được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Thử chuyển đổi msgId và cliMsgId sang kiểu số nguyên
            try:
                msg_id = int(call.data["msg_id"])
                cli_msg_id = int(call.data["cli_msg_id"])
            except ValueError:
                msg_id = call.data["msg_id"]
                cli_msg_id = call.data["cli_msg_id"]

            # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
            reaction_type = 1 if call.data["type"].lower() == "group" else 0

            # Chuyển đổi tên cảm xúc thành giá trị đúng từ enum Reactions
            reaction_icon = call.data["icon"].lower()
            reaction_map = {
                "like": "/-strong",
                "heart": "/-heart",
                "haha": ":>",
                "wow": ":o",
                "cry": ":-((",
                "angry": ":-h",
                "kiss": ":-*",
                "tears_of_joy": ":')",
                "shit": "/-shit",
                "rose": "/-rose",
                "broken_heart": "/-break",
                "dislike": "/-weak",
                "love": ";xx",
                "confused": ";-/",
                "wink": ";-)",
                "fade": "/-fade",
                "sun": "/-li",
                "birthday": "/-bd",
                "bomb": "/-bome",
                "ok": "/-ok",
                "peace": "/-v",
                "thanks": "/-thanks",
                "punch": "/-punch",
                "share": "/-share",
                "pray": "_()_",
                "no": "/-no",
                "bad": "/-bad",
                "love_you": "/-loveu",
                "sad": "--b"
            }

            # Sử dụng giá trị từ map hoặc giữ nguyên nếu không tìm thấy
            icon_value = reaction_map.get(reaction_icon, reaction_icon)

            payload = {
                "accountSelection": call.data["account_selection"],
                "icon": icon_value,
                "dest": {
                    "threadId": call.data["thread_id"],
                    "type": reaction_type,
                    "data": {
                        "msgId": msg_id,
                        "cliMsgId": cli_msg_id
                    }
                }
            }

            _LOGGER.debug("Gửi payload đến addReactionByAccount: %s", payload)
            url = f"{zalo_server}/api/addReactionByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi thêm cảm xúc: %s", resp.text)

            # Thêm log chi tiết hơn về phản hồi
            if resp.status_code != 200:
                _LOGGER.error("Lỗi HTTP khi gọi addReactionByAccount: %s - %s", resp.status_code, resp.reason)

            await show_result_notification(hass, "thêm cảm xúc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_reaction: %s", e)
            await show_result_notification(hass, "thêm cảm xúc", None, error=e)

    hass.services.async_register(DOMAIN, "add_reaction", async_add_reaction_service,
                                 schema=SERVICE_ADD_REACTION_SCHEMA)

    async def async_delete_message_service(call):
        _LOGGER.debug("Dịch vụ async_delete_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
            message_type = 1 if call.data["type"].lower() == "group" else 0

            payload = {
                "accountSelection": call.data["account_selection"],
                "dest": {
                    "threadId": call.data["thread_id"],
                    "type": message_type,
                    "data": {
                        "msgId": call.data["msg_id"],
                        "cliMsgId": call.data["cli_msg_id"],
                        "uidFrom": call.data["uid_from"]
                    }
                },
                "onlyMe": call.data.get("only_me", True)
            }

            url = f"{zalo_server}/api/deleteMessageByAccount"
            _LOGGER.debug("Gửi payload đến deleteMessageByAccount: %s", payload)
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi xóa tin nhắn: %s", resp.text)
            await show_result_notification(hass, "xóa tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_delete_message: %s", e)
            await show_result_notification(hass, "xóa tin nhắn", None, error=e)

    hass.services.async_register(DOMAIN, "delete_message", async_delete_message_service,
                                 schema=SERVICE_DELETE_MESSAGE_SCHEMA)

    async def async_forward_message_service(call):
        _LOGGER.debug("Dịch vụ async_forward_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            thread_ids = call.data["thread_ids"].split(",")
            thread_ids = [tid.strip() for tid in thread_ids]

            # Lấy type từ dữ liệu gọi hoặc mặc định là 0 (user)
            msg_type = call.data.get("type", "0")
            # Chuyển đổi type từ chuỗi sang số nếu cần
            msg_type_num = 1 if msg_type.lower() == "group" else 0

            payload = {
                "accountSelection": call.data["account_selection"],
                "params": {
                    "message": call.data["message"],
                    "threadIds": thread_ids
                },
                "type": msg_type_num
            }

            _LOGGER.debug("Gửi payload đến forwardMessageByAccount: %s", payload)
            url = f"{zalo_server}/api/forwardMessageByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi chuyển tiếp tin nhắn: %s", resp.text)
            await show_result_notification(hass, "chuyển tiếp tin nhắn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_forward_message: %s", e)
            await show_result_notification(hass, "chuyển tiếp tin nhắn", None, error=e)

    hass.services.async_register(DOMAIN, "forward_message", async_forward_message_service,
                                 schema=SERVICE_FORWARD_MESSAGE_SCHEMA)

    async def async_parse_link_service(call):
        _LOGGER.debug("Dịch vụ async_parse_link được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "link": call.data["link"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/parseLinkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi phân tích link: %s", resp.text)
            await show_result_notification(hass, "phân tích link", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_parse_link: %s", e)
            await show_result_notification(hass, "phân tích link", None, error=e)

    hass.services.async_register(DOMAIN, "parse_link", async_parse_link_service,
                                 schema=SERVICE_PARSE_LINK_SCHEMA)

    async def async_send_card_service(call):
        _LOGGER.debug("Dịch vụ async_send_card được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "userId": call.data["user_id"]
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendCardByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi danh thiếp: %s", resp.text)
            await show_result_notification(hass, "gửi danh thiếp", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_card: %s", e)
            await show_result_notification(hass, "gửi danh thiếp", None, error=e)

    hass.services.async_register(DOMAIN, "send_card", async_send_card_service,
                                 schema=SERVICE_SEND_CARD_SCHEMA)

    async def async_send_link_service(call):
        _LOGGER.debug("Dịch vụ async_send_link được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            options = {
                "link": call.data["link"],
                "msg": call.data.get("message", "")
            }

            if call.data.get("thumbnail"):
                options["thumbnail"] = call.data["thumbnail"]

            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "options": options
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendLinkByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi link: %s", resp.text)
            await show_result_notification(hass, "gửi link", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_link: %s", e)
            await show_result_notification(hass, "gửi link", None, error=e)

    hass.services.async_register(DOMAIN, "send_link", async_send_link_service,
                                 schema=SERVICE_SEND_LINK_SCHEMA)

    async def async_get_stickers_service(call):
        _LOGGER.debug("Dịch vụ async_get_stickers được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "query": call.data["query"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getStickersByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tìm kiếm sticker: %s", resp.text)
            await show_result_notification(hass, "tìm kiếm sticker", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_stickers: %s", e)
            await show_result_notification(hass, "tìm kiếm sticker", None, error=e)

    hass.services.async_register(DOMAIN, "get_stickers", async_get_stickers_service,
                                 schema=SERVICE_GET_STICKERS_SCHEMA)

    async def async_get_stickers_detail_service(call):
        _LOGGER.debug("Dịch vụ async_get_stickers_detail được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Chuyển đổi stickerId sang số nguyên
            try:
                sticker_id = int(call.data["sticker_id"])
            except ValueError:
                sticker_id = call.data["sticker_id"]

            payload = {
                "accountSelection": call.data["account_selection"],
                "stickerId": sticker_id
            }

            _LOGGER.debug("Gửi payload đến getStickersDetailByAccount: %s", payload)
            url = f"{zalo_server}/api/getStickersDetailByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi lấy chi tiết sticker: %s", resp.text)
            await show_result_notification(hass, "lấy chi tiết sticker", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_stickers_detail: %s", e)
            await show_result_notification(hass, "lấy chi tiết sticker", None, error=e)

    hass.services.async_register(DOMAIN, "get_stickers_detail", async_get_stickers_detail_service,
                                 schema=SERVICE_GET_STICKERS_DETAIL_SCHEMA)

    async def async_create_note_group_service(call):
        _LOGGER.debug("Dịch vụ async_create_note_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "groupId": call.data["group_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "title": call.data["title"],
                    "pinAct": call.data.get("pin_act", True)
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/createNoteGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tạo ghi chú nhóm: %s", resp.text)
            await show_result_notification(hass, "tạo ghi chú nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_create_note_group: %s", e)
            await show_result_notification(hass, "tạo ghi chú nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "create_note_group", async_create_note_group_service,
                                 schema=SERVICE_CREATE_NOTE_GROUP_SCHEMA)

    async def async_edit_note_group_service(call):
        _LOGGER.debug("Dịch vụ async_edit_note_group được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "groupId": call.data["group_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "topicId": call.data["topic_id"],
                    "title": call.data["title"]
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/editNoteGroupByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi sửa ghi chú nhóm: %s", resp.text)
            await show_result_notification(hass, "sửa ghi chú nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_edit_note_group: %s", e)
            await show_result_notification(hass, "sửa ghi chú nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "edit_note_group", async_edit_note_group_service,
                                 schema=SERVICE_EDIT_NOTE_GROUP_SCHEMA)

    async def async_get_list_board_service(call):
        _LOGGER.debug("Dịch vụ async_get_list_board được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "groupId": call.data["group_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getListBoardByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách bảng tin nhóm: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách bảng tin nhóm", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_list_board: %s", e)
            await show_result_notification(hass, "lấy danh sách bảng tin nhóm", None, error=e)

    hass.services.async_register(DOMAIN, "get_list_board", async_get_list_board_service,
                                 schema=SERVICE_GET_LIST_BOARD_SCHEMA)

    async def async_create_poll_service(call):
        _LOGGER.debug("Dịch vụ async_create_poll được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            options_list = call.data["options"].split(",")
            options_list = [opt.strip() for opt in options_list]

            payload = {
                "groupId": call.data["group_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "question": call.data["question"],
                    "options": options_list,
                    "allowMultiChoices": call.data.get("allow_multi_choices", False)
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/createPollByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi tạo bình chọn: %s", resp.text)
            await show_result_notification(hass, "tạo bình chọn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_create_poll: %s", e)
            await show_result_notification(hass, "tạo bình chọn", None, error=e)

    hass.services.async_register(DOMAIN, "create_poll", async_create_poll_service,
                                 schema=SERVICE_CREATE_POLL_SCHEMA)

    async def async_get_poll_detail_service(call):
        _LOGGER.debug("Dịch vụ async_get_poll_detail được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "pollId": call.data["poll_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getPollDetailByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy chi tiết bình chọn: %s", resp.text)
            await show_result_notification(hass, "lấy chi tiết bình chọn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_poll_detail: %s", e)
            await show_result_notification(hass, "lấy chi tiết bình chọn", None, error=e)

    hass.services.async_register(DOMAIN, "get_poll_detail", async_get_poll_detail_service,
                                 schema=SERVICE_GET_POLL_DETAIL_SCHEMA)

    async def async_lock_poll_service(call):
        _LOGGER.debug("Dịch vụ async_lock_poll được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "pollId": int(call.data["poll_id"])
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/lockPollByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi khóa bình chọn: %s", resp.text)
            await show_result_notification(hass, "khóa bình chọn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_lock_poll: %s", e)
            await show_result_notification(hass, "khóa bình chọn", None, error=e)

    hass.services.async_register(DOMAIN, "lock_poll", async_lock_poll_service,
                                 schema=SERVICE_LOCK_POLL_SCHEMA)

    async def async_edit_reminder_service(call):
        _LOGGER.debug("Dịch vụ async_edit_reminder được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"],
                "options": {
                    "topicId": call.data["topic_id"],
                    "title": call.data["title"]
                }
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/editReminderByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi sửa lời nhắc: %s", resp.text)
            await show_result_notification(hass, "sửa lời nhắc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_edit_reminder: %s", e)
            await show_result_notification(hass, "sửa lời nhắc", None, error=e)

    hass.services.async_register(DOMAIN, "edit_reminder", async_edit_reminder_service,
                                 schema=SERVICE_EDIT_REMINDER_SCHEMA)

    async def async_get_reminder_service(call):
        _LOGGER.debug("Dịch vụ async_get_reminder được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "reminderId": call.data["reminder_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getReminderByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy thông tin nhắc hẹn: %s", resp.text)
            await show_result_notification(hass, "lấy thông tin nhắc hẹn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_reminder: %s", e)
            await show_result_notification(hass, "lấy thông tin nhắc hẹn", None, error=e)

    hass.services.async_register(DOMAIN, "get_reminder", async_get_reminder_service,
                                 schema=SERVICE_GET_REMINDER_SCHEMA)

    async def async_get_list_reminder_service(call):
        _LOGGER.debug("Dịch vụ async_get_list_reminder được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Chuyển đổi type từ chuỗi sang số (0 cho user, 1 cho group)
            reminder_type = call.data.get("type", "0")
            reminder_type_num = 1 if reminder_type.lower() == "group" else 0

            payload = {
                "accountSelection": call.data["account_selection"],
                "threadId": call.data["thread_id"],
                "type": reminder_type_num
            }

            # Thêm options nếu có
            if "options" in call.data:
                payload["options"] = call.data["options"]

            _LOGGER.debug("Gửi payload đến getListReminderByAccount: %s", payload)
            url = f"{zalo_server}/api/getListReminderByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách lời nhắc: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách lời nhắc", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_list_reminder: %s", e)
            await show_result_notification(hass, "lấy danh sách lời nhắc", None, error=e)

    hass.services.async_register(DOMAIN, "get_list_reminder", async_get_list_reminder_service,
                                 schema=SERVICE_GET_LIST_REMINDER_SCHEMA)

    async def async_get_reminder_responses_service(call):
        _LOGGER.debug("Dịch vụ async_get_reminder_responses được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "reminderId": call.data["reminder_id"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/getReminderResponsesByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách phản hồi nhắc hẹn: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách phản hồi nhắc hẹn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_reminder_responses: %s", e)
            await show_result_notification(hass, "lấy danh sách phản hồi nhắc hẹn", None, error=e)

    hass.services.async_register(DOMAIN, "get_reminder_responses", async_get_reminder_responses_service,
                                 schema=SERVICE_GET_REMINDER_RESPONSES_SCHEMA)

    async def async_add_quick_message_service(call):
        _LOGGER.debug("Dịch vụ async_add_quick_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Tạo payload đúng định dạng theo yêu cầu của API
            add_payload = {
                "keyword": call.data["keyword"],
                "title": call.data["title"],
                "message": {
                    "title": call.data["title"],
                    "params": ""
                }
            }

            payload = {
                "accountSelection": call.data["account_selection"],
                "addPayload": add_payload
            }

            _LOGGER.debug("Gửi payload đến addQuickMessageByAccount: %s", payload)
            url = f"{zalo_server}/api/addQuickMessageByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi thêm tin nhắn nhanh: %s", resp.text)
            await show_result_notification(hass, "thêm tin nhắn nhanh", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_add_quick_message: %s", e)
            await show_result_notification(hass, "thêm tin nhắn nhanh", None, error=e)

    hass.services.async_register(DOMAIN, "add_quick_message", async_add_quick_message_service,
                                 schema=SERVICE_ADD_QUICK_MESSAGE_SCHEMA)

    async def async_get_quick_message_service(call):
        _LOGGER.debug("Dịch vụ async_get_quick_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }

            _LOGGER.debug("Gửi payload đến getQuickMessageByAccount: %s", payload)
            url = f"{zalo_server}/api/getQuickMessageByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách tin nhắn nhanh: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách tin nhắn nhanh", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_quick_message: %s", e)
            await show_result_notification(hass, "lấy danh sách tin nhắn nhanh", None, error=e)

    hass.services.async_register(DOMAIN, "get_quick_message", async_get_quick_message_service,
                                 schema=SERVICE_GET_QUICK_MESSAGE_SCHEMA)

    async def async_remove_quick_message_service(call):
        _LOGGER.debug("Dịch vụ async_remove_quick_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Chuyển đổi item_ids từ chuỗi sang mảng số nguyên
            item_ids = [int(item_id.strip()) for item_id in call.data["item_ids"].split(',')]

            payload = {
                "accountSelection": call.data["account_selection"],
                "itemIds": item_ids if len(item_ids) > 1 else item_ids[0]
            }

            _LOGGER.debug("Gửi payload đến removeQuickMessageByAccount: %s", payload)
            url = f"{zalo_server}/api/removeQuickMessageByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi xóa tin nhắn nhanh: %s", resp.text)
            await show_result_notification(hass, "xóa tin nhắn nhanh", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_remove_quick_message: %s", e)
            await show_result_notification(hass, "xóa tin nhắn nhanh", None, error=e)

    hass.services.async_register(DOMAIN, "remove_quick_message", async_remove_quick_message_service,
                                 schema=SERVICE_REMOVE_QUICK_MESSAGE_SCHEMA)

    async def async_update_quick_message_service(call):
        _LOGGER.debug("Dịch vụ async_update_quick_message được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Tạo payload đúng định dạng theo yêu cầu của API
            update_payload = {
                "keyword": call.data["keyword"],
                "title": call.data["title"],
                "message": {
                    "title": call.data["title"],
                    "params": ""
                }
            }

            # Chuyển đổi item_id sang số nguyên nếu cần
            try:
                item_id = int(call.data["item_id"])
            except ValueError:
                item_id = call.data["item_id"]

            payload = {
                "accountSelection": call.data["account_selection"],
                "itemId": item_id,
                "updatePayload": update_payload
            }

            _LOGGER.debug("Gửi payload đến updateQuickMessageByAccount: %s", payload)
            url = f"{zalo_server}/api/updateQuickMessageByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi cập nhật tin nhắn nhanh: %s", resp.text)
            await show_result_notification(hass, "cập nhật tin nhắn nhanh", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_update_quick_message: %s", e)
            await show_result_notification(hass, "cập nhật tin nhắn nhanh", None, error=e)

    hass.services.async_register(DOMAIN, "update_quick_message", async_update_quick_message_service,
                                 schema=SERVICE_UPDATE_QUICK_MESSAGE_SCHEMA)

    async def async_get_labels_service(call):
        _LOGGER.debug("Dịch vụ async_get_labels được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"]
            }

            _LOGGER.debug("Gửi payload đến getLabelsByAccount: %s", payload)
            url = f"{zalo_server}/api/getLabelsByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách nhãn: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách nhãn", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_labels: %s", e)
            await show_result_notification(hass, "lấy danh sách nhãn", None, error=e)

    hass.services.async_register(DOMAIN, "get_labels", async_get_labels_service,
                                 schema=SERVICE_GET_LABELS_SCHEMA)

    async def async_block_view_feed_service(call):
        _LOGGER.debug("Dịch vụ async_block_view_feed được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Đảm bảo isBlockFeed là giá trị boolean
            is_block_str = str(call.data["is_block_feed"]).lower()
            is_block = is_block_str == "true" or is_block_str == "1" or is_block_str == "yes"

            payload = {
                "accountSelection": call.data["account_selection"],
                "userId": call.data["user_id"],
                "isBlockFeed": is_block
            }

            _LOGGER.debug("Gửi payload đến blockViewFeedByAccount: %s", payload)
            url = f"{zalo_server}/api/blockViewFeedByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi chặn/bỏ chặn xem nhật ký: %s", resp.text)
            await show_result_notification(hass, "chặn/bỏ chặn xem nhật ký", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_block_view_feed: %s", e)
            await show_result_notification(hass, "chặn/bỏ chặn xem nhật ký", None, error=e)

    hass.services.async_register(DOMAIN, "block_view_feed", async_block_view_feed_service,
                                 schema=SERVICE_BLOCK_VIEW_FEED_SCHEMA)

    async def async_change_account_avatar_service(call):
        _LOGGER.debug("Dịch vụ async_change_account_avatar được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "avatarSource": call.data["avatar_source"]
            }

            _LOGGER.debug("Gửi payload đến changeAccountAvatarByAccount: %s", payload)
            url = f"{zalo_server}/api/changeAccountAvatarByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi thay đổi ảnh đại diện: %s", resp.text)
            await show_result_notification(hass, "thay đổi ảnh đại diện", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_change_account_avatar: %s", e)
            await show_result_notification(hass, "thay đổi ảnh đại diện", None, error=e)

    hass.services.async_register(DOMAIN, "change_account_avatar", async_change_account_avatar_service,
                                 schema=SERVICE_CHANGE_ACCOUNT_AVATAR_SCHEMA)

    async def async_get_avatar_list_service(call):
        _LOGGER.debug("Dịch vụ async_get_avatar_list được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)

            # Thêm các tham số count và page nếu có
            payload = {
                "accountSelection": call.data["account_selection"]
            }

            if "count" in call.data:
                try:
                    payload["count"] = int(call.data["count"])
                except ValueError:
                    payload["count"] = call.data["count"]

            if "page" in call.data:
                try:
                    payload["page"] = int(call.data["page"])
                except ValueError:
                    payload["page"] = call.data["page"]

            _LOGGER.debug("Gửi payload đến getAvatarListByAccount: %s", payload)
            url = f"{zalo_server}/api/getAvatarListByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi lấy danh sách ảnh đại diện: %s", resp.text)
            await show_result_notification(hass, "lấy danh sách ảnh đại diện", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_get_avatar_list: %s", e)
            await show_result_notification(hass, "lấy danh sách ảnh đại diện", None, error=e)

    hass.services.async_register(DOMAIN, "get_avatar_list", async_get_avatar_list_service,
                                 schema=SERVICE_GET_AVATAR_LIST_SCHEMA)

    async def async_last_online_service(call):
        _LOGGER.debug("Dịch vụ async_last_online được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "accountSelection": call.data["account_selection"],
                "userId": call.data["user_id"]  # Sửa từ uid thành userId theo yêu cầu của API
            }

            _LOGGER.debug("Gửi payload đến lastOnlineByAccount: %s", payload)
            url = f"{zalo_server}/api/lastOnlineByAccount"
            _LOGGER.debug("URL đầy đủ: %s", url)

            resp = await hass.async_add_executor_job(
                lambda: session.post(url, json=payload)
            )
            _LOGGER.info("Phản hồi xem thời gian hoạt động cuối: %s", resp.text)
            await show_result_notification(hass, "xem thời gian hoạt động cuối", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_last_online: %s", e)
            await show_result_notification(hass, "xem thời gian hoạt động cuối", None, error=e)

    hass.services.async_register(DOMAIN, "last_online", async_last_online_service,
                                 schema=SERVICE_LAST_ONLINE_SCHEMA)

    async def async_send_typing_event_service(call):
        _LOGGER.debug("Dịch vụ async_send_typing_event được gọi với: %s", call.data)
        try:
            await hass.async_add_executor_job(zalo_login)
            payload = {
                "threadId": call.data["thread_id"],
                "accountSelection": call.data["account_selection"]
            }
            resp = await hass.async_add_executor_job(
                lambda: session.post(f"{zalo_server}/api/sendTypingEventByAccount", json=payload)
            )
            _LOGGER.info("Phản hồi gửi thông báo typing: %s", resp.text)
            await show_result_notification(hass, "gửi thông báo typing", resp)
        except Exception as e:
            _LOGGER.error("Lỗi trong async_send_typing_event: %s", e)
            await show_result_notification(hass, "gửi thông báo typing", None, error=e)    

    hass.services.async_register(DOMAIN, "send_typing_event", async_send_typing_event_service,
                                 schema=SERVICE_SEND_TYPING_EVENT_SCHEMA)

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "zalo_bot")},
        manufacturer="Smarthome Black",
        name="Zalo Bot",
        model="Zalo Bot",
        sw_version="2025.8.30"
    )
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    # Unload các platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Xóa dữ liệu entry
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
