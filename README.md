## ❓ Nhóm Support:
- Zalo: https://zalo.me/g/alvkgn274
- Telegram: https://t.me/smarthomeblack

---

# Zalo Bot cho Home Assistant

## Giới thiệu

Dự án này cung cấp một bot Zalo tích hợp cho Home Assistant, giúp bạn gửi, nhận thông báo và điều khiển thiết bị qua Zalo một cách tiện lợi!


## Hướng dẫn cài đặt

### 1. Cài đặt qua HACS(Khuyến nghị)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=smarthomeblack&repository=zalo_bot)

- Tải về sau đó khởi động lại Home Assistant

### 2. Cài đặt thủ công

Nếu không sử dụng HACS, bạn có thể cài đặt thủ công như sau:

- Tải mã nguồn repo này về máy.
- Sao chép thư mục `custom_components/zalo_bot` vào thư mục `custom_components` trong thư mục cấu hình Home Assistant của bạn.
- Khởi động lại Home Assistant.
- Vào Cài đặt > Thiết bị & Dịch vụ > Thêm tích hợp mới > Chọn "Zalo Bot" và cấu hình theo hướng dẫn.

### 3. Cấu hình

- Nếu cài Server Zalo Bot bằng Addon thì mặc định zalo_server để nguyên
- user và pass điền admin

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/3.png" width="100%"></img>

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/4.png" width="100%"></img>

 - Nếu kết nối thành công và đăng nhập zalo bot thành công thì sẽ có cảm biến báo đã kết nối, các cảm biến sẽ cập nhập 1 phút 1 lần để cho biết trạng thái đăng nhập Zalo bot, có thể tạo tự động hóa để thông báo nếu như zalo bot bị đăng xuất hoặc cần đăng nhập lại, 

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/8.png" width="100%"></img>

### 4. Hướng Dẫn Sử Dụng
- Có 2 dịch vụ chính để dùng tự động hóa là zalo_bot.send_image và zalo_bot.send_message
- Vào trang quản lý ZALO BOT, Chọn Theo dõi tin nhắn và lấy Thread ID 
- Sau đó dùng tài khoản bất kỳ gửi tin nhắn cho Acc Bot hoặc thêm Acc bot vào trong 1 nhóm, sau đó gửi tin nhắn từ tài khoản chính vào nhóm
- Dùng Thread ID để điền vào cấu hình tự động hóa, như gửi ảnh, gửi tin nhắn
- Nếu gửi cho tài khoản cá nhân thì type để user, còn gửi vào trong nhóm thì type để Group

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/5.png" width="100%"></img>

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

## Đóng góp
Mọi đóng góp, báo lỗi hoặc ý tưởng mới đều được hoan nghênh qua GitHub Issues hoặc Pull Request.

---

**Chúc bạn trải nghiệm vui vẻ với Zalo Bot cho Home Assistant!**
