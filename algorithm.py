import string

def preprocess_to_list(text: str) -> list:
    """Làm sạch chuỗi và chuyển thành danh sách từ để so sánh."""
    if not isinstance(text, str) or not text.strip():
        return []
    # Xóa dấu câu bằng string.punctuation và chuyển về chữ thường
    clean_text = text.lower().translate(str.maketrans('', '', string.punctuation))
    # Tách từ và loại bỏ khoảng trắng thừa
    return clean_text.split()

def calculate_levenshtein_distance_words(target_list: list, user_list: list) -> int:
    """Tính khoảng cách Levenshtein giữa hai danh sách từ (Word-level)."""
    m, n = len(target_list), len(user_list)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # So sánh toàn bộ từ
            cost = 0 if target_list[i - 1] == user_list[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )
    return dp[m][n]

def get_pronunciation_score(target: str, user: str) -> int:
    """Tính điểm dựa trên độ tương đồng của danh sách từ."""
    target_words = preprocess_to_list(target)
    user_words = preprocess_to_list(user)

    if not target_words:
        return 0
    
    distance = calculate_levenshtein_distance_words(target_words, user_words)
    max_len = len(target_words)
    
    # Công thức tính điểm dựa trên đơn vị Từ
    score = (1 - (distance / max_len)) * 100
    return max(0, min(100, int(round(score))))

def get_visual_comparison(target: str, user: str) -> str:
    """Hiển thị HTML với logic đã loại bỏ dấu câu khỏi việc so sánh."""
    # 1. Chuẩn bị dữ liệu hiển thị (giữ nguyên để không mất chữ của target)
    target_display = target.split() 
    
    # 2. Chuẩn bị dữ liệu so sánh (đã xóa dấu câu)
    target_clean = [w.translate(str.maketrans('', '', string.punctuation)).lower() for w in target_display]
    user_clean = preprocess_to_list(user)

    m, n = len(target_clean), len(user_clean)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if target_clean[i - 1] == user_clean[j - 1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)

    # 3. Truy vết ngược để tạo HTML
    i, j = m, n
    html_parts = []

    while i > 0 or j > 0:
        # Trường hợp Khớp (Correct)
        if i > 0 and j > 0 and target_clean[i-1] == user_clean[j-1]:
            html_parts.append(f'<span style="color: #28a745;">{target_display[i-1]}</span>')
            i -= 1; j -= 1
        # Trường hợp Sai hoặc Thiếu (Incorrect/Missing)
        elif i > 0:
            html_parts.append(f'<span style="color: #dc3545;">{target_display[i-1]}</span>')
            # Nếu là phép thay thế (Substitution), giảm cả i và j
            if j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                i -= 1; j -= 1
            else: # Phép xóa (Deletion/Missing)
                i -= 1
        # Trường hợp Thừa từ (Extra - User nói dư)
        else:
            j -= 1

    html_parts.reverse()
    return " ".join(html_parts)