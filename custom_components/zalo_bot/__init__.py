import logging
import os
import shutil
import requests
import time
import http.server
import socketserver
import threading
import socket
from urllib.parse import quote
from homeassistant.components import webhook
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)
WEBHOOK_ID = "zalo_bot_webhook"
WWW_DIR = "/config/www"
PUBLIC_DIR = os.path.join(WWW_DIR, "zalo_bot")

# Định nghĩa CONFIG_SCHEMA để chỉ ra rằng tích hợp này chỉ sử dụng config entry
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def find_free_port():
    """Tìm một cổng trống để sử dụng"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
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
    encoded_filename = quote(file_name)

    # Tìm một cổng trống
    port = find_free_port()

    # Chuẩn bị máy chủ
    class SingleFileHandler(http.server.SimpleHTTPRequestHandler):
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
                        self.send_header("Content-type", content_type)
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

        def log_message(self, format, *args):
            # Tắt log để không làm ảnh hưởng đến log của Home Assistant
            pass

    # Tạo máy chủ và chạy trong một thread riêng
    httpd = socketserver.TCPServer(("0.0.0.0", port), SingleFileHandler)

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
    hass.data[DOMAIN][entry.entry_id] = entry.data
    session = requests.Session()
    zalo_server = entry.data["zalo_server"]
    admin_user = entry.data[CONF_USERNAME]
    admin_pass = entry.data[CONF_PASSWORD]

    def zalo_login():
        resp = session.post(f"{zalo_server}/api/login", json={
            "username": admin_user,
            "password": admin_pass
        })
        if resp.status_code == 200 and resp.json().get("success"):
            _LOGGER.info("Đăng nhập quản trị viên Zalo thành công")
        else:
            _LOGGER.error("Đăng nhập quản trị viên Zalo thất bại: %s", resp.text)

    async def handle_webhook(hass, webhook_id, request):
        data = await request.json()
        hass.states.async_set("sensor.zalo_last_message", str(data))
        return {}
    try:
        webhook.async_unregister(hass, WEBHOOK_ID)
    except Exception:
        pass
    webhook.async_register(
        hass, DOMAIN, "Webhook Zalo Bot", WEBHOOK_ID, handle_webhook
    )

    SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
        vol.Required("message"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
        vol.Optional("type", default="0"): str,
    })
    SERVICE_SEND_IMAGE_SCHEMA = vol.Schema({
        vol.Required("image_path"): str,
        vol.Required("thread_id"): str,
        vol.Required("account_selection"): str,
        vol.Optional("type", default="0"): str,
    })

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
    hass.services.async_register(
        DOMAIN, "send_message", async_send_message_service, schema=SERVICE_SEND_MESSAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "send_image", async_send_image_service, schema=SERVICE_SEND_IMAGE_SCHEMA
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

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "zalo_bot")},
        manufacturer="Smarthome Black",
        name="Zalo Bot",
        model="Zalo Bot",
        sw_version="2025.7.11"
    )
    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
