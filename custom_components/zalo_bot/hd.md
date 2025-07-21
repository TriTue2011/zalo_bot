# Hướng Dẫn Thay Đổi (hd.md)

Dưới đây là danh sách đầy đủ các thay đổi tôi sẽ thực hiện để mở rộng integration Zalo Bot trong Home Assistant. Mục tiêu là thêm các services mới tương ứng với tất cả API chính từ backend (không bao gồm debug APIs). Các thay đổi sẽ được áp dụng qua tool edit_file, đảm bảo code chạy ngay lập tức và không có linter errors (dùng voluptuous cho schema, logging chuẩn HASS).

## 1. **Các file sẽ được chỉnh sửa/tạo**
- **__init__.py**: Thêm schemas (vol.Schema) cho từng service mới, thêm async functions để gọi API (tương tự async_send_message_service: login server, chuẩn bị payload, gọi POST/GET với requests.Session, log response). Đăng ký services với hass.services.async_register.
- **services.yaml**: Thêm definitions cho từng service mới (description, fields với selectors như text/select).
- **manifest.json**: Tăng version lên "2025.7.18" để mark update.
- **hd.md** (này): File mới để liệt kê thay đổi (bạn yêu cầu).

## 2. **Danh sách services mới được thêm**
Mỗi service map đến một API endpoint của backend (zalo_server/api/...). Params dựa trên API backend. Không thêm debug services.

### Account Management
- **zalo_bot.get_logged_accounts**: Lấy list account Zalo (no params). Map: GET /api/accounts.
- **zalo_bot.get_account_details**: Lấy chi tiết account (params: own_id). Map: GET /api/accounts/:ownId.

### Zalo Core
- **zalo_bot.find_user**: Tìm user (params: phone, account_selection). Map: POST /api/findUserByAccount.
- **zalo_bot.get_user_info**: Lấy info user (params: user_id, account_selection). Map: POST /api/getUserInfoByAccount.
- **zalo_bot.send_friend_request**: Gửi mời kết bạn (params: user_id, message, account_selection). Map: POST /api/sendFriendRequestByAccount.
- **zalo_bot.create_group**: Tạo group (params: members (list), name, avatar_path, account_selection). Map: POST /api/createGroupByAccount.
- **zalo_bot.get_group_info**: Lấy info group (params: group_id (text), account_selection). Map: POST /api/getGroupInfoByAccount.
- **zalo_bot.add_user_to_group**: Thêm thành viên (params: group_id, member_id (text), account_selection). Map: POST /api/addUserToGroupByAccount.
- **zalo_bot.remove_user_from_group**: Xóa thành viên (params: group_id, member_id (text), account_selection). Map: POST /api/removeUserFromGroupByAccount.
- **zalo_bot.send_image_to_user**: Gửi 1 ảnh đến user (params: image_path, thread_id, account_selection). Map: POST /api/sendImageToUserByAccount.
- **zalo_bot.send_images_to_user**: Gửi nhiều ảnh đến user (params: image_paths (text), thread_id, account_selection). Map: POST /api/sendImagesToUserByAccount.
- **zalo_bot.send_image_to_group**: Gửi 1 ảnh đến group (params: image_path, thread_id, account_selection). Map: POST /api/sendImageToGroupByAccount.
- **zalo_bot.send_images_to_group**: Gửi nhiều ảnh đến group (params: image_paths (text), thread_id, account_selection). Map: POST /api/sendImagesToGroupByAccount.

### Webhook Management
- **zalo_bot.get_account_webhooks**: Lấy all webhook configs (no params). Map: GET /api/account-webhooks.
- **zalo_bot.get_account_webhook**: Lấy config cho account (params: own_id). Map: GET /api/account-webhook/:ownId.
- **zalo_bot.set_account_webhook**: Cập nhật config (params: own_id, message_webhook_url, group_event_webhook_url, reaction_webhook_url). Map: POST /api/account-webhook.
- **zalo_bot.delete_account_webhook**: Xóa config (params: own_id). Map: DELETE /api/account-webhook/:ownId.

### Proxy Management
- **zalo_bot.get_proxies**: Lấy list proxy (no params). Map: GET /api/proxies.
- **zalo_bot.add_proxy**: Thêm proxy (params: proxy_url). Map: POST /api/proxies.
- **zalo_bot.remove_proxy**: Xóa proxy (params: proxy_url). Map: DELETE /api/proxies.

## 3. **Chi tiết triển khai**
- Mỗi service: Async function gọi zalo_login, chuẩn bị payload, POST/GET đến endpoint, log response. Xử lý exception với _LOGGER.error.
- Params: Sử dụng vol.Required/vol.Optional, hỗ trợ list (ví dụ: members là text nhưng parse thành list trong code nếu cần).
- Không thay đổi code hiện tại (giữ send_message/send_image), chỉ thêm mới.
- Test: Reload HASS sau edit, kiểm tra trong Developer Tools.

## 4. **Rủi ro và lưu ý**
- Đảm bảo backend chạy (addon) trước khi gọi services.
- Nếu API backend thay đổi, cần update integration.
- Tăng version manifest để HASS nhận update.

Thay đổi sẽ được apply qua tool edit_file. Sau khi hoàn tất, bạn cần reload/restart HASS để thấy services mới. 