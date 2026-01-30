import gradio as gr
import history
from logic import PronunciationTrainer

# ==========================================
# CONFIGURATION
# ==========================================
# Set to True to skip model loading (for fast UI development)
MOCK_MODE = False 

# Initialize Core Logic
trainer = PronunciationTrainer(mock_mode=MOCK_MODE)

# ==========================================
# UI CONSTANTS
# ==========================================
EXAMPLE_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How much wood would a woodchuck chuck?",
    "Peter Piper picked a peck of pickled peppers.",
    "I scream, you scream, we all scream for ice cream.",
]

CUSTOM_CSS = """
.score-circle {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #f8f9fa;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.score-value { font-size: 48px; font-weight: bold; margin: 0; }
.score-label { font-size: 14px; color: #666; margin-top: 5px; }
.score-good { border: 8px solid #4CAF50; color: #4CAF50; }
.score-average { border: 8px solid #FF9800; color: #FF9800; }
.score-bad { border: 8px solid #F44336; color: #F44336; }
.error { color: red; font-weight: bold; }
"""

# ==========================================
# BUILD APPLICATION
# ==========================================
with gr.Blocks(title="English Pronunciation Trainer", theme=gr.themes.Soft(), css=CUSTOM_CSS) as app:
    
    gr.Markdown(
        """
        # 🎯 English Pronunciation Trainer
        ### Practice your English pronunciation with AI-powered feedback
        """
    )
    
    if MOCK_MODE:
        gr.Markdown("⚠️ **MOCK MODE ACTIVE**: AI Models are disabled. Used for UI development.", visible=True)

    with gr.Tabs():
        # TAB 1: PRACTICE ROOM
        with gr.TabItem("🎙️ Practice Room"):
            with gr.Row():
                # LEFT COLUMN - INPUTS
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Practice Text")
                    
                    target_text_input = gr.Textbox(
                        label="Enter text to practice",
                        placeholder="Type a sentence...",
                        lines=3,
                        value=EXAMPLE_SENTENCES[0]
                    )
                    
                    # Collapsible Examples
                    with gr.Accordion("📚 Quick Examples (Click to expand)", open=False):
                        gr.Markdown("Select an example to populate the text box:")
                        example_buttons = []
                        for example in EXAMPLE_SENTENCES:
                            btn = gr.Button(example, size="sm")
                            # When clicked, update the text box
                            btn.click(lambda x=example: x, None, target_text_input)

                    
                    gr.Markdown("---")
                    gr.Markdown("### 🔊 Listen to Reference")
                    
                    with gr.Row():
                        reference_btn = gr.Button("🎧 Generate Sample", variant="secondary")
                        reference_status = gr.Textbox(label="Status", interactive=False, visible=False)
                    
                    reference_audio = gr.Audio(label="Reference Audio", type="filepath")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🎤 Your Recording")
                    
                    user_audio_input = gr.Audio(
                        label="Record your pronunciation",
                        sources=["microphone"],
                        type="filepath"
                    )
                    
                    analyze_btn = gr.Button("✨ Analyze My Pronunciation", variant="primary", size="lg")
                
                # RIGHT COLUMN - RESULTS
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Your Results")
                    
                    # Score Display Component
                    score_display = gr.HTML(trainer.format_score_display(0))
                    
                    gr.Markdown("### 🔍 Detailed Analysis")
                    
                    visual_feedback = gr.HTML(
                        "<div style='padding: 20px; text-align: center; color: black;'>"
                        "Record your pronunciation to see visual feedback..."
                        "</div>"
                    )
                    
                    details_output = gr.Textbox(
                        label="Additional Information",
                        lines=4,
                        interactive=False
                    )

            gr.Markdown(
                """
                ---
                ### 📖 How to Use:
                1. **Enter** text or choose from **Quick Examples**.
                2. **Listen** to the sample audio.
                3. **Record** your voice.
                4. **Analyze** to check your score.
                """
            )

        # TAB 2: HISTORY
        with gr.TabItem("📜 My History"):
            gr.Markdown("### Your Practice History")
            refresh_btn = gr.Button("🔄 Refresh History", size="sm")
            
            history_table = gr.Dataframe(
                headers=["Date", "Target Text", "Your Speech", "Score", "Similarity"],
                datatype=["str", "str", "str", "number", "str"],
                value=history.load_data(),
                interactive=False,
                wrap=True
            )

    # ==========================================
    # EVENT HANDLERS
    # ==========================================
    
    # 1. Generate Reference Audio
    reference_btn.click(
        fn=trainer.generate_reference_audio,
        inputs=[target_text_input],
        outputs=[reference_audio, reference_status]
    )
    
    # 2. Analyze Pronunciation
    analyze_btn.click(
        fn=trainer.process_pronunciation,
        inputs=[target_text_input, user_audio_input],
        outputs=[score_display, visual_feedback, details_output, history_table]
    )
    
    # 3. Refresh History
    refresh_btn.click(
        fn=history.load_data,
        outputs=[history_table]
    )

if __name__ == "__main__":
    print(f"Starting app (Mock Mode: {MOCK_MODE})...")
    app.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )
