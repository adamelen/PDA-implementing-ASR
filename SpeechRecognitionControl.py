from pocketsphinx import Pocketsphinx
from VoiceCommand import VoiceCommand

class SpeechRecognitionControl:
    ''' A <<Controller>> class that controls the Speech to Text process '''

    def __init__(self, hmm, lm, dic):
        # configure transcription parameters
        config = {
            'hmm': hmm,
            'lm': lm,
            'dic': dic
        }
        print("1")
        self.ps = Pocketsphinx(**config)
        print("2")

    def STT(self, audio_f, vc):
        '''Imports a .wav file and converts speech to text using pocketsphinx'''

        # decode audio and save the "hypothesis" as the text attribute in a VoiceCommand object
        self.ps.decode(
            audio_file=audio_f,
            buffer_size=2048,
            no_search=False,
            full_utt=False
        )

        # save the text above as the "text" attribute of the VoiceCommand object
        vc.text = unicode(self.ps.hypothesis(), 'utf-8')
        return vc

