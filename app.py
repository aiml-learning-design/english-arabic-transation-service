import os
import tempfile
from typing import List

import gradio as gr
from langchain_core.documents import Document

from translator_marian import translate
from test_to_speech import generate_audio
import streamlit as st
import logging

from universal_loader import UniversalDocumentLoader


def extract_text_from_file(file_path: str) -> str:
    try:
        loader = UniversalDocumentLoader(file_path)
        documents: List[Document] = loader.load()
        return "\n\n".join([doc.page_content for doc in documents])
    except Exception as ex:
        logging.error(f"Error loading file: {str(ex)}")
        return f"Error extracting text: {str(ex)}"


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


def main():
    st.set_page_config(
        page_title="EN->AR Document Translator",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 English to Arabic Document Translator")
    st.markdown("""
    Upload any document (PDF, Word, etc.) or enter text manually to translate to Arabic.
    """)

    # Initialize session state
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input")

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "docx", "doc", "txt", "rtf", "html", "pptx", "ppt", "csv"],
            accept_multiple_files=False
        )

        # Manual text input
        english_text = st.text_area(
            "Or enter English text directly",
            height=200,
            value=st.session_state.extracted_text
        )

        # Process buttons
        process_col1, process_col2 = st.columns(2)
        with process_col1:
            if st.button("Extract Text", disabled=not uploaded_file):
                with st.spinner("Extracting text from document..."):
                    # Save uploaded file to temp location
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        extracted = extract_text_from_file(tmp_path)
                        st.session_state.extracted_text = extracted
                        english_text = extracted  # Update the text area
                    finally:
                        os.unlink(tmp_path)  # Clean up temp file

        with process_col2:
            translate_btn = st.button(
                "Translate to Arabic",
                disabled=not (english_text or st.session_state.extracted_text)
            )

    with col2:
        st.subheader("Output")

        # Display extracted text (editable)
        if st.session_state.extracted_text:
            st.text_area(
                "Extracted English Text",
                value=st.session_state.extracted_text,
                height=200,
                key="extracted_display"
            )

        # Display translation
        if st.session_state.translated_text:
            st.text_area(
                "Arabic Translation",
                value=st.session_state.translated_text,
                height=200,
                key="translated_display"
            )

            # Audio playback
            if st.session_state.audio_file:
                st.audio(st.session_state.audio_file, format="audio/mp3")

    # Handle translation
    if translate_btn and (english_text or st.session_state.extracted_text):
        text_to_translate = english_text if english_text else st.session_state.extracted_text

        with st.spinner("Translating to Arabic..."):
            translated_text, audio_data = process_text(text_to_translate)

            st.session_state.translated_text = translated_text
            st.session_state.audio_file = audio_data

            # Rerun to update the UI
            st.rerun()


if __name__ == "__main__":
    main()