import ConfigParser
from gtts import gTTS
import os
from VoiceCommand import VoiceCommand
from RecordControl import RecordControl
from SpeechRecognitionControl import SpeechRecognitionControl
from Translation import Translation
from TextToIntentValue import TextToIntentValue
from Information import Information
from Service import Service
from WeatherAdapter import WeatherAdapter
from Places import Places

class AppControl:
    ''' A <<Controller>> class that controls the main functionality of the program through the function appControl() '''

    def __init__(self):
        self.services = {
           'weather': lambda: WeatherAdapter(),
           'hospital': lambda: Places('hospital', 'hospitals'),
           'pharmacy': lambda: Places('pharmacy', 'pharmacies')
           } 

    def app(self):
        # read config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')

        lang = config.get('GENERAL', 'LANGUAGE') # mhpws to lang na mpei san attribute?
        vc = VoiceCommand()  # create a VoiceCommand object
        trl = Translation(config.get('TRANSLATION', 'BASE_URL'),  # create a Translation object
                          config.get('TRANSLATION', 'APP_ID'))

        # record user
        if (config.get('FUNCTIONS','RECORD') == 'ON'):
            rec = RecordControl(config.get('RECORD', 'RECORD_FILE_NAME'))
            rec.record()

        # convert speech to text
        if (config.get('FUNCTIONS', 'SPEECH_TO_TEXT') == 'ON'):
            speech = SpeechRecognitionControl(config.get('STT', 'WAV_FILE_NAME'),
                                            config.get(lang, 'HMM'),
                                            config.get(lang, 'LM'),
                                            config.get(lang, 'DIC'))
            vc = speech.STT(vc)
            print("STT result: " + vc.text)

        # if text isn't in English, translate it
        if (config.get('FUNCTIONS', 'TRANSLATION') == 'ON'):
            if (lang == 'EL'):
                if (config.get('TRANSLATION', 'SPECIFIC_TEXT') == 'ON'):
                    vc.text = config.get('TRANSLATION', 'TEXT')
                    print(vc.text)
                vc.text = trl.translation(vc.text, 'el', 'en')
                print('Translation result: ' + vc.text)

        # extract intent and value from text
        if (config.get('FUNCTIONS','TEXT_TO_INTENT_VALUE') == 'ON'):
            if (config.get('TTIV', 'SPECIFIC_TEXT') == 'ON'):  # use a predefined text, otherwise use the text that was returned by STT
                vc.text = config.get('TTIV', 'TEXT')
            ttiv = TextToIntentValue(config.get('TTIV', 'WIT_ACCESS_TOKEN'),
                                     config.get('TTIV', 'BASE_URL'))
            vc = ttiv.TTIV(vc)
            print("TTIV result:")
            print(vc.intent)
            print(vc.parameters)

        # get the info that the user asked for
        if (config.get('FUNCTIONS', 'GET_INFO') == 'ON'):
            if (config.get('INFO', 'CHOOSE_SERVICE') == 'ON'):  # use a predefined service, otherwise use the intent as a service
                service = config.get('INFO', 'SERVICE')
                vc.parameters = {}
            else:
                service = vc.intent
            info = Information(self.services[service]())
            vc = info.useService(vc, trl)
            print(vc.textToTell)
            ttsobj = gTTS(vc.textToTell, lang=lang.lower())
            ttsobj.save("textToSpeech.mp3")
            os.system("mpg321 textToSpeech.mp3")

if __name__ == '__main__':
    app = AppControl()
    app.app()
