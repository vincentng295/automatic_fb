# Automatic Facebook Python  

**Automatic Facebook Python** là một dự án Python giúp tự động hóa các tác vụ liên quan đến Facebook, sử dụng các thư viện và API hiện đại.  

---

## 🚀 Tính năng hiện tại  

- **AI trả lời tin nhắn**: Tự động phản hồi tin nhắn Messenger bằng Google Generative AI (Gemini).  
- **Tự động chấp nhận kết bạn**: Xử lý tự động lời mời kết bạn trên Facebook.  
- **Tự động làm nhiệm vụ**: Tương tác với [traodoisub.com](https://traodoisub.com) để tự động hoàn thành nhiệm vụ.  

---

## ⚙️ Thiết lập

### Secrets

Để chạy workflows `aichat-schedule` và `traodoisub`, bạn cần thiết lập các secrets:  

- **`PASSWORD`**: Mật khẩu để giải mã các tệp zip trong thư mục `secrets`.
- **`GENKEY`**: Google Developer API key để sử dụng Gemini AI.  (cho `aichat-schedule`)
- **`TDS_TOKEN`**: Token dùng API của `traodoisub.com`. (cho `traodoisub`)


---

### AI Chatbot trên FB

- Lần đầu tiên, bạn cần chạy workflow `Configure Facebook account for schedule AI Chat runs` để nó đăng nhập Facebook và tạo hai tệp `logininfo.json` và `cookies.json`. Những tệp này sẽ được mã hóa bằng biến secret `PASSWORD` mà bạn đã thiết lập. Sau đó, nó sẽ được lưu trữ trong nhánh `caches/schedule` của repo.
- Khi thay đổi tài khoản Facebook, hãy xóa nhánh `cache/schedule` rồi chạy lại workflow `Configure Facebook account for schedule AI Chat runs`

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
        "cookies" : []
    },
    {
        "username": "facebook_number_or_email_2",
        "password": "facebook_password_2",
        "otp_sec": "PYOTP_TOKEN_SECRET_CODE_2",
        "alt": "1",
        "cookies" : []
    }
]
```

## 📌 Lưu ý

Bảo mật: Đảm bảo tất cả các tệp và thông tin trong thư mục secrets được bảo vệ nghiêm ngặt.

