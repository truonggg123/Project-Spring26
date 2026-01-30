# Project-Spring26


1. Thành viên 1: Database Logic (database.py)
•	Nhiệm vụ: Quản lý mọi thứ liên quan đến lưu trữ lâu dài.
•	Công việc cụ thể:
o	Cài đặt SQL Server và thư viện pyodbc.
o	Viết code tạo bảng (Users, History).
o	Viết hàm save_practice_result(user_id, target, user_text, score) để chèn dữ liệu.
o	Viết hàm load_history(user_id) trả về một danh sách để hiển thị lên bảng Gradio.
•  Hàm register_user(username, password):
•	Kiểm tra xem username đã tồn tại trong bảng Users chưa.
•	Nếu chưa, thực hiện câu lệnh INSERT INTO Users (Username, Password) VALUES (?, ?).
•  Hàm login_user(username, password):
•	Thực hiện câu lệnh SELECT UserID FROM Users WHERE Username = ? AND Password = ?.
•	Nếu tìm thấy, trả về UserID để các module khác (như Lịch sử) sử dụng. Nếu không, trả về None.

•	Mục tiêu: Đảm bảo dữ liệu không bị mất khi tắt ứng dụng.

2. Thành viên 2: Comparison Algorithm (algorithm.py)
•	Nhiệm vụ: Xây dựng bộ máy chấm điểm bằng thuật toán DSA.
•	Công việc cụ thể:
o	Tự code thuật toán Levenshtein Distance bằng phương pháp mảng 2 chiều (Quy hoạch động).
o	Viết hàm get_pronunciation_score(s1, s2) nhận vào 2 chuỗi văn bản và trả về số điểm (0-100).
o	Viết thêm logic để so sánh từng từ và đánh dấu màu (ví dụ: từ nào đúng trả về màu xanh, sai trả về màu đỏ).
•	Mục tiêu: Trả về kết quả phân tích chính xác độ lệch giữa câu mẫu và câu người dùng nói.


3. Thành viên 3: Suggestion Engine (search_engine.py)

•	Nhiệm vụ: Xử lý cấu trúc dữ liệu cây để hỗ trợ người dùng nhập liệu.
•	Công việc cụ thể:
o	Cài đặt cấu trúc dữ liệu Trie (Cây tiền tố).
o	Viết hàm insert_word(word) và hàm get_suggestions(prefix).
o	Tìm một danh sách khoảng 500-1000 từ tiếng Anh thông dụng, viết code để nạp danh sách này vào cây Trie khi khởi động.
•	Mục tiêu: Khi người dùng gõ từ vào ô tìm kiếm, cây Trie phải trả về danh sách các từ bắt đầu bằng chữ cái đó một cách nhanh nhất.


4. Thành viên 4: Speech & AI Handler (speech_module.py)

•	Nhiệm vụ: Phụ trách phần "Nghe" và "Nói" của AI.
•	Công việc cụ thể:
o	Tích hợp OpenAI Whisper (dùng bản base hoặc tiny cho nhẹ) để chuyển ghi âm thành văn bản.
o	Tích hợp gTTS để tạo giọng đọc mẫu cho câu tiếng Anh.
o	Viết hàm clean_text(text) để loại bỏ dấu câu, chuyển về chữ thường trước khi đưa cho Thành viên 2 chấm điểm.
•	Mục tiêu: Chuyển đổi qua lại giữa âm thanh và văn bản một cách mượt mà.


5. Thành viên 5: UI Designer (interface.py)
•	Nhiệm vụ: Xây dựng "mặt tiền" của ứng dụng.
•	Công việc cụ thể:
o	Sử dụng Gradio tạo 3 Tab: Luyện tập, Tra từ, Lịch sử.
o	Tạo các thành phần: gr.Audio (ghi âm), gr.Textbox (nhập văn bản), gr.Dataframe (hiển thị lịch sử), gr.HTML (hiển thị điểm số vòng tròn).
o	Viết CSS để giao diện trông hiện đại và chuyên nghiệp (căn giữa các thành phần, đổi màu nút bấm).
•	Mục tiêu: Tạo ra một giao diện hoàn chỉnh, dù hiện tại các nút bấm chỉ đang gọi đến các hàm "giả" (dummy functions).



6. Thành viên 6: Dictionary & Logic Integrator (dictionary_logic.py)
•	Nhiệm vụ: Xử lý dữ liệu từ điển và chuẩn bị cho việc ghép nối.
•	Công việc cụ thể:
o	Tìm và xử lý file dữ liệu từ điển (thường là JSON hoặc CSV Anh-Việt).
o	Viết hàm lookup_word(word) trả về nghĩa, loại từ và ví dụ.
o	Viết các hàm xử lý trung gian (ví dụ: chuyển đổi điểm số từ con số sang nhận xét "Tốt", "Cần cố gắng").



DEADLINE: 28/2/2026


====Kết quả=========
Sản phẩm (Elsa Clone)
Các bạn sẽ có một ứng dụng hoàn chỉnh với các tính năng:
1.	Hệ thống tài khoản: Đăng ký, đăng nhập bảo mật bằng SQL Server.
2.	Luyện tập AI: Chấm điểm phát âm chính xác dựa trên thuật toán và trí tuệ nhân tạo.
3.	Từ điển thông minh: Gợi ý từ khi gõ (Autocomplete) và tra cứu nghĩa nhanh chóng.
4.	Báo cáo tiến độ: Xem lại lịch sử luyện tập và điểm số cá nhân


===================================================================

Ba file code ban đầu bạn gửi đóng vai trò là "Proof of Concept" (Bản mẫu thử nghiệm). Chúng chứng minh rằng ý tưởng này khả thi, nhưng để trở thành một project môn học đạt điểm cao, nhóm bạn sẽ bóc tách và tái cấu trúc lại chúng thành một hệ thống chuyên nghiệp hơn.
Dưới đây là cách nhóm bạn sẽ "tiến hóa" từ 3 file đó sang 6 module độc lập:
1. Sự thay đổi về cấu trúc (Architecture)
•	3 file cũ: Code trộn lẫn giữa giao diện (Gradio), logic chấm điểm và lưu trữ (file JSON). Điều này khiến việc làm việc nhóm rất khó vì ai sửa vào file nào cũng dễ làm hỏng phần của người khác.
•	6 file mới: Mỗi người là một "ông chủ" của một file riêng.
o	Thành viên 4 sẽ lấy phần Whisper và gTTS từ file cũ để đưa vào speech_module.py.
o	Thành viên 5 sẽ lấy phần layout Gradio để đưa vào interface.py.
o	Thành viên 2 sẽ không dùng thư viện có sẵn nữa mà tự viết thuật toán vào algorithm.py.
________________________________________
2. Sự nâng cấp về chất lượng (Quality)
Các bạn không chỉ "chép lại" code cũ mà là nâng cấp nó để đáp ứng yêu cầu của giảng viên:
•	Từ JSON sang SQL Server: File history.py cũ dùng JSON (rất dễ bị mất dữ liệu hoặc lỗi nếu nhiều người cùng ghi). Thành viên 1 sẽ nâng cấp nó lên SQL Server, cho phép quản lý hàng ngàn người dùng và lịch sử luyện tập một cách an toàn.
•	Từ thư viện sang Thuật toán tự thân: File logic.py cũ dùng thư viện Levenshtein. Thành viên 2 sẽ tự code thuật toán này bằng Quy hoạch động. Đây là phần giúp bạn lấy điểm môn DSA.
•	Thêm cấu trúc dữ liệu mới: Code cũ không có gợi ý từ vựng. Thành viên 3 sẽ thêm cây Trie để tối ưu hóa trải nghiệm người dùng, giúp app "thông minh" hơn.
________________________________________
3. Quy trình làm việc thực tế của nhóm
Nhóm bạn sẽ coi 3 file cũ như một bản thiết kế mẫu để hiểu luồng đi:
1.	Tham khảo logic.py để biết cách lấy text từ Whisper rồi đem đi so sánh.
2.	Tham khảo app.py để biết cách sắp xếp các component trên màn hình.
3.	Xây dựng mới: Mỗi thành viên viết file của mình dựa trên các gợi ý nhiệm vụ chi tiết ở trên.
________________________________________
4. Thành quả cuối cùng so với bản gốc
Sản phẩm cuối cùng của nhóm bạn sẽ vượt xa 3 file ban đầu:
•	Có Bảo mật (Đăng nhập/Đăng ký).
•	Có Hiệu năng (Tìm kiếm bằng Trie).
•	Có Độ tin cậy (Dữ liệu lưu trong SQL Server).
•	Có Học thuật (Thuật toán tự cài đặt).
Lời khuyên: Hãy giữ 3 file cũ đó để chạy thử và hiểu "cảm giác" của ứng dụng trước. Sau đó, mỗi thành viên bắt tay vào viết file độc lập của mình.

