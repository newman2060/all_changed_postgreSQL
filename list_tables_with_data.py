import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime

# Read information from .env file
load_dotenv()

# Database connection parameters
db_params = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DEFAULT_DB_NAME"),
    "user": os.getenv("DEFAULT_DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def get_tables_info(cursor):
    cursor.execute("""
    SELECT table_catalog, table_name,
           (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name) as column_count
    FROM information_schema.tables t
    WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()

    result = []
    for table in tables:
        table_catalog, table_name, column_count = table
        if column_count >= 1:
            # Check if the table has data and count the number of rows
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
            row_count = cursor.fetchone()[0]

            if row_count > 0:
                result.append({
                    'database': db_params['database'],
                    'table_catalog': table_catalog,
                    'table': table_name,
                    'columns': column_count,
                    'row_count': row_count
                })

    return result

def main():
    print("Starting database connection...")
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    print("Connected successfully.")

    try:
        print("Retrieving table information...")
        tables_info = get_tables_info(cursor)
        print(f"Retrieved information of {len(tables_info)} tables.")

        print("Information of tables with column count >= 3 and having data:")
        for table in tables_info:
            print(f"Table: {table['table']}, Columns: {table['columns']}, Rows: {table['row_count']}")

        print("Creating DataFrame...")
        df = pd.DataFrame(tables_info)

        print("Creating Excel file name...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"tables_info_{timestamp}.xlsx"

        print(f"Exporting to Excel file: {excel_filename}")
        df.to_excel(excel_filename, index=False)
        print(f"Exported table information to file: {excel_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing database connection...")
        cursor.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
