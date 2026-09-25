## ❓ Nhóm Support:
- Zalo: https://zalo.me/g/alvkgn274
- Telegram: https://t.me/smarthomeblack

---

# Zalo Bot cho Home Assistant

## Giới thiệu

Dự án này cung cấp tích hợp Zalo Bot cho Home Assistant, giúp gửi/nhận thông
báo, gọi service và xây automation qua Zalo cá nhân.

> Cần cài **cả hai phần**: gateway Zalo Bot (add-on hoặc Docker) để đăng nhập
> Zalo, và custom integration này để Home Assistant có entity/service. HACS
> không tự thay thế gateway Node.js.

## Phiên bản và cập nhật

- Custom integration hiện tại: **2026.9.25**.
- Add-on/gateway tương thích: **2026.8.23.3** hoặc mới hơn; muốn `send_voice`
  ra **bong bóng tin thoại** thì cần **2026.9.25.0** trở lên.

> **Nên cập nhật cả hai.** Bản 2026.8.23 sửa một lỗi khiến gateway tự xoá cookie
> đăng nhập khi mạng chập chờn, và cắt việc tích hợp đăng nhập lại trước mỗi
> lượt gọi — trên máy ARM mỗi lần đăng nhập làm gateway đứng hình 3,4 giây.

Trong HACS, chọn **Zalo Bot → Download** rồi **khởi động lại Home Assistant**.
Không cần xoá integration hay quét QR lại. Nếu cũng cập nhật add-on, cập nhật
trong **Settings → Add-ons → Zalo Bot** và khởi động lại add-on; giữ nguyên
`data_directory` để bảo toàn cookie, webhook và proxy.


## Hướng dẫn cài đặt

### 1. Cài đặt qua HACS(Khuyến nghị)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TriTue2011&repository=zalo_bot)

- Tải về sau đó khởi động lại Home Assistant

### 2. Cài đặt thủ công

Nếu không sử dụng HACS, bạn có thể cài đặt thủ công như sau:

- Tải mã nguồn repo này về máy.
- Sao chép thư mục `custom_components/zalo_bot` vào thư mục `custom_components` trong thư mục cấu hình Home Assistant của bạn.
- Khởi động lại Home Assistant.
- Vào Cài đặt > Thiết bị & Dịch vụ > Thêm tích hợp mới > Chọn "Zalo Bot" và cấu hình theo hướng dẫn.

### 3. Cấu hình

Khung cấu hình sẽ **thử kết nối ngay** khi bạn bấm Gửi. Sai địa chỉ thì báo
"Không gọi được tới máy chủ Zalo", sai mật khẩu thì báo "Máy chủ từ chối tài
khoản hoặc mật khẩu" — không phải đợi tới lúc gọi service đầu tiên mới biết.

Địa chỉ máy chủ được chuẩn hoá tự động: gõ `192.168.1.10:3000` hay
`http://192.168.1.10:3000/` đều được.

**Mật khẩu** không còn điền sẵn `admin`. Gateway tự sinh một mật khẩu ngẫu nhiên
lần chạy đầu và ghi vào tệp `THONG-TIN-DANG-NHAP.txt` trong thư mục dữ liệu của
add-on — mở bằng File editor hoặc Samba là thấy. Gõ đại vài lần sẽ bị máy chủ
khoá IP 15 phút.


- Nếu cài Zalo Bot bằng add-on trên cùng máy Home Assistant, dùng
  `http://localhost:3000`. Nếu gateway ở máy khác, dùng
  `http://<ip-may-gateway>:3000`.
- Username mặc định là `admin`. Password là giá trị đã điền khi cài add-on, hoặc
  mật khẩu ngẫu nhiên trong `THONG-TIN-DANG-NHAP.txt`/tab **Log** của add-on.
  Không còn mật khẩu mặc định `admin` / `admin` cho cài đặt mới.
- Quét QR và xác nhận tài khoản Zalo trong giao diện gateway trước khi thêm
  integration.

<img title="Zalo Bot" src="https://raw.githubusercontent.com/TriTue2011/zalo_bot/refs/heads/main/img/3.png" width="100%"></img>

<img title="Zalo Bot" src="https://raw.githubusercontent.com/TriTue2011/zalo_bot/refs/heads/main/img/4.png" width="100%"></img>

 - Nếu kết nối thành công và đăng nhập zalo bot thành công thì sẽ có cảm biến báo đã kết nối, các cảm biến sẽ cập nhập 1 phút 1 lần để cho biết trạng thái đăng nhập Zalo bot, có thể tạo tự động hóa để thông báo nếu như zalo bot bị đăng xuất hoặc cần đăng nhập lại, 

<img title="Zalo Bot" src="https://raw.githubusercontent.com/TriTue2011/zalo_bot/refs/heads/main/img/8.png" width="100%"></img>

### 4. Hướng Dẫn Sử Dụng
- Tích hợp có 96 dịch vụ; hay dùng nhất là `zalo_bot.send_message`, `send_image`,
  `send_file`, `send_video`, `send_voice`. Cách gọi từng dịch vụ và bảng tra cứu
  đầy đủ ở mục **Hướng dẫn gọi dịch vụ (đầy đủ)** bên dưới.
- Vào trang quản lý ZALO BOT, Chọn Theo dõi tin nhắn và lấy Thread ID 
- Sau đó dùng tài khoản bất kỳ gửi tin nhắn cho Acc Bot hoặc thêm Acc bot vào trong 1 nhóm, sau đó gửi tin nhắn từ tài khoản chính vào nhóm
- Dùng Thread ID để điền vào cấu hình tự động hóa, như gửi ảnh, gửi tin nhắn
- Nếu gửi cho tài khoản cá nhân, đặt `type: "0"` (hoặc `"user"`); gửi vào nhóm
  đặt `type: "1"` (hoặc `"group"`).

<img title="Zalo Bot" src="https://raw.githubusercontent.com/TriTue2011/zalo_bot/refs/heads/main/img/5.png" width="100%"></img>

### 5. Hướng Dẫn Tạo Hội Thoại Và Tự Động Hóa

- [▶️ Xem video hướng dẫn trên YouTube](https://www.youtube.com/watch?v=xdl0oUv1LDg)

- code

```yaml
alias: zalo bot
description: ""
triggers:
  - allowed_methods:
      - POST
      - PUT
      - GET
      - HEAD
    local_only: false
    webhook_id: "-kckRb3xuIlUYoMHgbwIwPMKq"
    trigger: webhook
conditions:
  - condition: template
    value_template: >
      {{ '@Blackbot' in trigger.json.data.content and trigger.json.data.uidFrom
      == '85276xxxxxxxxx203115' }}
actions:
  - variables:
      user_message: "{{ trigger.json.data.content }}"
      conversation_id: "{{ trigger.json.data.uidFrom }}"
  - data:
      text: "{{ user_message }}"
      agent_id: conversation.google_ai_conversation
      conversation_id: "{{ conversation_id }}"
    response_variable: convo_response
    action: conversation.process
  - action: zalo_bot.send_message
    data:
      type: "1"
      thread_id: "{{ trigger.json.data.idTo }}"
      account_selection: "+84123456789"
      message: "Bot-Hass: {{ convo_response.response.speech.plain.speech }}"
      quote: |
        {% if trigger.json.data.msgType == 'webchat' %}
          {{ {'content': trigger.json.data.content, 'uidFrom': trigger.json.data.uidFrom, 'cliMsgId': trigger.json.data.cliMsgId} }}
        {% else %}
          {{ {'content': trigger.json.data.content, 'msgType': trigger.json.data.msgType, 'uidFrom': trigger.json.data.uidFrom, 'cliMsgId': trigger.json.data.cliMsgId} }}
        {% endif %}
mode: single

```

Thay 85276xxxxxxxxx203115 bằng uidFrom của bạn, thay @Blackbot thành tên bot của bạn, thay +84123456789 thành sdt của bot.

### ID Zalo và ID thao tác

| Loại | Ví dụ | Cách nhập |
|---|---|---|
| ID người dùng, nhóm, tin nhắn | `5841349563795164131` | Giữ nguyên dạng **text** để không mất chữ số với ID lớn. |
| ID poll, sticker, sticker album, quick message | `123456789` | Nhập số nguyên không âm, tối đa `9007199254740991`; không dùng `poll123`, số thập phân hoặc ID quá lớn. |

Poll, sticker và quick message là các API `zca-js` dùng JavaScript number. Bản
hiện tại kiểm tra dữ liệu trước khi gọi gateway để tránh JavaScript làm tròn
sang một ID khác.

## Hướng dẫn gọi dịch vụ (đầy đủ)

Tích hợp có **96 dịch vụ** `zalo_bot.*`. Phần này gồm: bốn tham số dùng chung,
cách nhận kết quả, cách trả lời đúng chỗ tin vừa đến, ví dụ cho các dịch vụ hay
dùng, và cuối cùng là bảng tra cứu đủ 96 dịch vụ.

Thử nhanh bất kỳ dịch vụ nào ở **Công cụ nhà phát triển → Hành động**, chọn
dịch vụ rồi bấm **Chế độ YAML** để dán các ví dụ dưới đây.

### Bốn tham số dùng chung

| Tham số | Là gì | Lấy ở đâu |
|---|---|---|
| `account_selection` | Tài khoản Zalo **gửi đi** (tài khoản bot). Nhận **ownId** hoặc **số điện thoại**. | Trang quản lý gateway, hoặc gọi `zalo_bot.get_logged_accounts`. Số điện thoại phải gõ **đúng như gateway hiển thị**; không chắc thì dùng ownId. Trong automation nhận tin: `{{ trigger.json._accountId }}`. |
| `thread_id` | Nơi **nhận**: ID người (chat riêng) hoặc ID nhóm. | Mục **Theo dõi tin nhắn** trên trang gateway, hoặc `{{ trigger.json.threadId }}` khi trả lời. Luôn để trong dấu nháy `"..."` — ID dài 19 chữ số, để dạng số là mất chữ số cuối. |
| `type` | Người hay nhóm. | `"0"` hoặc `"user"` = người; `"1"` hoặc `"group"` = nhóm. Mọi dịch vụ nhận cả hai cách viết. Bỏ trống = người. Trả lời tin vừa đến: `{{ trigger.json.type }}`. |
| `ttl` | Tự huỷ tin sau bao lâu, tính bằng **mili giây**. | `0` = không tự huỷ. `60000` = 1 phút, `3600000` = 1 giờ. |

> **Sai `type` là lỗi hay gặp nhất.** Gửi vào nhóm mà quên `type: "1"` thì Zalo
> hiểu là gửi cho một *người* có ID đó — không tới đâu cả. Từ bản 2026.9.25 giá
> trị lạ (ví dụ `"2"`, `"nhom"`) bị từ chối ngay khi gọi thay vì lặng lẽ thành
> "người".

### Nhận kết quả trả về

Mọi dịch vụ đều trả kết quả, nên dùng được `response_variable`:

```yaml
- action: zalo_bot.get_all_groups
  data:
    account_selection: "{{ trigger.json._accountId }}"
  response_variable: ket_qua
- action: persistent_notification.create
  data:
    message: "{{ ket_qua }}"
```

Kết quả có dạng `{"success": true, "data": ..., "usedAccount": {...}}`; lỗi thì
`{"success": false, "error": "..."}` hoặc `{"error": "..."}`. Bật công tắc
**Thông báo** của thiết bị Zalo Bot để thấy kết quả mỗi lần gọi ngay trong HA.

### Trả lời đúng chỗ tin vừa đến

Gateway đẩy mỗi tin đến vào webhook của Home Assistant (đặt URL ở trang gateway
hoặc bằng `zalo_bot.set_account_webhook`). Trong automation, `trigger.json` có:

| Trường | Ý nghĩa |
|---|---|
| `trigger.json.type` | `0` chat riêng, `1` nhóm |
| `trigger.json.threadId` | Nơi tin đến — gửi trả vào đây |
| `trigger.json._accountId` | Tài khoản bot đã nhận tin — gửi trả bằng tài khoản này |
| `trigger.json.data.uidFrom` | ID người gửi |
| `trigger.json.data.dName` | Tên hiển thị người gửi |
| `trigger.json.data.content` | Nội dung (chữ, hoặc đối tượng nếu là ảnh/tệp) |
| `trigger.json.data.msgId`, `trigger.json.data.cliMsgId` | Hai mã của tin — cần cho thả cảm xúc, trích dẫn, xoá |

Mẫu trả lời dùng được cho **cả chat riêng lẫn nhóm**, không phải sửa gì:

```yaml
- action: zalo_bot.send_message
  data:
    account_selection: "{{ trigger.json._accountId }}"
    thread_id: "{{ trigger.json.threadId }}"
    type: "{{ trigger.json.type }}"
    message: "Đã nhận: {{ trigger.json.data.content }}"
```

### Gửi tin nhắn — `send_message`

```yaml
action: zalo_bot.send_message
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "0"
  message: "Cửa chính **đang mở** quá 10 phút"
  ttl: 0
```

- `message` hiểu markdown (đậm, nghiêng, màu…) — xem mục **Định dạng chữ**.
- **Trích dẫn** tin đang trả lời bằng `quote`. Cần đủ `content`, `uidFrom`,
  `cliMsgId`. Tin gốc là chữ thường (`msgType` = `webchat`) thì **bỏ** `msgType`;
  tin gốc là ảnh, tệp… thì thêm `msgType: "{{ trigger.json.data.msgType }}"`
  (ví dụ ở mục 5 xử lý sẵn cả hai):

```yaml
action: zalo_bot.send_message
data:
  account_selection: "{{ trigger.json._accountId }}"
  thread_id: "{{ trigger.json.threadId }}"
  type: "{{ trigger.json.type }}"
  message: "Trả lời bạn đây"
  quote:
    content: "{{ trigger.json.data.content }}"
    uidFrom: "{{ trigger.json.data.uidFrom }}"
    cliMsgId: "{{ trigger.json.data.cliMsgId }}"
```

### Gửi ảnh, tệp, video

Cả ba nhận **đường dẫn trong máy Home Assistant** (`/config/...`) hoặc **URL**
`http(s)://`.

```yaml
action: zalo_bot.send_image
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "1"
  image_path: "/config/www/snapshot/cong.jpg"
  message: "Có người ở cổng"
```

```yaml
action: zalo_bot.send_file
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  file_path_or_url: "/config/www/bao_cao/dien_thang_9.pdf"
  message: "Báo cáo điện tháng 9"
```

```yaml
action: zalo_bot.send_video
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "1"
  video_path_or_url: "/config/www/clip/cong.mp4"
  thumbnail_url: "/config/www/clip/cong.jpg"   # bỏ trống thì dùng chính video làm ảnh bìa
  message: "Clip lúc chuông reo"
```

Nhiều ảnh một lượt: `send_images_to_user` / `send_images_to_group`, các đường
dẫn cách nhau bằng dấu phẩy: `image_paths: "/config/www/a.jpg,/config/www/b.jpg"`.
Tối đa 24 ảnh và 100 MB mỗi lượt.

**Tệp trong máy được đưa sang gateway thế nào** (cần biết khi gửi không được):

- Gateway là add-on cùng máy (`http://localhost:3000`): ảnh và tệp được chép vào
  `/config/www/zalo_bot/` để gateway đọc.
- Còn lại (gateway ở máy khác, và mọi video/tin thoại): Home Assistant mở một
  cổng HTTP tạm **60–90 giây** trên IP LAN của nó để gateway tải tệp về. Máy
  gateway phải gọi được tới IP đó; tường lửa chặn là gửi hỏng.
- Dùng URL thì gateway tự tải, không cần hai điều trên.

### Gửi tin thoại — `send_voice`

Người nhận thấy **bong bóng tin thoại** bấm nghe được, như ghi âm bằng app Zalo,
không phải một tệp đính kèm.

```yaml
action: zalo_bot.send_voice
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "0"
  voice_path: "/config/www/am_thanh/chuong_cua.mp3"   # hoặc URL http(s)://
```

> **Cần add-on/gateway 2026.9.25.0 trở lên.** Bản này tự đổi âm thanh (mp3, wav,
> ogg…) sang đúng định dạng tin thoại của Zalo (AAC 16 kHz một kênh) rồi tải lên
> máy chủ Zalo. Gateway cũ gửi thẳng đường dẫn cho điện thoại người nhận tự tải,
> nên tệp trong mạng nhà hay URL nội bộ đều **không nghe được** khi người nhận ở
> ngoài.

**Đọc chữ thành tin thoại (TTS).** Home Assistant có sẵn API trả URL tệp đọc của
bất kỳ dịch vụ TTS nào. Khai một `rest_command` trong `configuration.yaml`:

```yaml
rest_command:
  zalo_tts_url:
    url: "http://127.0.0.1:8123/api/tts_get_url"
    method: POST
    headers:
      Authorization: !secret ha_bearer_token   # "Bearer <long-lived access token>"
    content_type: "application/json"
    payload: '{"engine_id": "{{ engine }}", "message": {{ message | tojson }}}'
```

- `ha_bearer_token` trong `secrets.yaml` có dạng `"Bearer eyJ..."`; tạo token ở
  **Hồ sơ → Bảo mật → Mã truy cập dài hạn**.
- `127.0.0.1:8123` đúng khi Home Assistant chạy trên máy (HA OS, Supervised,
  Docker mạng host). Khác thì thay bằng địa chỉ HA.

Rồi dùng trong automation:

```yaml
- action: rest_command.zalo_tts_url
  data:
    engine: tts.google_translate_vi_com    # thực thể TTS của bạn (Cài đặt → Thực thể, lọc "tts.")
    message: "Cửa chính đang mở quá mười phút"
  response_variable: tts
- action: zalo_bot.send_voice
  data:
    account_selection: "84901234567"
    thread_id: "5841349563795164131"
    type: "0"
    voice_path: "{{ tts.content.url }}"
```

URL này nằm trên địa chỉ nội bộ của Home Assistant (**Cài đặt → Hệ thống → Mạng
→ URL mạng cục bộ**); gateway phải gọi được tới đó. Người nhận ở đâu cũng nghe
được vì gateway đã tải lên máy chủ Zalo.

### Sticker, liên kết, danh thiếp

```yaml
# Tìm sticker theo từ khoá, rồi gửi bằng ID số lấy từ kết quả
- action: zalo_bot.get_stickers
  data:
    account_selection: "84901234567"
    query: "vui"
  response_variable: st
- action: zalo_bot.send_sticker
  data:
    account_selection: "84901234567"
    thread_id: "5841349563795164131"
    type: "0"
    sticker_id: 1234
```

```yaml
action: zalo_bot.send_link
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "1"
  link: "https://www.home-assistant.io"
  message: "Xem cái này nhé"
```

`send_card` gửi danh thiếp một người (`user_id`) vào `thread_id`. Từ 2026.9.25,
`send_link` và `send_card` gửi được vào nhóm (`type: "1"`); bản cũ chỉ gửi được
chat riêng.

### Thả cảm xúc, thu hồi, xoá, chuyển tiếp

Các thao tác này cần **hai mã** của tin (`msgId` và `cliMsgId`), lấy từ
`trigger.json.data`.

```yaml
action: zalo_bot.add_reaction
data:
  account_selection: "{{ trigger.json._accountId }}"
  thread_id: "{{ trigger.json.threadId }}"
  type: "{{ trigger.json.type }}"
  msg_id: "{{ trigger.json.data.msgId }}"
  cli_msg_id: "{{ trigger.json.data.cliMsgId }}"
  icon: like      # heart, haha, wow, cry, angry, ok, thanks, pray… (đủ danh sách ở bảng dưới)
```

- `undo_message` — **thu hồi** tin bot đã gửi (hai phía đều mất). Cần `msg_id`,
  nên có thêm `cli_msg_id`; thiếu nó có trường hợp Zalo từ chối. Tin tự huỷ thì
  dùng `ttl` lúc gửi cho gọn.
- `delete_message` — **xoá** một tin, mặc định chỉ phía mình (`only_me: true`).
  Cần thêm `uid_from` (người gửi tin đó).
- `forward_message` — chuyển tiếp nội dung tới nhiều nơi:
  `thread_ids: "id1,id2"`, cùng một `type` cho tất cả.

### Nhóm, bình chọn, nhắc hẹn

```yaml
# Tạo bình chọn trong nhóm
action: zalo_bot.create_poll
data:
  account_selection: "84901234567"
  group_id: "5841349563795164131"
  question: "Tối nay ăn gì?"
  options: "Phở,Bún chả,Cơm nhà"
  allow_multi_choices: false
```

```yaml
# Nhắc hẹn lúc 20:00 hôm nay. remind_time là mốc thời gian tính bằng MILI GIÂY.
action: zalo_bot.create_reminder
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "1"
  title: "Đổ rác"
  content: "Xe rác qua lúc 20:30"
  remind_time: "{{ (as_timestamp(today_at('20:00')) * 1000) | int }}"
```

- `get_all_groups` trả **ID** các nhóm; tên và thành viên lấy bằng
  `get_group_info` (nhiều ID cách nhau dấu phẩy).
- `get_group_chat_history` lấy tối đa 1000 tin gần nhất của nhóm (`count`).
- Các thao tác đổi quyền (`change_group_owner`, `disperse_group`,
  `remove_user_from_group`…) cần tài khoản bot là trưởng/phó nhóm.

### Bảng tra cứu đủ 96 dịch vụ

Sinh từ `services.yaml` và schema của tích hợp. Cột **Cần điền** là thứ phải có
để gọi thành công; `type` ở đâu cũng nhận `0`/`user` hoặc `1`/`group`.

#### Gửi tin

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.send_message` | Gửi tin nhắn Zalo | `message`, `thread_id`, `account_selection` | `type`, `ttl`, `quote` |
| `zalo_bot.send_image` | Gửi ảnh Zalo | `image_path`, `thread_id`, `account_selection` | `message`, `type`, `ttl` |
| `zalo_bot.send_file` | Gửi một file bất kỳ qua URL hoặc từ đường dẫn cục bộ | `file_path_or_url`, `thread_id`, `account_selection` | `message`, `type`, `ttl` |
| `zalo_bot.send_video` | Gửi video qua URL hoặc từ đường dẫn cục bộ | `thread_id`, `video_path_or_url`, `account_selection` | `thumbnail_url`, `message`, `width`, `height`, `ttl`, `type` |
| `zalo_bot.send_voice` | Gửi tin nhắn thoại | `voice_path`, `thread_id`, `account_selection` | `type` |
| `zalo_bot.send_sticker` | Gửi sticker | `sticker_id`, `thread_id`, `account_selection` | `type` |
| `zalo_bot.send_link` | Gửi một tin nhắn chứa liên kết có preview | `thread_id`, `link`, `account_selection` | `message`, `thumbnail`, `type` |
| `zalo_bot.send_card` | Gửi danh thiếp của một người dùng | `thread_id`, `user_id`, `account_selection` | `type` |
| `zalo_bot.send_image_to_user` | Gửi 1 ảnh đến user | `image_path`, `thread_id`, `account_selection` | — |
| `zalo_bot.send_images_to_user` | Gửi nhiều ảnh đến user | `image_paths`, `thread_id`, `account_selection` | — |
| `zalo_bot.send_image_to_group` | Gửi 1 ảnh đến group | `image_path`, `thread_id`, `account_selection` | — |
| `zalo_bot.send_images_to_group` | Gửi nhiều ảnh đến group | `image_paths`, `thread_id`, `account_selection` | — |
| `zalo_bot.forward_message` | Chuyển tiếp một tin nhắn | `message`, `thread_ids`, `account_selection` | `type` |
| `zalo_bot.send_typing_event` | Gửi thông báo đang soạn tin nhắn | `thread_id`, `account_selection` | — |

#### Thao tác trên tin đã có

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.add_reaction` | Thả cảm xúc vào một tin nhắn | `icon` (`like` · `heart` · `haha` · `wow` · `cry` · `angry` · `kiss` · `tears_of_joy` · `shit` · `rose` · `broken_heart` · `dislike` · `love` · `confused` · `wink` · `fade` · `sun` · `birthday` · `bomb` · `ok` · `peace` · `thanks` · `punch` · `share` · `pray` · `no` · `bad` · `love_you` · `sad`), `thread_id`, `msg_id`, `cli_msg_id`, `type`, `account_selection` | — |
| `zalo_bot.undo_message` | Thu hồi tin nhắn đã gửi | `msg_id`, `thread_id`, `account_selection` | `cli_msg_id`, `type` |
| `zalo_bot.delete_message` | Xóa một tin nhắn (chỉ ở phía mình) | `thread_id`, `msg_id`, `cli_msg_id`, `uid_from`, `type`, `account_selection` | `only_me` (true/false) |
| `zalo_bot.parse_link` | Phân tích link để lấy thông tin preview | `link`, `account_selection` | — |
| `zalo_bot.get_stickers` | Tìm kiếm sticker theo từ khóa | `query`, `account_selection` | — |
| `zalo_bot.get_stickers_detail` | Lấy thông tin chi tiết của một bộ sticker | `sticker_album`, `account_selection` | — |

#### Nhóm

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.get_all_groups` | Lấy danh sách tất cả nhóm đã tham gia | `account_selection` | — |
| `zalo_bot.get_group_info` | Lấy info group | `group_id`, `account_selection` | — |
| `zalo_bot.get_group_chat_history` | Lấy lịch sử tin nhắn của một nhóm | `group_id`, `account_selection` | `count` |
| `zalo_bot.create_group` | Tạo group mới | `members`, `account_selection` | `name`, `avatar_path` |
| `zalo_bot.add_user_to_group` | Thêm thành viên vào group | `group_id`, `member_id`, `account_selection` | — |
| `zalo_bot.remove_user_from_group` | Xóa thành viên khỏi group | `group_id`, `member_id`, `account_selection` | — |
| `zalo_bot.change_group_name` | Đổi tên nhóm | `group_id`, `name`, `account_selection` | — |
| `zalo_bot.change_group_avatar` | Đổi ảnh đại diện nhóm | `group_id`, `image_path`, `account_selection` | — |
| `zalo_bot.add_group_deputy` | Thêm phó nhóm | `group_id`, `member_id`, `account_selection` | — |
| `zalo_bot.remove_group_deputy` | Xóa phó nhóm | `group_id`, `member_id`, `account_selection` | — |
| `zalo_bot.change_group_owner` | Chuyển quyền sở hữu nhóm | `group_id`, `member_id`, `account_selection` | — |
| `zalo_bot.enable_group_link` | Kích hoạt và lấy link tham gia nhóm | `group_id`, `account_selection` | — |
| `zalo_bot.disable_group_link` | Vô hiệu hóa link tham gia nhóm | `group_id`, `account_selection` | — |
| `zalo_bot.join_group` | Tham gia nhóm bằng link mời | `link`, `account_selection` | — |
| `zalo_bot.leave_group` | Rời khỏi nhóm | `group_id`, `account_selection` | `silent` (true/false) |
| `zalo_bot.disperse_group` | Giải tán nhóm | `group_id`, `account_selection` | — |

#### Ghi chú và bình chọn trong nhóm

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.create_note_group` | Tạo ghi chú mới trong nhóm | `group_id`, `title`, `account_selection` | `pin_act` (true/false) |
| `zalo_bot.edit_note_group` | Chỉnh sửa ghi chú trong nhóm | `group_id`, `topic_id`, `title`, `account_selection` | — |
| `zalo_bot.get_list_board` | Lấy danh sách các mục trên bảng tin của nhóm | `group_id`, `account_selection` | — |
| `zalo_bot.create_poll` | Tạo một cuộc bình chọn trong nhóm | `group_id`, `question`, `options`, `account_selection` | `allow_multi_choices` (true/false) |
| `zalo_bot.get_poll_detail` | Lấy thông tin chi tiết của một cuộc bình chọn | `poll_id`, `account_selection` | — |
| `zalo_bot.lock_poll` | Khóa một cuộc bình chọn | `poll_id`, `account_selection` | — |

#### Nhắc hẹn

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.create_reminder` | Tạo nhắc nhở mới | `title`, `content`, `remind_time`, `thread_id`, `account_selection` | `type` |
| `zalo_bot.edit_reminder` | Chỉnh sửa một nhắc hẹn | `thread_id`, `topic_id`, `title`, `account_selection` | — |
| `zalo_bot.remove_reminder` | Xóa nhắc nhở | `reminder_id`, `thread_id`, `account_selection` | `type` |
| `zalo_bot.get_reminder` | Lấy thông tin chi tiết của một nhắc hẹn | `reminder_id`, `account_selection` | — |
| `zalo_bot.get_list_reminder` | Lấy danh sách các nhắc hẹn trong một cuộc trò chuyện | `thread_id`, `account_selection` | `type` |
| `zalo_bot.get_reminder_responses` | Lấy danh sách phản hồi cho một nhắc hẹn | `reminder_id`, `account_selection` | — |

#### Bạn bè và người dùng

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.find_user` | Tìm user bằng số điện thoại | `phone`, `account_selection` | — |
| `zalo_bot.get_user_info` | Lấy thông tin user | `user_id`, `account_selection` | — |
| `zalo_bot.last_online` | Xem thời gian hoạt động cuối cùng của một người dùng | `user_id`, `account_selection` | — |
| `zalo_bot.get_all_friends` | Lấy danh sách tất cả bạn bè | `account_selection` | — |
| `zalo_bot.send_friend_request` | Gửi lời mời kết bạn | `user_id`, `account_selection` | `message` |
| `zalo_bot.accept_friend_request` | Chấp nhận lời mời kết bạn từ một người dùng | `user_id`, `account_selection` | — |
| `zalo_bot.get_sent_friend_requests` | Lấy danh sách lời mời kết bạn đã gửi | `account_selection` | — |
| `zalo_bot.undo_friend_request` | Thu hồi lời mời kết bạn đã gửi | `friend_id`, `account_selection` | — |
| `zalo_bot.remove_friend` | Hủy kết bạn với một người dùng | `friend_id`, `account_selection` | — |
| `zalo_bot.change_friend_alias` | Thay đổi biệt danh của một người bạn | `friend_id`, `alias`, `account_selection` | — |
| `zalo_bot.remove_friend_alias` | Xóa biệt danh của một người bạn | `friend_id`, `account_selection` | — |
| `zalo_bot.block_user` | Chặn một người dùng | `user_id`, `account_selection` | — |
| `zalo_bot.unblock_user` | Bỏ chặn một người dùng | `user_id`, `account_selection` | — |
| `zalo_bot.block_view_feed` | Chặn/bỏ chặn một người bạn xem nhật ký | `user_id`, `is_block_feed` (true/false), `account_selection` | — |

#### Cuộc trò chuyện

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.set_mute` | Tắt thông báo cho cuộc trò chuyện | `thread_id`, `duration` (`3600` · `14400` · `-1` · `0`), `account_selection` | `type` |
| `zalo_bot.get_mute` | Lấy danh sách các cuộc trò chuyện đang bị tắt thông báo | `account_selection` | — |
| `zalo_bot.set_pinned_conversation` | Ghim hoặc bỏ ghim cuộc trò chuyện | `thread_id`, `pinned` (true/false), `account_selection` | `type` |
| `zalo_bot.get_pin_conversations` | Lấy danh sách các cuộc trò chuyện đã được ghim | `account_selection` | — |
| `zalo_bot.add_unread_mark` | Đánh dấu một cuộc trò chuyện là chưa đọc | `thread_id`, `account_selection` | — |
| `zalo_bot.remove_unread_mark` | Bỏ đánh dấu chưa đọc cho một cuộc trò chuyện | `thread_id`, `account_selection` | — |
| `zalo_bot.get_unread_mark` | Lấy danh sách các cuộc trò chuyện được đánh dấu là chưa đọc | `account_selection` | — |
| `zalo_bot.delete_chat` | Xóa một cuộc trò chuyện khỏi danh sách | `thread_id`, `account_selection` | — |
| `zalo_bot.get_archived_chat_list` | Lấy danh sách các cuộc trò chuyện đã được lưu trữ | `account_selection` | — |
| `zalo_bot.update_auto_delete_chat` | Bật/tắt chế độ tự động xóa tin nhắn | `thread_id`, `ttl` (`0` · `86400000` · `604800000`), `account_selection` | — |
| `zalo_bot.get_auto_delete_chat` | Lấy danh sách các cuộc trò chuyện đang bật tự động xóa tin nhắn | `account_selection` | — |
| `zalo_bot.set_hidden_conversations` | Ẩn hoặc bỏ ẩn một cuộc trò chuyện | `thread_id`, `hidden` (true/false), `account_selection` | — |
| `zalo_bot.get_hidden_conversations` | Lấy danh sách các cuộc trò chuyện đang bị ẩn bằng mã PIN | `account_selection` | — |
| `zalo_bot.update_hidden_convers_pin` | Đặt hoặc thay đổi mã PIN cho các cuộc trò chuyện ẩn | `pin`, `account_selection` | — |
| `zalo_bot.reset_hidden_convers_pin` | Gỡ bỏ mã PIN cho các cuộc trò chuyện ẩn | `account_selection` | — |

#### Tin nhắn nhanh và nhãn

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.add_quick_message` | Thêm một tin nhắn nhanh mới | `keyword`, `title`, `account_selection` | — |
| `zalo_bot.get_quick_message` | Lấy danh sách tin nhắn nhanh | `account_selection` | — |
| `zalo_bot.update_quick_message` | Cập nhật tin nhắn nhanh | `item_id`, `keyword`, `title`, `account_selection` | — |
| `zalo_bot.remove_quick_message` | Xóa tin nhắn nhanh | `item_ids`, `account_selection` | — |
| `zalo_bot.get_labels` | Lấy danh sách các nhãn | `account_selection` | — |

#### Tài khoản bot

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.get_logged_accounts` | Lấy danh sách tài khoản Zalo đã login | — | — |
| `zalo_bot.get_account_details` | Lấy chi tiết một tài khoản Zalo | `own_id` | — |
| `zalo_bot.update_profile` | Cập nhật thông tin cá nhân | `account_selection` | `name`, `dob`, `gender` (`0` · `1`) |
| `zalo_bot.update_settings` | Cập nhật cài đặt riêng tư | `setting_type` (`online_status` · `seen_status` · `receive_message` · `phone_search`), `status` (`1` · `0`), `account_selection` | — |
| `zalo_bot.change_account_avatar` | Thay đổi ảnh đại diện | `avatar_source`, `account_selection` | — |
| `zalo_bot.get_avatar_list` | Lấy danh sách các ảnh đại diện đã sử dụng | `account_selection` | `count`, `page` |
| `zalo_bot.get_login_qr` | Lấy mã QR đăng nhập Zalo từ server và hiển thị lên thông báo | — | — |

#### Quản trị gateway (webhook, proxy)

| Dịch vụ | Việc | Cần điền | Tuỳ chọn |
|---|---|---|---|
| `zalo_bot.get_account_webhooks` | Lấy tất cả config webhook | — | — |
| `zalo_bot.get_account_webhook` | Lấy config webhook cho account | `own_id` | — |
| `zalo_bot.set_account_webhook` | Cập nhật config webhook | `own_id` | `message_webhook_url`, `group_event_webhook_url`, `reaction_webhook_url` |
| `zalo_bot.delete_account_webhook` | Xóa config webhook | `own_id` | — |
| `zalo_bot.get_proxies` | Lấy danh sách proxy | — | — |
| `zalo_bot.add_proxy` | Thêm proxy mới | `proxy_url` | — |
| `zalo_bot.remove_proxy` | Xóa proxy | `proxy_url` | — |

## Định dạng chữ: đậm, nghiêng, màu, cỡ

Zalo cá nhân không hiểu markdown. Tích hợp này nhận markdown quen thuộc rồi tự
quy ra mã style của Zalo, nên trong automation bạn cứ viết bình thường.

### Bật và chọn màu

Sau khi cài, thiết bị **Zalo Bot** có hai thực thể điều khiển việc này:

| Thực thể | Việc |
|---|---|
| Công tắc **Markdown** | Bật/tắt toàn bộ. Tắt thì tin gửi đi nguyên văn, kể cả dấu `**`. |
| Ô chọn **Markdown Color** | `none` · `red` · `orange` · `yellow` · `green` |

Cả hai nhớ lựa chọn qua lần khởi động lại Home Assistant.

**Màu chỉ áp cho phần in đậm.** Chọn `red` thì `**29°C**` ra đỏ và đậm; phần
nghiêng hay gạch chân vẫn màu thường. Đây là chủ ý — tô màu mọi thứ thì tin nhắn
rối và khó đọc.

### Cú pháp nhận được

| Viết | Ra |
|---|---|
| `**chữ**` | đậm |
| `*chữ*` | nghiêng |
| `***chữ***` | đậm + nghiêng |
| `~~chữ~~` | gạch ngang |
| `__chữ__` | gạch chân |
| `` `chữ` `` | nghiêng (Zalo không có kiểu chữ máy) |
| `> chữ` | nghiêng |
| `# Tiêu đề` · `## Mục` | to + đậm |
| `### Mục nhỏ` | đậm |
| `#### …` tới `###### …` | chữ nhỏ |
| `[chữ](https://…)` | giữ chữ, bỏ cú pháp link |

**Zalo chỉ có hai cỡ chữ**, to và nhỏ. Nên `#` và `##` cho ra kết quả giống
nhau, `####` tới `######` cũng vậy. Không có cỡ nào lớn hơn `##`.

Emoji đếm là hai đơn vị trong cách Zalo đánh dấu khoảng chữ; tích hợp đã quy đổi
sẵn nên bạn đặt emoji ở đâu cũng không làm lệch phần in đậm.

### Ví dụ

```yaml
action: zalo_bot.send_message
data:
  account_selection: "84901234567"
  thread_id: "5841349563795164131"
  type: "0"
  message: |
    # Báo động
    Nhiệt độ phòng khách **29°C** — vượt ngưỡng *27°C*.
    > Điều hoà đã tự bật.
```

### Tích hợp không tự tô đậm giúp bạn

Nó chỉ dịch những gì bạn đã viết. Muốn bot **tự** nhận ra số liệu rồi tô đậm —
"Nhiệt độ: 29°C" tự đậm phần `29°C` mà không cần gõ `**` — thì đó là việc của
gateway `chatgpt2api`, không phải của tích hợp này.

## Thực thể tích hợp tạo ra

Tất cả nằm dưới một thiết bị tên **Zalo Bot**.

| Thực thể | Kiểu | Cho biết gì |
|---|---|---|
| **Zalo Server** | binary_sensor | Máy chủ gateway **còn sống** không. Bật nghĩa là gọi được, kể cả khi mật khẩu sai. |
| **Zalo Login** | binary_sensor | Đã có tài khoản Zalo nào **đăng nhập** chưa. Thuộc tính kèm theo: `total_accounts`, `accounts`. |
| **Markdown** | switch | Bật/tắt dịch markdown sang định dạng Zalo |
| **Markdown Color** | select | Màu cho phần in đậm |
| **Thông báo** | switch | Hiện kết quả mỗi lần gọi service dưới dạng thông báo trong HA |

Hai cảm biến cập nhật **mỗi 60 giây**.

> Từ **2026.8.23.3** trở đi, "Zalo Server" báo đúng trạng thái máy chủ. Bản
> trước nó báo trạng thái *đăng nhập*, nên máy chủ đang chạy mà sai mật khẩu thì
> nó vẫn tắt — automation nào dựa vào nó để biết máy chủ còn sống sẽ bị đánh
> lừa. Nếu bạn đang có automation dùng thực thể này, kiểm lại xem nó cần "máy
> chủ sống" hay "đã đăng nhập".

## Khắc phục lỗi thường gặp

- **`Detected blocking call to open ... manifest.json`**: custom integration
  đang cũ. Cập nhật qua HACS rồi khởi động lại Home Assistant. Bản mới lấy
  version từ cache của Home Assistant, không mở file trong event loop.
- **Gateway phản hồi chậm, thỉnh thoảng bỏ lỡ tin Zalo**: cập nhật **cả hai**
  phần lên 2026.8.23 trở lên. Bản cũ đăng nhập lại trước mỗi lượt gọi service và
  thêm một lần mỗi 60 giây; mỗi lần đăng nhập làm gateway đứng hình 3,4 giây
  trên máy ARM.
- **Cảnh báo `Đăng nhập máy chủ Zalo thất bại`**: mật khẩu trong cấu hình không
  còn khớp. Lấy lại từ `THONG-TIN-DANG-NHAP.txt` trong thư mục dữ liệu của
  add-on, rồi sửa trong **Cài đặt → Thiết bị & Dịch vụ → Zalo Bot → Cấu hình**.
- **Đăng nhập bị từ chối liên tục dù mật khẩu đúng**: gõ sai quá 10 lần trong 15
  phút thì máy chủ khoá IP. Chờ 15 phút.
- **`# Tiêu đề` không to hơn `## Mục`**: đúng như vậy — Zalo chỉ có hai cỡ chữ.
  Xem mục Định dạng chữ ở trên.
- **Không kết nối được gateway**: từ Home Assistant kiểm tra
  `http://<ip-may-gateway>:3000/admin-login` trả HTTP `200`, sau đó kiểm tra
  username/password. Đừng mở cổng 3000 trực tiếp ra Internet.
- **Upload album trả `413`**: giảm xuống tối đa 24 ảnh và tổng 100 MB mỗi
  request. Đây là giới hạn bảo vệ RAM/ổ đĩa của gateway.

## Tính năng

### Tính năng cơ bản
- Nhận thông báo từ Home Assistant qua Zalo
- Gửi tin nhắn văn bản đến người dùng hoặc nhóm
- Gửi hình ảnh, file, sticker, video, tin nhắn thoại
- Điều khiển thiết bị Home Assistant bằng tin nhắn Zalo
- Tự động phản hồi tin nhắn thông qua tích hợp với các dịch vụ AI

### Quản lý tin nhắn
- Thêm, xem, cập nhật và xóa tin nhắn nhanh (Quick Message)
- Thả cảm xúc vào tin nhắn (like, heart, haha, wow, cry, angry và nhiều loại khác)
- Thu hồi tin nhắn đã gửi
- Xóa tin nhắn (chỉ ở phía mình hoặc với tất cả)
- Chuyển tiếp tin nhắn đến nhiều người dùng hoặc nhóm cùng lúc
- Gửi liên kết với preview tự động
- Gửi danh thiếp người dùng
- Gửi tin nhắn có định dạng (in đậm, in nghiêng)
- Trả lời/trích dẫn tin nhắn
- Gửi sự kiện "đang gõ", "đã nhận", "đã xem" tin nhắn

### Quản lý nhóm
- Tạo nhóm mới với nhiều thành viên
- Thêm/xóa thành viên khỏi nhóm
- Thay đổi tên nhóm và ảnh đại diện
- Thêm/xóa phó nhóm
- Chuyển quyền sở hữu nhóm
- Giải tán nhóm
- Bật/tắt liên kết tham gia nhóm
- Tham gia nhóm qua link mời
- Rời khỏi nhóm (im lặng hoặc thông báo)
- Cài đặt nhóm nâng cao (chặn thay đổi tên/ảnh, chặn tạo bình chọn/ghi chú/nhắc hẹn, chặn gửi tin nhắn)
- Xem thông tin chi tiết của nhóm và thành viên

### Quản lý liên hệ
- Tìm kiếm người dùng qua số điện thoại
- Lấy thông tin chi tiết người dùng
- Gửi/chấp nhận/thu hồi lời mời kết bạn
- Chặn/bỏ chặn người dùng
- Hủy kết bạn
- Thay đổi/xóa biệt danh của bạn bè
- Chặn/bỏ chặn xem nhật ký
- Lấy danh sách tất cả bạn bè
- Lấy danh sách lời mời kết bạn đã nhận/đã gửi
- Lấy danh sách biệt danh đã đặt

### Tính năng tiện ích nhóm
- Tạo và quản lý ghi chú nhóm (thêm, sửa, ghim)
- Tạo và quản lý bình chọn trong nhóm (tạo, xem chi tiết, khóa)
- Tạo, chỉnh sửa, xóa và quản lý nhắc hẹn
- Xem phản hồi cho nhắc hẹn (tham gia/từ chối)
- Lấy danh sách các mục trên bảng tin của nhóm

### Quản lý cuộc trò chuyện
- Tắt/bật thông báo cho cuộc trò chuyện (1 giờ, 4 giờ hoặc vĩnh viễn)
- Ghim/bỏ ghim cuộc trò chuyện
- Đánh dấu/bỏ đánh dấu chưa đọc
- Xóa cuộc trò chuyện
- Lấy danh sách cuộc trò chuyện đã lưu trữ
- Bật/tắt tự động xóa tin nhắn (1 ngày, 7 ngày)
- Ẩn/hiện cuộc trò chuyện bằng mã PIN
- Đặt/thay đổi/xóa mã PIN cho cuộc trò chuyện ẩn
- Lấy danh sách cuộc trò chuyện đã ghim, đã tắt thông báo, đã đánh dấu chưa đọc

### Tùy chỉnh tài khoản
- Cập nhật thông tin cá nhân (tên, ngày sinh, giới tính)
- Cập nhật cài đặt riêng tư (trạng thái online, trạng thái đã xem, nhận tin nhắn, tìm kiếm bằng SĐT)
- Thay đổi ảnh đại diện (tải lên mới hoặc dùng lại ảnh cũ)
- Lấy danh sách ảnh đại diện đã sử dụng
- Xóa ảnh đại diện khỏi album
- Xem thời gian hoạt động cuối của người dùng
- Thay đổi ngôn ngữ

### Tính năng quản trị
- Quản lý webhook cho tài khoản (thêm, xem, cập nhật, xóa)
- Quản lý proxy (thêm, xóa, xem danh sách)
- Báo cáo người dùng vi phạm (nhạy cảm, làm phiền, lừa đảo)

### Tính năng nhãn (Label)
- Lấy danh sách các nhãn
- Cập nhật danh sách nhãn (thêm/xóa/sửa nhãn)
- Thêm/xóa cuộc trò chuyện khỏi nhãn

---

## Có gì mới ở 2026.9.25

- **`type` thống nhất ở mọi dịch vụ.** Trước đây nửa số dịch vụ đòi `"0"`/`"1"`,
  nửa kia đòi `"user"`/`"group"`, và viết nhầm kiểu thì tin lặng lẽ đi vào chat
  riêng thay vì nhóm. Nay dịch vụ nào cũng nhận cả hai cách; giá trị lạ bị từ
  chối ngay khi gọi.
- **Sáu dịch vụ không gọi được đúng như giao diện hướng dẫn.** `set_mute`,
  `set_pinned_conversation`, `forward_message`, `get_list_reminder` (trường
  `type`), `undo_message` (trường `cli_msg_id`) và `get_avatar_list` (`count`,
  `page`) bị Home Assistant báo `extra keys not allowed` vì schema thiếu trường
  mà `services.yaml` bắt điền. Đã bổ sung.
- **`send_voice` gửi được vào nhóm.** Bản cũ bỏ mất `type` nên tin thoại gửi
  vào nhóm thành gửi cho "người" có ID nhóm.
- **`send_link`, `send_card` có `type`** để gửi vào nhóm; bản cũ chỉ chat riêng.
- **Nhắc hẹn chat riêng** (`create_reminder`/`remove_reminder` với `type: "0"`):
  bản cũ gửi `type` dạng chữ, gateway so với số nên đi nhầm nhánh nhóm.
- README có thêm mục **Hướng dẫn gọi dịch vụ (đầy đủ)**.

## Có gì mới ở 2026.8.23

- **Không đăng nhập lại ở mỗi lượt gọi nữa.** Tích hợp giữ phiên 6 tiếng, chỉ
  đăng nhập lại khi hết hạn hoặc khi máy chủ trả 401. Cảm biến hỏi
  `/api/check-auth` trước thay vì đăng nhập mù mỗi phút.
- **Mọi lời gọi HTTP có hạn chờ.** Trước đây 98 trên 99 lời gọi chờ vô hạn; máy
  chủ treo là chiếm luôn thread của Home Assistant.
- **Cảm biến "Zalo Server" báo đúng trạng thái máy chủ**, không phải trạng thái
  đăng nhập.
- **Thông báo thôi chồng chất.** Mỗi dịch vụ giữ đúng một thông báo, luôn hiện
  kết quả gần nhất. Bản cũ đẻ thông báo mới mỗi lần gọi — một automation chạy
  mỗi phút chất 1.440 cái mỗi ngày.
- **Config flow kiểm tra kết nối** và chuẩn hoá địa chỉ máy chủ; thêm tiếng Việt
  và tiếng Anh cho khung cấu hình.
- **`# Tiêu đề` dùng đúng mã cỡ chữ Zalo hiểu.** Trước đây nó gửi `f_20` — mã
  Zalo không biết — nên tiêu đề chỉ ra đậm chứ không to hơn.
- Đóng phiên HTTP khi gỡ tích hợp; bỏ 18 tệp `.pyc` khỏi repo.

## Đóng góp
Mọi đóng góp, báo lỗi hoặc ý tưởng mới đều được hoan nghênh qua GitHub Issues hoặc Pull Request.

---

**Chúc bạn trải nghiệm vui vẻ với Zalo Bot cho Home Assistant!**
