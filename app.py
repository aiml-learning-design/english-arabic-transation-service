import base64
import streamlit as st
from translator_marian import translate
from test_to_speech import generate_audio
import logging
from io import BytesIO


# Configure app
st.set_page_config(
    page_title="EN->AR Translator",
    layout="wide"
)

st.title(" English → Arabic Translator 🌐🈳")


def process_text(text):
    try:
        arabic_text = translate(text)
        arabic_text = arabic_text.replace("<pad>", "").replace("</s>", "").strip()
        return arabic_text, generate_audio(arabic_text)
    except Exception as ex:
        logging.error(f"Processing error: {str(ex)}")
        return str(ex), None


# Layout
col1, col2 = st.columns(2)

with col1:
    english_input = st.text_area(
        "English Text",
        placeholder="Type here...",
        height=150,
        key="english_input"
    )
    translate_btn = st.button("Translate & Pronounce")

with col2:
    # Initialize output areas
    translation_display = st.empty()
    audio_display = st.empty()

    # Default state
    translation_display.text_area(
        "Arabic Translation",
        value="",
        height=150,
        disabled=True,
        key="arabic_translation_default"
    )

    # Process on button click
    if translate_btn:
        if english_input.strip():
            with st.spinner("Translating..."):
                arabic_text, audio_data = process_text(english_input)

                # Update translation
                translation_display.text_area(
                    "Arabic Translation",
                    value=arabic_text,
                    height=150,
                    disabled=True,
                    key="arabic_translation_result"
                )

                # Update audio if available
                if audio_data:
                    try:
                        if isinstance(audio_data, str):  # Handle file path
                            with open(audio_data, "rb") as f:
                                audio_bytes = f.read()
                            audio_display.audio(audio_bytes, format='audio/mp3')
                        else:  # Handle base64
                            audio_bytes = base64.b64decode(audio_data.split(",")[1])
                            audio_display.audio(BytesIO(audio_bytes), format='audio/wav')
                    except Exception as e:
                        st.error(f"Audio error: {str(e)}")
                else:
                    audio_display.warning("No audio generated")
        else:
            st.warning("Please enter text to translate")
