
### **Tài liệu hướng dẫn Workflow: Chạy Auto Traodoisub với Facebook**

## **Tên Workflow**  
`Run Auto Traodoisub with Facebook`

---

## **1. Sự kiện kích hoạt Workflow**

Workflow được kích hoạt bởi hai sự kiện chính:

- **Lịch định kỳ (`schedule`)**

  Workflow sẽ chạy mỗi ngày vào lúc 0h theo định dạng cron:
  ```cron
  0 0 * * *
  ```

- **Thủ công (`workflow_dispatch`)**

  Cho phép người dùng thực thi thủ công với các thông số nhập tùy chọn.

---

## **2. Thông số nhập (Inputs)**

- `json`: Nhập JSON chứa danh sách tài khoản đăng nhập. Nếu để trống, workflow sẽ sử dụng bản sao lưu. Không bắt buộc.

	Ví dụ :
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


- `count`: Số vòng lặp cho một công việc:
  - `0`: Chỉ kiểm tra.
  - `999`: Vô hạn (mặc định). Không bắt buộc.
- `timelimit`: Thời gian giới hạn của workflow tính bằng giây. Mặc định là `7200`. Không bắt buộc.
- `delay`: Thời gian trễ giữa các công việc tính bằng giây. Mặc định là `100`. Không bắt buộc.

---

## **3. Các bước công việc (Jobs)**

### **Job: run-tests**

- **Chạy trên môi trường:** `windows-latest`
- **Biến môi trường quan trọng:**  
  - `GITHUB_TOKEN`: Token GitHub.
  - `STORAGE_BRANCE`: Nhánh lưu trữ tạm thời.

---

## **4. Các bước thực hiện (Steps)**

### **1. Checkout repository**
Sử dụng GitHub Action `actions/checkout@v3` để lấy mã nguồn từ repository.

### **2. Thiết lập Python**
Sử dụng `actions/setup-python@v4` để cài đặt Python 3.9.

### **3. Cài đặt thư viện phụ thuộc**
Chạy lệnh:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Hủy workflow trước đó**
Sử dụng GitHub Action `styfle/cancel-workflow-action@0.12.1` để hủy các workflow đang chạy.

### **5. Chạy script Auto Traodoisub**
Chạy script thực thi công việc:
```bash
python traodoisub_v2_timeout.py
```
Biến môi trường quan trọng:
- `PYTHONUNBUFFERED`: Đặt giá trị `"1"` để hiển thị log liên tục.
- `PASSWORD`: Sử dụng mật khẩu từ GitHub Secrets.
- `TDS_TOKEN`: Token Traodoisub từ GitHub Secrets.

---

## **5. Ghi chú**

- Cần cấu hình GitHub Secrets cho các thông tin nhạy cảm như `PASSWORD` và `TDS_TOKEN`.