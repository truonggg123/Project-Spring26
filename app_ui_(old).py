import gradio as gr
import whisper
import eng_to_ipa as ipa
import Levenshtein
import difflib
import numpy as np # Cần thêm thư viện này để tính toán số học

# 1. Tải Model
print("⏳ Đang tải Model Whisper...")
model = whisper.load_model("base")
print("✅ Sẵn sàng!")

def check_pronunciation(target_text, audio_path):
    if audio_path is None:
        return "⚠️ Bạn chưa ghi âm!", "0"
    
    # --- BƯỚC 1: AI NGHE & LẤY ĐỘ TỰ TIN ---
    # word_timestamps=False mặc định, nhưng ta cần lấy segments để tính độ tự tin
    result = model.transcribe(audio_path, fp16=False) # fp16=False để tránh lỗi trên CPU
    user_text = result["text"].strip()
    
    if not user_text:
        return "❌ Không nghe rõ, nói to lên nhé!", "0"

    # Tính độ tự tin trung bình (Confidence Score)
    # Whisper trả về log_probability (số âm). Ta chuyển về % (0-100)
    avg_logprob = sum([s['avg_logprob'] for s in result['segments']]) / len(result['segments'])
    confidence_score = np.exp(avg_logprob) * 100 

    # --- BƯỚC 2: XỬ LÝ IPA ---
    target_clean = target_text.lower().strip(".,?!")
    user_clean = user_text.lower().strip(".,?!")
    
    target_ipa = ipa.convert(target_clean)
    user_ipa = ipa.convert(user_clean)
    
    # --- BƯỚC 3: HIỂN THỊ LỖI ---
    matcher = difflib.SequenceMatcher(None, target_ipa, user_ipa)
    ipa_similarity = matcher.ratio() * 100 # Điểm giống nhau về mặt chữ viết

    # --- BƯỚC 4: TÍNH ĐIỂM TỔNG HỢP (QUAN TRỌNG) ---
    # Công thức: 60% dựa trên IPA khớp + 40% dựa trên độ dứt khoát của giọng đọc
    # Nếu bạn đọc đúng chữ nhưng lí nhí hoặc sai tông -> Confidence thấp -> Kéo điểm xuống
    final_score = (ipa_similarity * 0.6) + (confidence_score * 0.4)

    # Logic hiển thị HTML (như cũ nhưng thêm info)
    html_output = f"<h3>🗣️ AI nghe được: '{user_text}'</h3>"
    
    # Hiển thị thanh độ tự tin
    color_conf = "red" if confidence_score < 60 else "green"
    html_output += f"<p>🤖 Độ tự tin của AI: <span style='color:{color_conf}'><b>{confidence_score:.1f}%</b></span> (Nếu thấp nghĩa là bạn phát âm chưa rõ)</p>"
    
    html_output += f"<p>🔤 So sánh âm: /{target_ipa}/</p><hr>"
    html_output += "<div style='font-size: 20px; line-height: 1.8;'>"
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            html_output += f"<span style='color: green; font-weight: bold;'>{target_ipa[i1:i2]}</span>"
        elif tag == 'replace':
            html_output += f"<span style='color: red; text-decoration: underline; margin: 0 5px;' title='Bạn đọc là: {user_ipa[j1:j2]}'>{target_ipa[i1:i2]}</span>"
        elif tag == 'delete':
            html_output += f"<span style='background-color: #ffeeba; color: #856404; margin: 0 5px;'>[Thiếu: {target_ipa[i1:i2]}]</span>"
        elif tag == 'insert':
            html_output += f"<span style='color: gray; font-size: 0.8em;'>[Thừa: {user_ipa[j1:j2]}]</span>"
            
    html_output += "</div>"
    
    # Màu sắc điểm số cuối cùng
    score_color = "#e74c3c" # Đỏ
    if final_score > 80: score_color = "#27ae60" # Xanh
    elif final_score > 50: score_color = "#f39c12" # Cam
    
    score_html = f"""
    <div style='text-align: center;'>
        <h1 style='color: {score_color}; font-size: 4em; margin: 0;'>{final_score:.0f}</h1>
        <p style='color: gray;'>/ 100</p>
    </div>
    """
    
    return html_output, score_html

# Giao diện
with gr.Blocks(title="ELSA Strict Mode", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎤 ELSA Lite (Strict Mode)")
    gr.Markdown("ℹ️ *Phiên bản này sẽ trừ điểm nặng nếu bạn đọc đúng từ nhưng phát âm không rõ ràng (AI không tự tin).*")
    
    with gr.Row():
        with gr.Column():
            txt_target = gr.Textbox(label="Câu mẫu", value="I want to improve my English skills", lines=2)
            gr.Examples(
                examples=["Vegetables are good for health", "I would like a cup of coffee", "She sells seashells by the seashore"],
                inputs=txt_target
            )
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Thu âm")
            btn_check = gr.Button("Chấm điểm", variant="primary")
            
        with gr.Column():
            out_score = gr.HTML(label="Điểm tổng hợp")
            out_result = gr.HTML(label="Phân tích")

    btn_check.click(fn=check_pronunciation, inputs=[txt_target, audio_input], outputs=[out_result, out_score])

if __name__ == "__main__":
    print("🚀 Server đang chạy...")
    app.launch(server_name="0.0.0.0", server_port=7860)