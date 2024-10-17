import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from datetime import datetime
import pandas as pd
import glob

# Đọc thông tin từ file .env
load_dotenv()

# Thông tin kết nối đến cơ sở dữ liệu
db_params = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DEFAULT_DB_NAME"),
    "user": os.getenv("DEFAULT_DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def get_all_tables(cursor):
    cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_row_count(cursor, table_name):
    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
    return cursor.fetchone()[0]

def get_latest_excel_file():
    files = glob.glob("bang_thay_doi_*.xlsx")
    if not files:
        return None
    return max(files, key=os.path.getctime)

def load_previous_data(file_path):
    if file_path:
        df = pd.read_excel(file_path)
        return {row['Tên bảng']: row['Số hàng hiện tại'] for _, row in df.iterrows()}
    return {}

def main():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:
        all_tables = get_all_tables(cursor)

        latest_file = get_latest_excel_file()
        previous_data = load_previous_data(latest_file)

        print("Các bảng có thay đổi:")
        data = []
        for table in all_tables:
            current_count = get_table_row_count(cursor, table)
            previous_count = previous_data.get(table, 0)
            difference = current_count - previous_count

            if difference != 0:
                print(f"Bảng: {table}, Thời gian kiểm tra: {datetime.now()}, Số hàng hiện tại: {current_count}, Số hàng trước đó: {previous_count}, Chênh lệch: {difference}")
                data.append({
                    "Tên bảng": table,
                    "Thời gian kiểm tra": datetime.now(),
                    "Số hàng hiện tại": current_count,
                    "Số hàng trước đó": previous_count,
                    "Chênh lệch": difference
                })

        # Tạo DataFrame từ dữ liệu
        df = pd.DataFrame(data)

        # Xuất ra file Excel với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f"bang_thay_doi_{timestamp}.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"Đã xuất kết quả ra file: {excel_file}")

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
