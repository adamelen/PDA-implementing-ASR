# coding=utf-8

from record import record
from STT import STT
from translation import translation
from TTIV import TTIV
from weather import weather
from hospital import hospital
from pharmacy import pharmacy
from taxi import taxi
import ConfigParser
import json
from gtts import gTTS
import os

# lookup table containing all services and the corresponding functions
services = {
           'weather': lambda: weather(parameters),
           'hospital': lambda: hospital(parameters),
           'pharmacy': lambda: pharmacy(parameters),
           'taxi': lambda: taxi(parameters)
           } 

# read config file
config = ConfigParser.ConfigParser()
config.read('config.ini')

lang = config.get('GENERAL', 'LANGUAGE')

# record user
if (config.get('FUNCTIONS','RECORD') == 'ON'):
    record(config.get('RECORD', 'RECORD_FILE_NAME'))

# convert speech to text
if (config.get('FUNCTIONS', 'SPEECH_TO_TEXT') == 'ON'):
    text = STT(config.get('STT', 'WAV_FILE_NAME'),
               config.get(lang, 'HMM'),
               config.get(lang, 'LM'),
               config.get(lang, 'DIC'))
    print("STT result: " + text)

# if text isn't in English, translate it
if (config.get('FUNCTIONS', 'TRANSLATION') == 'ON'):
    if (lang == 'EL'):
        if (config.get('TRANSLATION', 'SPECIFIC_TEXT') == 'ON'):
            text = config.get('TRANSLATION', 'TEXT')
        text = translation(config.get('TRANSLATION', 'BASE_URL'),
                    config.get('TRANSLATION', 'APP_ID'),
                    text,
                    config.get('TRANSLATION', 'LANG_FROM_TO'))
        print('Translation result: ' + text)

# extract intent and value from text
if (config.get('FUNCTIONS','TEXT_TO_INTENT_VALUE') == 'ON'):
    if (config.get('TTIV', 'SPECIFIC_TEXT') == 'ON'):  # use a predefined text, otherwise use the text that was returned by STT
        text = config.get('TTIV', 'TEXT')
    (intent, parameters) = TTIV(config.get('TTIV', 'WIT_ACCESS_TOKEN'),
                           config.get('TTIV', 'BASE_URL'),
                           text)
    print("TTIV result:")
    print(intent)
    print(parameters)

# get the info that the user asked for
if (config.get('FUNCTIONS', 'GET_INFO') == 'ON'):
    if (config.get('INFO', 'CHOOSE_SERVICE') == 'ON'):  # use a predefined service, otherwise use the intent as a service
        service = config.get('INFO', 'SERVICE')
    else:
        service = intent
    textToTell = services[service]()
    print(textToTell)
    ttsobj = gTTS(textToTell, lang=lang.lower())
    ttsobj.save("textToSpeech.mp3")
    os.system("mpg321 textToSpeech.mp3")
