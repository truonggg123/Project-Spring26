import string


def preprocess_text(text: str) -> str:
    """
    Tiền xử lý chuỗi:
    - Chuyển thành chữ thường.
    - Xóa các ký tự đặc biệt và dấu câu.
    - Loại bỏ khoảng trắng thừa.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Chuyển chữ thường
    text = text.lower()
    
    # Xoá dấu câu
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tách và ghép lại để loại bỏ khoảng trắng thừa
    return " ".join(text.split())


def calculate_distance(s1: str, s2: str) -> int:
    """
    Thuật toán tính khoảng cách Levenshtein bằng Quy hoạch động (Dynamic Programming).
    
    Args:
        s1 (str): Chuỗi gốc (Target)
        s2 (str): Chuỗi cần so sánh (User)
        
    Returns:
        int: Số bước chỉnh sửa tối thiểu (thêm, sửa, xóa).
    """
    # Xử lý trường hợp chuỗi rỗng
    if not s1:
        return len(s2) if s2 else 0
    if not s2:
        return len(s1)
        
    m, n = len(s1), len(s2)
    
    # Khởi tạo ma trận 2 chiều kích thước (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Khởi tạo giá trị cho cột đầu và hàng đầu
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    # Điền giá trị vào bảng Quy hoạch động
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
                
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # Phép xóa (Deletion)
                dp[i][j - 1] + 1,        # Phép thêm (Insertion)
                dp[i - 1][j - 1] + cost  # Phép thay thế (Substitution)
            )
            
    return dp[m][n]


def get_pronunciation_score(target: str, user: str) -> int:
    """
    Tính điểm phát âm của người dùng theo công thức.
    
    Args:
        target (str): Câu mẫu.
        user (str): Văn bản nhận diện từ giọng nói (AI Whisper).
        
    Returns:
        int: Điểm số từ 0 đến 100.
    """
    clean_target = preprocess_text(target)
    clean_user = preprocess_text(user)
    
    # Xử lý edge cases: nếu chuỗi target rỗng thì không thể chấm điểm
    if not clean_target:
        return 0
    
    # Tính khoảng cách Levenshtein trên chuỗi đã được làm sạch
    distance = calculate_distance(clean_target, clean_user)
    
    # Lấy max độ dài của câu mẫu (tối thiểu là 1 để tránh lỗi chia cho 0)
    max_len = max(len(clean_target), 1)
    
    # Công thức: Score = (1 - distance / max_len) * 100
    score = (1 - (distance / max_len)) * 100
    
    # Ràng buộc kết quả trong khoảng 0 đến 100 và làm tròn
    final_score = max(0, min(100, int(round(score))))
    
    return final_score


def get_visual_comparison(target: str, user: str) -> str:
    """
    So sánh từng từ và trả về kết quả hiển thị dạng HTML cho UI (Gradio).
    
    Quy tắc:
    - Từ đúng: Hiển thị màu xanh lá (#28a745)
    - Từ sai hoặc thiếu: Hiển thị màu đỏ (#dc3545)
    
    Args:
        target (str): Câu tiếng Anh mẫu.
        user (str): Câu người dùng đọc.
        
    Returns:
        str: Chuỗi HTML chứa các thẻ <span>.
    """
    if not isinstance(target, str) or not target.strip():
        return ""
        
    # Lấy danh sách từ gốc (giữ nguyên hoa/thường)
    target_words_orig = target.translate(str.maketrans('', '', string.punctuation)).split()
    # Danh sách từ dùng để tính toán (chữ thường)
    target_words = [w.lower() for w in target_words_orig]
    
    # Danh sách từ của người đọc
    if not isinstance(user, str) or not user.strip():
        user_words = []
    else:
        user_words = user.translate(str.maketrans('', '', string.punctuation)).lower().split()
        
    m, n = len(target_words), len(user_words)
    
    # Ma trận DP dùng cho so sánh cấp độ "từ" (word-level)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if target_words[i - 1] == user_words[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )
            
    # Truy vết ngược (Backtracking) để xác định trạng thái của từng từ trong câu mẫu
    i, j = m, n
    aligned_target = []
    
    while i > 0 or j > 0:
        # Nếu từ gốc và từ người dùng khớp nhau
        if i > 0 and j > 0 and target_words[i - 1] == user_words[j - 1]:
            aligned_target.append((target_words_orig[i - 1], "correct"))
            i -= 1
            j -= 1
        # Nếu từ bị thay thế (đọc sai)
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            aligned_target.append((target_words_orig[i - 1], "incorrect"))
            i -= 1
            j -= 1
        # Nếu từ bị thiếu (trong target có nhưng user không nói)
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            aligned_target.append((target_words_orig[i - 1], "incorrect"))
            i -= 1
        # Nếu từ bị thừa (user nói linh tinh thêm từ, bỏ qua không đưa lên UI dựa trên câu target)
        else:
            j -= 1
            
    # Hiển thị theo thứ tự từ trái sang phải
    aligned_target.reverse()
    
    # Khởi tạo danh sách các thẻ HTML
    html_elements = []
    
    for word, status in aligned_target:
        if status == "correct":
            html_elements.append(f'<span style="color: #28a745;">{word}</span>')
        else:
            html_elements.append(f'<span style="color: #dc3545;">{word}</span>')
            
    return " ".join(html_elements)
