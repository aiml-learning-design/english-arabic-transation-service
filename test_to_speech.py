from gtts import gTTS
import os
import base64
import uuid


def generate_audio(text):
    try:
        tts = gTTS(text=text, lang='ar', )
       # audio_path = "temp_audio.mp3"
        audio_path = f"temp_audio.mp3"
        tts.save(audio_path)
     #   with open(audio_path, "rb") as audio_file:
      #      audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

        #os.remove(audio_path)
       # return f"data:audi/mp3;base64,{audio_base64}"
        return audio_path
    except Exception as ex:
        print(f"TTS Error: {str(ex)}")
        return ""
