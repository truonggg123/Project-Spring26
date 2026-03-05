# --- Patch: disable Gradio's BrotliMiddleware to fix the
# h11 "Too little data for declared Content-Length" bug on Windows.
# BrotliMiddleware compresses FileResponse bodies but does not update
# Content-Length, so h11 rejects the response. Easiest fix: make it a no-op.
try:
    import gradio.brotli_middleware as _bm

    async def _passthrough(self, scope, receive, send):
        await self.app(scope, receive, send)

    _bm.BrotliMiddleware.__call__ = _passthrough
except Exception:
    # Keep app startup resilient if Gradio internals change.
    pass
# --- End patch
import gradio as gr
import pandas as pd
import os
import history
import auth
from logic import PronunciationTrainer
from dictionary_logic import DictionaryLogic

from ui_components import MAZII_CSS, format_dict_result, get_nav_btn_css

# ==========================================
# CONFIGURATION
# ==========================================
MOCK_MODE = os.getenv("MOCK_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}
trainer = PronunciationTrainer(mock_mode=MOCK_MODE)
dict_logic = DictionaryLogic()

LESSONS = [
    "Lesson 1: Daily Conversations",
    "Lesson 2: At the Airport",
    "Lesson 3: Job Interview Skills",
]

SAMPLE_SCRIPTS = {
    "Lesson 1: Daily Conversations": "Hello, how are you today? I'm doing great.",
    "Lesson 2: At the Airport": "Where is the baggage claim area?",
    "Lesson 3: Job Interview Skills": "I have experience in software development.",
}

def lookup_word(word):
    if not word: return ""
    result = dict_logic.lookup(word)
    return format_dict_result(result)

# ————————————————————————————————————————————————————————————————————————————————————————————————————
# MAIN APPLICATION
# ————————————————————————————————————————————————————————————————————————————————————————————————————
with gr.Blocks(title="SpeakMaster AI", theme=gr.themes.Soft()) as app:
    # -- SESSION STATE --
    user_id_state = gr.State(None)
    username_state = gr.State("")
    
    # ── VIEW: AUTHENTICATION ──
    with gr.Column(visible=True) as view_auth:
        with gr.Row():
            with gr.Column(scale=1): pass
            with gr.Column(scale=2, elem_classes=["custom-card"]):
                # Login Form
                with gr.Column(visible=True) as login_form:
                    gr.HTML("<div style='text-align:center; margin-bottom:20px;'><h1 style='color:#1B5D94;'>SpeakMaster AI</h1><p>Chào mừng bạn quay lại!</p></div>")
                    login_user = gr.Textbox(label="Tên đăng nhập")
                    login_pass = gr.Textbox(label="Mật khẩu", type="password")
                    login_btn = gr.Button("Đăng nhập", variant="primary")
                    login_msg = gr.Markdown("")
                    goto_reg_btn = gr.Button("Chưa có tài khoản? Đăng ký ngay tại đây", variant="link")
                    
                # Registration Form
                with gr.Column(visible=False) as reg_form:
                    gr.HTML("<div style='text-align:center; margin-bottom:20px;'><h1 style='color:#1B5D94;'>Tạo tài khoản</h1><p>Hãy cùng bắt đầu hành trình luyện tiếng Anh!</p></div>")
                    reg_user = gr.Textbox(label="Tên đăng nhập mới")
                    reg_pass = gr.Textbox(label="Mật khẩu", type="password")
                    reg_confirm = gr.Textbox(label="Xác nhận mật khẩu", type="password")
                    reg_btn = gr.Button("Tạo tài khoản", variant="primary")
                    reg_msg = gr.Markdown("")
                    goto_login_btn = gr.Button("Đã có tài khoản? Đăng nhập", variant="link")

            with gr.Column(scale=1): pass

    # ── VIEW: MAIN APP ──
    with gr.Row(elem_classes=["main-layout"], visible=False) as view_main:
        
        # ── SIDEBAR (Left) ──
        with gr.Column(scale=1, min_width=250, elem_classes=["sidebar-col"]):
            gr.HTML('<div class="logo-area">SpeakMaster</div>')
            user_display = gr.Markdown("Người dùng: **Bản khách**")
            
            # Navigation Buttons
            btn_dict     = gr.Button("Tra cứu", elem_classes=["nav-btn", "active"])
            btn_practice = gr.Button("Luyện nói", elem_classes=["nav-btn"])
            btn_history  = gr.Button("Lịch sử", elem_classes=["nav-btn"])
            
            gr.Markdown("---")
            gr.Button("Cài đặt", elem_classes=["nav-btn"])

        # ── MAIN CONTENT (Right) ──
        with gr.Column(scale=5, elem_classes=["content-col"]):
            
            gr.Markdown("### Chào ngày mới !")

            # ── SEARCH BAR ──
            with gr.Row(elem_classes=["search-row"]):
                    lang_drp = gr.Dropdown(
                        choices=["Anh - Việt", "Việt - Anh"], 
                        value="Anh - Việt", 
                        container=False, 
                        elem_classes=["lang-select"],
                        interactive=True
                    )
                    search_txt = gr.Textbox(
                        placeholder="Nhập từ vựng cần tra cứu...", 
                        container=False, 
                        elem_classes=["search-input"],
                        scale=5,
                        show_label=False
                    )
                    search_btn = gr.Button(
                        value="",
                        scale=0, 
                        variant="secondary", 
                        elem_classes=["search-btn-icon"]
                    )
            
            # ── VIEW: DICTIONARY ──
            with gr.Column(visible=True, elem_classes=["transparent-group"]) as view_dict:
                gr.Markdown("#### Từ vựng trong ngày / Tìm kiếm")
                daily_word_row = gr.Row()
                with daily_word_row:
                    gr.HTML(lookup_word("hello"), elem_classes=["custom-card"])
                    gr.HTML(lookup_word("world"), elem_classes=["custom-card"])
                
                dict_result = gr.HTML(visible=False, elem_classes=["custom-card"])

            # ── VIEW: PRACTICE ──
            with gr.Group(visible=False) as view_practice:
                with gr.Column(elem_classes=["custom-card"]):
                    gr.Markdown("### 🎤 Luyện nói cùng AI")
                    
                    lesson_sel = gr.Dropdown(choices=LESSONS, value=LESSONS[0], label="Chọn bài học")
                    script_display = gr.Textbox(
                        value=SAMPLE_SCRIPTS[LESSONS[0]], 
                        label="Mẫu câu", 
                        lines=2, 
                        interactive=True
                    )

                    with gr.Row():
                        reference_btn = gr.Button("🎧 Nghe mẫu", variant="secondary")
                        reference_status = gr.Textbox(label="Status", interactive=False, visible=False)
                    reference_audio = gr.Audio(label="Giọng đọc mẫu", type="numpy")

                    audio_in = gr.Audio(label="Ghi âm giọng của bạn", sources=["microphone"], type="numpy")
                    analyze_btn = gr.Button("✨ Kiểm tra phát âm", variant="primary", size="lg")
                    
                    gr.Markdown("#### 📊 Kết quả")
                    with gr.Row():
                        with gr.Column(scale=1):
                            score_display = gr.HTML(trainer.format_score_display(0))
                        
                        with gr.Column(scale=2):
                            visual_feedback = gr.HTML(
                                "<div style='padding: 20px; text-align: center; color: black;'>"
                                "Ghi âm để xem đánh giá chi tiết..."
                                "</div>"
                            )
                            details_output = gr.Textbox(label="Thông tin thêm", lines=4, interactive=False)

            # ── VIEW: HISTORY ──
            with gr.Group(visible=False) as view_history:
                with gr.Column(elem_classes=["custom-card"]):
                    gr.Markdown("### 📜 Lịch sử học tập")
                    refresh_btn = gr.Button("🔄 Làm mới", size="sm")
                    history_table = gr.Dataframe(
                        headers=["Date", "Target Text", "Your Speech", "Score", "Similarity"],
                        datatype=["str", "str", "str", "number", "str"],
                        value=history.load_data(None), # Initial load with no user
                        interactive=False,
                        wrap=True
                    )
        
        # ── FLOATING CAT ──
        btn_cat = gr.Button(
            value="", 
            elem_classes=["floating-cat-btn", "floating-cat-anim"],
            scale=0
        )
    
    # ── AUTH LOGIC ──
    def handle_login(u, p):
        success, msg, uid = auth.login(u, p)
        if success:
            return (
                gr.update(visible=False), # hide auth
                gr.update(visible=True),  # show main
                uid, 
                u,
                f"Người dùng: **{u}**",
                history.load_data(uid) # load real history
            )
        return gr.update(value=msg), gr.update(), None, "", gr.update(), gr.update()

    def handle_register(u, p, c):
        if not u: return gr.update(value="Vui lòng nhập tên đăng nhập."), gr.update(), gr.update(), gr.update()
        if p != c:
            return gr.update(), gr.update(value="Mật khẩu xác nhận không khớp."), gr.update(), gr.update()
        
        success, msg, uid = auth.register(u, p)
        if success:
            return (
                gr.update(value=f"Đăng ký thành công! Chào {u}, hãy đăng nhập."), # login_msg
                gr.update(value=""), # clear reg_msg
                gr.update(visible=False), # hide reg form
                gr.update(visible=True)   # show login form
            )
        return gr.update(), gr.update(value=msg), gr.update(), gr.update()

    # Form switching
    goto_reg_btn.click(lambda: [gr.update(visible=False), gr.update(visible=True)], outputs=[login_form, reg_form])
    goto_login_btn.click(lambda: [gr.update(visible=True), gr.update(visible=False)], outputs=[login_form, reg_form])

    login_btn.click(
        fn=handle_login,
        inputs=[login_user, login_pass],
        outputs=[view_auth, view_main, user_id_state, username_state, user_display, history_table]
    )
    
    reg_btn.click(
        fn=handle_register,
        inputs=[reg_user, reg_pass, reg_confirm],
        outputs=[login_msg, reg_msg, reg_form, login_form]
    )

    # ————————————————————————————————————————————————————————————————————————————————————————————————————
    # LOGIC HANDLERS ————————————————————————————————————————————————————————————————————————————————————————————————————
    
    # Navigation Logic
    def switch_tab(target):
        style_dict     = get_nav_btn_css(target == "dict")
        style_practice = get_nav_btn_css(target == "practice")
        style_history  = get_nav_btn_css(target == "history")
        
        return [
            gr.update(elem_classes=style_dict),
            gr.update(elem_classes=style_practice),
            gr.update(elem_classes=style_history),
            gr.update(visible=(target == "dict")),
            gr.update(visible=(target == "practice")),
            gr.update(visible=(target == "history"))
        ]

    # Tabs Events
    btn_dict.click(lambda: switch_tab("dict"), outputs=[btn_dict, btn_practice, btn_history, view_dict, view_practice, view_history])
    btn_practice.click(lambda: switch_tab("practice"), outputs=[btn_dict, btn_practice, btn_history, view_dict, view_practice, view_history])
    btn_history.click(lambda: switch_tab("history"), outputs=[btn_dict, btn_practice, btn_history, view_dict, view_practice, view_history])
    btn_cat.click(lambda: switch_tab("practice"), outputs=[btn_dict, btn_practice, btn_history, view_dict, view_practice, view_history])

    # Dictionary Events
    search_txt.submit(lambda x: gr.update(value=lookup_word(x), visible=True), inputs=[search_txt], outputs=[dict_result])
    search_btn.click(lambda x: gr.update(value=lookup_word(x), visible=True), inputs=[search_txt], outputs=[dict_result])
    search_txt.submit(lambda: gr.update(visible=False), outputs=[daily_word_row])
    search_btn.click(lambda: gr.update(visible=False), outputs=[daily_word_row])
    
    # Practice Events
    lesson_sel.change(lambda x: SAMPLE_SCRIPTS.get(x, ""), inputs=[lesson_sel], outputs=[script_display])
    
    reference_btn.click(
        fn=trainer.generate_reference_audio,
        inputs=[script_display],
        outputs=[reference_audio, reference_status]
    )
    
    analyze_btn.click(
        fn=trainer.process_pronunciation,
        inputs=[script_display, audio_in, user_id_state],
        outputs=[score_display, visual_feedback, details_output, history_table]
    )

    refresh_btn.click(
        fn=history.load_data,
        inputs=[user_id_state],
        outputs=[history_table]
    )

if __name__ == "__main__":
    app.launch(
        share=False,
        server_name="127.0.0.1",
        show_error=True,
        css=MAZII_CSS
    )



