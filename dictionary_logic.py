import pyodbc

class DictionaryLogic:
    def __init__(self):
        # Cấu hình kết nối SQL Server
        self.server = r'localhost\SQLEXPRESS03'
        self.database = 'DictionaryDB'
        self.conn_str = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"Trusted_Connection=yes;"
        )

    def _get_connection(self):
        """Tạo kết nối mới đến Database"""
        return pyodbc.connect(self.conn_str)

    def lookup(self, word):
        """
        Thực hiện tra cứu từ vựng dựa trên cột Word.
        Trả về một Dictionary chứa: Word, Phonetic, Definition hoặc None.
        """
        if not word:
            return None

        # Làm sạch từ khóa đầu vào
        search_term = word.strip().lower()
        
        # Truy vấn 3 cột đúng theo cấu trúc bảng của bạn
        query = """
            SELECT Word, Phonetic, Definition 
            FROM Dictionary 
            WHERE Word = ?
        """

        try:
            # Sử dụng 'with' để đảm bảo đóng kết nối ngay sau khi lấy dữ liệu
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_term,))
                row = cursor.fetchone()
                
                if row:
                    # Trả về dữ liệu đã được xử lý định dạng cơ bản
                    return {
                        "word": row[0].strip(),
                        "phonetic": f"[{row[1].strip()}]" if row[1] and row[1].strip() else "",
                        "definition": row[2] # Nội dung đã được format lúc import
                    }
        except Exception as e:
            print(f"❌ Lỗi truy vấn database: {e}")
            
        return None

# --- CHƯƠNG TRÌNH KIỂM TRA NHANH ---
if __name__ == "__main__":
    logic = DictionaryLogic()
    
    # Thử tra cứu một từ (Ví dụ: từ 's' hoặc từ bất kỳ bạn đã nạp)
    while True:
        print("Bấm Ctrl+C để thoát.")
        test_word = input("Nhập từ cần tra cứu: ")
        result = logic.lookup(test_word)
        
        if result:
            print(f"✅ Đã tìm thấy từ: {result['word']}")
            print(f"🔊 Phiên âm: {result['phonetic']}")
            print(f"📖 Nghĩa:\n{result['definition']}")
        else:
            print(f"❌ Không tìm thấy từ '{test_word}' trong từ điển.")