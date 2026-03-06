import gradio as gr

# ==========================================
# CSS - MAZII STYLE + Custom Score Circle
# ==========================================
MAZII_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --sidebar-bg: #1B5D94;
    --sidebar-hover: #154a75;
    --main-bg: #F3F4F6;
    --card-bg: #FFFFFF;
    --text-primary: #1F2937;
    --text-sidebar: #FFFFFF;
}

body, .gradio-container {
    background-color: var(--main-bg) !important;
    font-family: 'Inter', sans-serif !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
}

.main-layout { display: flex; min-height: 100vh; }
.sidebar-col {
    background-color: var(--sidebar-bg) !important;
    padding: 20px !important;
    min-height: 100vh !important;
    display: flex;
    flex-direction: column;
    gap: 10px;
    box-shadow: 4px 0 10px rgba(0,0,0,0.1);
}

.logo-area {
    font-size: 24px; font-weight: 800; color: white;
    margin-bottom: 30px; padding-left: 10px;
    display: flex; align-items: center; gap: 8px;
}

.nav-btn {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.8) !important;
    text-align: left !important;
    font-weight: 500 !important;
    font-size: 16px !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    justify-content: flex-start !important;
    transition: all 0.2s !important;
}
.nav-btn:hover { background-color: var(--sidebar-hover) !important; color: white !important; }
.nav-btn.active {
    background-color: white !important;
    color: var(--sidebar-bg) !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.content-col { padding: 30px !important; background-color: var(--main-bg); }

.search-row {
    display: flex; align-items: center; gap: 0;
    border: 1px solid #E5E7EB; border-radius: 30px;
    padding: 6px 16px; background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: all 0.2s;
}
.search-row:focus-within { border-color: #2563EB; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }

.lang-select { border: none !important; box-shadow: none !important; background: transparent !important; width: 140px !important; font-weight: 600 !important; color: #1F2937 !important; }
.search-input { border: none !important; box-shadow: none !important; background: transparent !important; flex: 1; }
.search-input input { font-size: 16px !important; }

.custom-card {
    background: white; border-radius: 12px; padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    margin-bottom: 20px; animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.search-btn-icon {
    background: transparent !important; border: none !important; box-shadow: none !important;
    padding: 0 !important; min-width: 40px !important; width: 40px !important; height: 40px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.search-btn-icon::after {
    content: ""; display: block; width: 20px; height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236B7280' stroke-width='2.5'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: center; transition: all 0.2s;
}
.search-btn-icon:hover::after {
    filter: brightness(0.5);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%233B82F6' stroke-width='2.5'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
}

.floating-cat-btn {
    position: fixed !important; bottom: 30px !important; right: 30px !important;
    width: 80px !important; height: 80px !important; background: transparent !important;
    border: none !important; box-shadow: none !important; z-index: 9999 !important;
    cursor: pointer !important; display: flex !important; align-items: center !important; justify-content: center !important;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48Y2lyY2xlIGN4PSIyNTYiIGN5PSIyNTYiIHI9IjI0MCIgZmlsbD0iIzNCODJGNiIvPjxlbGxpcHNlIGN4PSIyNTYiIGN5PSIzMDAiIHJ4PSIxODAiIHJ5PSIxNDAiIGZpbGw9IiNGRkZGRkYiLz48Y2lyY2xlIGN4PSIyMTAiIGN5PSIyMjAiIHI9IjMwIiBmaWxsPSJibGFjayIvPjxjaXJjbGUgY3g9IjIyMCIgY3k9IjIxMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PGNpcmNsZSBjeD0iMzAyIiBjeT0iMjIwIiByPSIzMCIgZmlsbD0iYmxhY2siLz48Y2lyY2xlIGN4PSIzMTIiIGN5PSIyMTAiIHI9IjEwIiBmaWxsPSJ3aGl0ZSIvPjxjaXJjbGUgY3g9IjI1NiIgY3k9IjI3MCIgcj0iMjAiIGZpbGw9IiNFRjQ0NDQiLz48cGF0aCBkPSJNMjU2IDI5MCB2NjAiIHN0cm9rZT0iYmxhY2siIHN0cm9rZS13aWR0aD0iNCIvPjxwYXRoIGQ9Ik0xOTAgMzIwIGwtNjAgLTEwIE0zMjAgMzIwIGw2MCAtMTAgTTE5MCAzNDAgbC01MCAxMCBNMzIwIDM0MCBsNTAgMTAiIHN0cm9rZT0iYmxhY2siIHN0cm9rZS13aWR0aD0iNCIvPjxwb2x5Z29uIHBvaW50cz0iMjAwLDgwIDE1MCwyMCAyNTAsNTAiIGZpbGw9IiMzQjgyRjYiLz48cG9seWdvbiBwb2ludHM9IjMxMiw4MCAzNjIsMjAgMjYyLDUwIiBmaWxsPSIjM0I4MkY2Ii8+PHJlY3QgeD0iMjAwIiB5PSI0NDAiIHdpZHRoPSIxMTIiIGhlaWdodD0iMjAiIGZpbGw9IiNGQ0QzNEQiIHJ4PSIxMCIvPjwvc3ZnPg==") !important;
    background-size: contain !important; background-repeat: no-repeat !important; background-position: center !important;
}

.floating-cat-anim { animation: sway 3s ease-in-out infinite; transform-origin: bottom center; }
@keyframes sway { 0%, 100% { transform: rotate(-5deg); } 50% { transform: rotate(5deg); } }
.floating-cat-btn:hover { animation: shake 0.5s ease-in-out infinite; }
@keyframes shake { 0%, 50%, 100% { transform: rotate(0deg); } 25% { transform: rotate(-15deg); } 75% { transform: rotate(15deg); } }

.transparent-group, .transparent-group > *, .transparent-group .block, .transparent-group .form {
    background: transparent !important; background-color: transparent !important;
    border: none !important; box-shadow: none !important; padding: 0 !important;
}

.score-circle {
    width: 150px; height: 150px; border-radius: 50%; margin: 0 auto;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    background: #f8f9fa; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.score-value { font-size: 48px; font-weight: bold; margin: 0; }
.score-label { font-size: 14px; color: #666; margin-top: 5px; }
.score-good { border: 8px solid #4CAF50; color: #4CAF50; }
.score-average { border: 8px solid #FF9800; color: #FF9800; }
.score-bad { border: 8px solid #F44336; color: #F44336; }
.error { color: red; font-weight: bold; }
"""

def format_dict_result(result):
    if not result:
        return "<div style='color:#b91c1c; font-weight:500; background:#fef2f2; padding:16px; border-radius:12px; border: 1px solid #f87171; text-align:center;'>Không tìm thấy từ này trong cơ sở dữ liệu.</div>"
    
    word = result.get('word', '')
    phonetic = result.get('phonetic', '')
    definition = result.get('definition', '')
    
    def_text = str(definition).replace('\\\\n', '\n').replace('\\n', '\n')
    lines = def_text.split('\n')
    
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if not line: continue
            
        doc_lower = line.lower()
        if any(doc_lower.startswith(pos) for pos in ["danh từ", "tính từ", "động từ", "đại từ", "trạng từ", "giới từ", "liên từ"]):
            parts = line.split('-', 1)
            pos_text = parts[0].strip()
            rest_text = parts[1].strip() if len(parts) > 1 else ""
            html = f"<div style='margin-top: 16px; margin-bottom: 8px;'><span style='background: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.05em;'>{pos_text}</span>"
            if rest_text: html += f"<span style='font-weight: 600; color: #111827; margin-left: 10px; font-size: 1.1em;'>{rest_text}</span>"
            html += "</div>"
            formatted_lines.append(html)
        elif line.startswith('- '):
            formatted_lines.append(f"<div style='margin-left: 16px; position: relative; margin-bottom: 6px;'><span style='position: absolute; left: -16px; color: #3b82f6; font-weight: bold;'>•</span> <span style='font-weight: 600; color: #1f2937;'>{line[2:]}</span></div>")
        elif line.startswith('Example:'):
            parts = line.split('->', 1)
            ex_en = parts[0].replace('Example:', '').strip()
            ex_vi = parts[1].strip() if len(parts) > 1 else ""
            html = f"<div style='background: #f8fafc; padding: 12px; border-left: 3px solid #64748b; border-radius: 4px; margin: 8px 0 12px 16px;'>"
            html += f"<div style='color: #0f172a; font-style: italic; font-weight: 500;'>{ex_en}</div>"
            if ex_vi: html += f"<div style='color: #475569; margin-top: 4px; font-size: 0.95em;'>→ {ex_vi}</div>"
            html += "</div>"
            formatted_lines.append(html)
        else:
            formatted_lines.append(f"<div style='margin-bottom: 8px; font-weight: 500; color: #1e293b;'>{line}</div>")

    definition_html = "".join(formatted_lines)
    
    return f"""
    <div style="background:white; padding:32px; border-radius:16px; box-shadow:0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; display:flex; flex-direction:column;">
        <div style="display: flex; align-items: baseline; gap: 16px; margin-bottom: 24px; flex-shrink: 0;">
            <h2 style="color:#1e3a8a; font-size:3em; font-weight:800; margin:0; letter-spacing:-0.02em;">{word}</h2>
            <div style="color:#b91c1c; background:#fee2e2; padding:4px 12px; border-radius:20px; font-family: monospace; font-size:1.1em; font-weight:600;">{phonetic}</div>
        </div>
        <div style="border-top: 1px solid #e2e8f0; padding-top: 24px; flex-grow: 1; padding-right: 8px;">
            <div style="font-size: 1.15em; line-height: 1.8; color: #334155;">{definition_html}</div>
        </div>
    </div>
    """

def get_nav_btn_css(is_active):
    return ["nav-btn", "active"] if is_active else ["nav-btn"]
