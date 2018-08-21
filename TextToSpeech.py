# coding: utf-8

from gtts import gTTS

class TextToSpeech:
    def TTS(self, text, lang):
        ttsobj = gTTS(text, lang=lang)
        ttsobj.save("textToSpeech.mp3")
