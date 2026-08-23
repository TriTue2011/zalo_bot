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

- Custom integration hiện tại: **2026.8.23.4**.
- Add-on/gateway tương thích: **2026.8.23.3** hoặc mới hơn.

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

Địa chỉ máy chủ được chuẩn hoá tự động: gõ `172.16.10.28:3000` hay
`http://172.16.10.28:3000/` đều được.

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
- Có 2 dịch vụ chính để dùng tự động hóa là zalo_bot.send_image và zalo_bot.send_message
- Vào trang quản lý ZALO BOT, Chọn Theo dõi tin nhắn và lấy Thread ID 
- Sau đó dùng tài khoản bất kỳ gửi tin nhắn cho Acc Bot hoặc thêm Acc bot vào trong 1 nhóm, sau đó gửi tin nhắn từ tài khoản chính vào nhóm
- Dùng Thread ID để điền vào cấu hình tự động hóa, như gửi ảnh, gửi tin nhắn
- Nếu gửi cho tài khoản cá nhân, đặt `type: "0"`; gửi vào nhóm đặt `type: "1"`.

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
  account_selection: "{{ states('sensor.zalo_account') }}"
  thread_id: "zalo:1234567890123456789"
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
