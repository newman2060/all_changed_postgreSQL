### 1. Tạo một file `.env` trong thư mục dự án của bạn với nội dung như sau:
```
DB_HOST=your_host
DB_PORT=your_port
DB_PASSWORD=your_password
DEFAULT_DB_NAME=postgres
DEFAULT_DB_USER=your_default_user

VIRTUAL_ENV=./venv
```



### 2. **Tạo môi trường ảo**

```bash
python -m venv venv
```

### 3. **Kích hoạt môi trường ảo**

- **Trên Windows**:
  ```bash
  venv\Scripts\activate
  ```


### 4. Để sử dụng mã này, bạn cần cài đặt thêm các thư viện sau:
```
pip install python-dotenv pandas openpyxl psycopg2
```

### 5. Chạy file `all_changed.py`
```
python all_changed.py
```

