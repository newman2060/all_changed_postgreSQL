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

def create_change_log_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS my_change_log (
        table_name text PRIMARY KEY,
        last_check timestamp,
        row_count bigint
    )
    """)

def get_all_tables(cursor):
    cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    """)
    return [row[0] for row in cursor.fetchall()]

def update_change_log(cursor, table_name):
    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
    row_count = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO my_change_log (table_name, last_check, row_count)
    VALUES (%s, %s, %s)
    ON CONFLICT (table_name) DO UPDATE
    SET last_check = EXCLUDED.last_check, row_count = EXCLUDED.row_count
    """, (table_name, datetime.now(), row_count))

def get_changed_tables(cursor):
    cursor.execute("""
    SELECT t1.table_name, t1.last_check, t1.row_count,
           COALESCE(t2.row_count, 0) as previous_count,
           t1.row_count - COALESCE(t2.row_count, 0) as row_difference
    FROM my_change_log t1
    LEFT JOIN my_change_log t2 ON t1.table_name = t2.table_name AND t2.last_check < t1.last_check
    WHERE t1.row_count <> COALESCE(t2.row_count, -1)
    ORDER BY t1.last_check DESC
    """)
    return cursor.fetchall()

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
        create_change_log_table(cursor)

        all_tables = get_all_tables(cursor)
        for table in all_tables:
            update_change_log(cursor, table)

        changed_tables = get_changed_tables(cursor)

        latest_file = get_latest_excel_file()
        previous_data = load_previous_data(latest_file)

        print("Các bảng có thay đổi:")
        data = []
        for table in changed_tables:
            previous_count = previous_data.get(table[0], table[3])
            current_count = table[2]
            difference = current_count - previous_count
            print(f"Bảng: {table[0]}, Thời gian kiểm tra: {table[1]}, Số hàng hiện tại: {current_count}, Số hàng trước đó: {previous_count}, Chênh lệch: {difference}")
            data.append({
                "Tên bảng": table[0],
                "Thời gian kiểm tra": table[1],
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

        conn.commit()
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
