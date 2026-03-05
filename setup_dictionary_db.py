import pyodbc
import re

# ==============================


#FILE NÀY CHỈ CẦN CHẠY 1 LẦN ĐỂ NẠP DỮ LIỆU VÀO DB


# ==============================
SERVER = r'localhost\SQLEXPRESS03'
DATABASE = 'DictionaryDB'
CSV_FILE = 'English - Vietnamese.csv'
BATCH_SIZE = 1000


# ==============================
# FORMAT DEFINITION
# ==============================
def format_definition(text):
    if not text:
        return ""

    text = text.replace("|*  ", "\n\n")

    text = text.replace("|*", "\n\n")

    text = text.replace("|-", "\n- ")

    text = text.replace("|=", "\n   Ví dụ: ")

    text = text.replace("|+", " ➜ ")

    text = text.replace("||@", "\n@ ")

    return text.strip()


# ==============================
# IMPORT FUNCTION
# ==============================
def import_dictionary():

    conn = pyodbc.connect(
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={SERVER};Database={DATABASE};Trusted_Connection=yes;"
    )

    cursor = conn.cursor()

    print(" Drop bảng cũ nếu tồn tại...")
    cursor.execute("IF OBJECT_ID('Dictionary', 'U') IS NOT NULL DROP TABLE Dictionary")

    print(" Tạo bảng mới...")
    cursor.execute("""
        CREATE TABLE Dictionary (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Word NVARCHAR(500),
            Phonetic NVARCHAR(255),
            Definition NVARCHAR(MAX)
        )
    """)
    conn.commit()

    print(" Bắt đầu import...\n")

    insert_sql = """
        INSERT INTO Dictionary (Word, Phonetic, Definition)
        VALUES (?, ?, ?)
    """

    batch_data = []
    count = 0
    skipped = 0

    with open(CSV_FILE, encoding='utf-16') as f:
        next(f)  # bỏ header

        for line in f:

            line = line.strip()

            if not line:
                continue

            # CHỈ split tại dấu phẩy đầu tiên
            parts = line.split(",", 1)

            if len(parts) < 2:
                skipped += 1
                continue

            word_part = parts[0].strip()
            raw_text = parts[1].strip()

            # ======================
            # TÁCH PHONETIC
            # ======================
            phonetic = ""
            p_match = re.search(r'\[(.*?)\]', word_part)

            if p_match:
                phonetic = p_match.group(1)
                word = re.sub(r'\[.*?\]', '', word_part).strip().lower()
            else:
                word = word_part.lower()

            # chống lỗi word bất thường
            if len(word) == 0 or len(word) > 200:
                skipped += 1
                continue

            definition = format_definition(raw_text)

            batch_data.append((word, phonetic, definition))
            count += 1

            # batch insert
            if len(batch_data) >= BATCH_SIZE:
                cursor.executemany(insert_sql, batch_data)
                conn.commit()
                batch_data.clear()
                print(f"Đã import {count} từ...")

        # insert phần còn lại
        if batch_data:
            cursor.executemany(insert_sql, batch_data)
            conn.commit()

    conn.close()

    print("\n=============================")
    print(f" HOÀN TẤT!")
    print(f" Imported: {count} từ")
    print(f" Skipped: {skipped} dòng lỗi")
    print("=============================")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    import_dictionary()