# Zalo Bot cho Home Assistant

## Giới thiệu

Dự án này cung cấp một bot Zalo tích hợp cho Home Assistant, giúp bạn gửi, nhận thông báo và điều khiển thiết bị qua Zalo một cách tiện lợi.

## Tính năng
- Nhận thông báo từ Home Assistant qua Zalo
- Điều khiển thiết bị Home Assistant bằng tin nhắn Zalo
- Yêu cầu đã cài đặt Addon Zalo Bot

## Hướng dẫn cài đặt

### 1. Thêm repo vào HACS

Vào HACS > Integrations > Ba chấm góc phải > Custom repositories, thêm đường dẫn repo:
```
https://github.com/smarthomeblack/zalo_bot
```
Chọn loại: Integration.

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/1.png" width="100%"></img>

### 2. Cài đặt và cấu hình bộ tích hợp

- Sau khi thêm repo, tìm kiếm "Zalo Bot" trong HACS và cài đặt rồi khởi động lại Hass.

- Vào Cài đặt > Thiết bị & Dịch vụ > Thêm tích hợp mới > Chọn "Zalo Bot" và cấu hình theo hướng dẫn.

<img title="Zalo Bot" src="https://raw.githubusercontent.com/smarthomeblack/zalo_bot/refs/heads/main/img/2.png" width="100%"></img>

### 3. Cài đặt thủ công

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
    local_only: true
    webhook_id: "-kckRb3xuIlUYoMHgbwIwPMKq"
    trigger: webhook
conditions:
  - condition: template
    value_template: >
      {{ '@TenZaloBot' in trigger.json.data.content and trigger.json.data.dName ==
      'TenZaloBan' }}
actions:
  - variables:
      user_message: "{{ trigger.json.data.content }}"
  - data:
      text: "{{ user_message }}"
      agent_id: conversation.google_generative_ai_2
    response_variable: convo_response
    action: conversation.process
  - data:
      message: "{{ convo_response.response.speech.plain.speech }}"
      thread_id: "Id hội thoại"
      account_selection: "SĐT của Bot"
      type: 1
    action: zalo_bot.send_message
mode: single
```

## Đóng góp
Mọi đóng góp, báo lỗi hoặc ý tưởng mới đều được hoan nghênh qua GitHub Issues hoặc Pull Request.

---

**Chúc bạn trải nghiệm vui vẻ với Zalo Bot cho Home Assistant!**
