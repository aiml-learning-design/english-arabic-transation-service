from gtts import gTTS


def generate_audio(text):
    try:
        tts = gTTS(text=text, lang='ar', )
        audio_path = f"temp_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as ex:
        print(f"TTS Error: {str(ex)}")
        return ""
