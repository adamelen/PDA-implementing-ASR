from pocketsphinx import AudioFile
from VoiceCommand import VoiceCommand

class SpeechRecognitionControl:
    ''' A <<Controller>> class that controls the Speech to Text process '''

    def __init__(self, audio_file, hmm, lm, dic):
        # configure transcription parameters
        self.audio_file = audio_file
        self.hmm = hmm
        self.lm = lm
        self.dic = dic

    def STT(self, vc):
        '''Imports a .wav file and converts speech to text using pocketsphinx'''

        config = {
            'audio_file': self.audio_file,
            'hmm': self.hmm,
            'lm': self.lm,
            'dic': self.dic
        }
        # extract phrases from audio and merge them in a "text" variable
        text = ""
        audio = AudioFile(**config)
        for phrase in audio:
            text = text + str(phrase) + " "

        # save the text above as the "text" attribute of the VoiceCommand object
        vc.text = text
        return vc

