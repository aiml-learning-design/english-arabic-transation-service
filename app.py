import gradio as gr
from translator_marian import translate
from test_to_speech import generate_audio
import logging


def process_text(text):
    try:
        arabic_text = translate(text)
        arabic_text = arabic_text.replace("<pad>", "").replace("</s>", "").strip()
        audio_base64 = generate_audio(arabic_text)
        return arabic_text, audio_base64 if audio_base64 else None
    except Exception as ex:
        logging.error(f"Processing error: {str(ex)}")
        return str(ex), None


with gr.Blocks(title="EN->AR Translator {Gemini}") as app:
    gr.Markdown("# English -> Arabic Translator (Gemini)")
    gr.Markdown("Powered by Google Gemini + RAG")

    with gr.Row():
        with gr.Column():
            english_input = gr.Textbox(label="English Text", placeholder="Type here...")
            translate_btn = gr.Button("Translate & Speak")

        with gr.Column():
            arabic_output = gr.Textbox(label="Arabic Translation", interactive=False)
            audio_output = gr.Audio(label="Pronunciation", visible=True)

    translate_btn.click(
        fn=process_text,
        inputs=english_input,
        outputs=[arabic_output, audio_output]
    )

if __name__ == '__main__':
    app.launch(
        server_port=8670,
        share=False,  # Disable share link creation
        show_error=True,
        server_name="0.0.0.0"  # Allow all network access
    )
