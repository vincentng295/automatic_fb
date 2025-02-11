# Automatic Facebook Python  

**Automatic Facebook Python** là một dự án Python giúp tự động hóa các tác vụ liên quan đến Facebook, sử dụng các thư viện và API hiện đại.  

---

## 🚀 Tính năng hiện tại  

- **AI trả lời tin nhắn**: Tự động phản hồi tin nhắn Messenger bằng Google Generative AI (Gemini).  
- **Tự động chấp nhận kết bạn**: Xử lý tự động lời mời kết bạn trên Facebook.  
- **Tự động làm nhiệm vụ**: Tương tác với [traodoisub.com](https://traodoisub.com) để tự động hoàn thành nhiệm vụ.  

---

## ⚙️ Cách sử dụng và Thiết lập

> Lưu ý: Hiện chỉ hỗ trợ tài khoản Facebook ngôn ngữ Tiếng Việt

- Bạn không cần phải fork hay clone toàn bộ repo, bạn chỉ cần một repo trống với file [.github/workflows/aichat-schedule.yml](.github/workflows/aichat-schedule.yml) hoặc [.github/workflows/traodoisub.yml](.github/workflows/traodoisub.yml) để chạy github workflows
- Vào **Settings** > **Actions** > **General**, ở mục ***Workflow permissions*** chọn *Read and write permissions*

### Secrets

Để chạy workflows `aichat-schedule` và `traodoisub`, bạn cần thiết lập các secrets:  

- **`PASSWORD`**: Mật khẩu để giải mã các tệp zip trong thư mục `secrets`.
- **`GENKEY`**: Google Developer API key để sử dụng Gemini AI.  (cho `aichat-schedule`)
- **`TDS_TOKEN`**: Token dùng API của `traodoisub.com`. (cho `traodoisub`)

---

### AI Chatbot trên FB

- Lần đầu tiên, bạn cần chạy workflow `Run AI Chat on Messenger Account` để đăng nhập Facebook và sao lưu cookies vào nhánh `caches/schedule`.
- Cookies và các file liên quan sẽ được mã hóa bằng mật khẩu của bạn (`PASSWORD` secret) để không ai có thể truy cập tài khoản Facebook của bạn thông qua việc sử dụng cookies.
- Khi thay đổi tài khoản Facebook, hãy xóa nhánh `cache/schedule` rồi chạy lại workflow `Run AI Chat on Messenger Account`

---

### Auto Traodoisub 

Cấu trúc json mẫu:

```json
[
    {
        "username": "facebook_number_or_email_1",
        "password": "facebook_password_1",
        "otp_sec": "PYOTP_TOKEN_SECRET_CODE_1",
        "alt": "0",
        "cookies" : [{"name" : "c_user", "value" : "123456789012345", ... }, ...] or strings pair "c_user=123456789012345;name=val2;..."
    },
    {
        "username": "facebook_number_or_email_2",
        "password": "facebook_password_2",
        "otp_sec": "PYOTP_TOKEN_SECRET_CODE_2",
        "alt": "1",
        "cookies" :  [{"name" : "c_user", "value" : "123456789012345", ... }, ...] or strings pair "c_user=123456789012345;name=val2;..."
    }
]
```

## 📌 Lưu ý

Bảo mật: Đảm bảo tất cả các tệp và thông tin trong thư mục secrets được bảo vệ nghiêm ngặt.

