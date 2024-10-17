### tạo môi trường ảo
```bash
python -m venv venv
```

### kích hoạt môi trường ảo.
  ```bash
  venv\Scripts\activate
  ```

### cài đặt các thư viện từ đó vào môi trường ảo:

```bash
pip install -r requirements.txt
```

### tải file .gitignore từ link GitHub:

```
# URL của file .gitignore trên GitHub
$url = "https://raw.githubusercontent.com/newman2060/new_project_tips_tricks/main/.gitignore"

# Tên file đích
$outputFile = ".gitignore"

# Tải file
Invoke-WebRequest -Uri $url -OutFile $outputFile

# Kiểm tra xem file đã được tải về chưa
if (Test-Path $outputFile) {
    Write-Host "File .gitignore đã được tải thành công."
} else {
    Write-Host "Có lỗi xảy ra khi tải file .gitignore."
}
```

### Tạo một file `.env` trong thư mục dự án của bạn với nội dung như sau:
```
DB_HOST=your_host
DB_PORT=your_port
DB_PASSWORD=your_password
DEFAULT_DB_NAME=postgres
DEFAULT_DB_USER=your_default_user

VIRTUAL_ENV=./venv
```

### 5. **Chạy script**

- **Chạy script**: Khi bạn chạy script, nó sẽ tự động kết nối đến từng database, lấy danh sách các bảng và cột (loại bỏ cột bắt đầu bằng "create" và "update"), và xuất kết quả ra file Excel.

```bash
python all_changed.py
```

