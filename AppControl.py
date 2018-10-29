# coding: utf-8

import ConfigParser
from gtts import gTTS
import unicodedata as ud
from word2number import w2n
from VoiceCommand import VoiceCommand
from RecordControl import RecordControl
from SpeechRecognitionControl import SpeechRecognitionControl
from Translation import Translation
from TextToIntentValue import TextToIntentValue
from Information import Information
from Service import Service
from WeatherAdapter import WeatherAdapter
from TextToSpeech import TextToSpeech
from PlaceServiceAdapter import PlaceServiceAdapter

class AppControl:
    ''' A <<Controller>> class that controls the main functionality of the program through the function appControl() '''

    def __init__(self):
        self.services = {
           'weather': lambda: WeatherAdapter(),
           'hospital': lambda: PlaceServiceAdapter('hospital'),
           'pharmacy': lambda: PlaceServiceAdapter('pharmacy')
           } 
        # read config file
        self.config = ConfigParser.ConfigParser()
        self.config.read('config.ini')
        #self.lang = self.config.get('GENERAL', 'LANGUAGE')
        self.vc = VoiceCommand()  # create a VoiceCommand object
        self.latin_letters= {}
        self.responses = {
            'el': 
            [u"Παρακαλώ επαναλάβετε αυτό που είπατε ή γράψτε το στο παρακάτω πλαίσιο (είναι πιο εύκολο να καταλάβω το γραπτό λόγο).",
             u"Δεν υπάρχουν πληροφορίες για την τοποθεσία που ζητήσατε. Αντικαταστήστε την με κάποια κοντινή της που είναι γνωστότερη.",
             u"Αυτά που είπατε δε σχετίζονται με κάποια υπηρεσία. Κάντε ένα ερώτημα για τον καιρό, τα νοσοκομεία ή τα φαρμακεία."],
            'en':
            ["Please repeat your question or write it in the box below (it's easier for me to understand written language).",
             "There is no information about the place you asked for. Replace it with a better known place close to it.",
             "Your question is irrelevant to the services provided. Ask a question about the weather, hospitals or pharmacies."]
            }

    def is_latin(self, uchr):
        try: return self.latin_letters[uchr]
        except KeyError:
            return self.latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

    # checks if there are any not latin characters
    def only_roman_chars(self, unistr):
        return all(self.is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())

    def start_rec(self):
        self.rec = RecordControl(self.config.get('RECORD', 'RECORD_FILE_NAME'))  # create a RecordControl object
        self.rec.record()  # and call the method that starts the recording

    def stop_rec(self):
        self.rec.stop_recording()  # call the method that stops the recording

    # The reason why there are 2 methods for STT control is that we want to do the initialization step in the main thread of the MainScreenUI and the rest in another thread that runs in the background in order the GUI not to freeze
    def initialize_STT(self, lang):
        config = self.config
        print("before")
        self.speech = SpeechRecognitionControl(config.get(lang.upper(), 'HMM'),
                                            config.get(lang.upper(), 'LM'),
                                            config.get(lang.upper(), 'DIC'))
        print("after")

    # convert speech to text
    def convert_to_text(self):
        print("convert to text")
        self.vc = self.speech.STT(self.config.get('STT', 'WAV_FILE_NAME'), self.vc)
        print("STT result: " + self.vc.text)

    def process_input(self, lang, text=''):
        config = self.config
        print("lang = " + lang)

        vc = self.vc
        if text != '':
            vc.text = text

        tts = TextToSpeech()
        # check if the user gave an empty or a None text
        if (vc.text == None or vc.text == ''):
            tempText = self.responses[lang][0]
            tts.TTS(tempText, lang)
            return tempText

        trl = Translation(config.get('TRANSLATION', 'BASE_URL'),  # create a Translation object
                          config.get('TRANSLATION', 'APP_ID'))

        # if text isn't in English, translate it
        if (lang == 'el'):
            vc.text = trl.translate(vc.text, 'el', 'en')
            print('Translation result: ' + vc.text)

        # check if there are any Greek characters in vc.text and return an error text if there are, because TTIV can't recognize greek characters
        if (self.only_roman_chars(vc.text)==False):
            tempText = self.responses[lang][1]
            return tempText

        if ("-" in vc.text):
            vc.text = vc.text.replace("-", " ")

        # extract intent and value from text
        if (config.get('FUNCTIONS','TEXT_TO_INTENT_VALUE') == 'ON'):
            ttiv = TextToIntentValue(config.get('TTIV', 'WIT_ACCESS_TOKEN'),
                                     config.get('TTIV', 'BASE_URL'))
            vc = ttiv.TTIV(vc)
            if vc.intent not in self.services:
                tempText = self.responses[lang][2]
                tts.TTS(tempText, lang)
                return tempText
            else: 
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
            vc = info.useService(vc, trl, lang)
            print(vc.textToTell)
            tts.TTS(vc.textToTell, lang)
            return vc.textToTell
        return ''

if __name__ == '__main__':
    app = AppControl()
    app.initialize_STT('en')
    app.convert_to_text()
    app.process_input('en')
