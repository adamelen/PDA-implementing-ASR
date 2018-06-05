from record import record
from STT import STT
from TTIV import TTIV
import weather
import ConfigParser
import json
from gtts import gTTS
import os

# read config file
config = ConfigParser.ConfigParser()
config.read('config.ini')

lang = config.get('GENERAL', 'LANGUAGE');

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
# extract intent and value from text
if (config.get('FUNCTIONS','TEXT_TO_INTENT_VALUE') == 'ON'):
    if (config.get('TTIV', 'SPECIFIC_TEXT') == 'ON'):  # use a predefined text, otherwise use the text that was returned by STT
        text = config.get('TTIV', 'TEXT')
    (intent, value) = TTIV(config.get('TTIV', 'WIT_ACCESS_TOKEN'),
                           config.get('TTIV', 'BASE_URL'),
                           text)
    print("TTIV result: " + intent + " " + value)
# get the info that the user asked for
if (config.get('FUNCTIONS', 'GET_INFO') == 'ON'):
    if (config.get('INFO', 'CHOOSE_SERVICE') == 'ON'):  # use a predefined service, otherwise use the intent as a service
        service = config.get('INFO', 'SERVICE')
    else:
        service = intent
    if (service == 'weather'):	# get a weather forecast from https://openweathermap.org/
        base_url = config.get('WEATHER', 'WEATHER_BASE_URL')
        app_id = config.get('WEATHER', 'APP_ID')
        if (config.get('WEATHER', 'SPECIFIC_CITY_ID') == 'ON'):  # use a predefined city_id
            city_id = config.get('WEATHER', 'CITY_ID')
        else:
            city_id = weather.find_city_id(value)  # otherwise find the city_id that corresponds to the city_name (=value)
        textToTell = weather.weather(base_url, city_id, lang.lower(), app_id)
        print(textToTell)
    ttsobj = gTTS(textToTell)
    ttsobj.save("textToSpeech.mp3")
    os.system("mpg321 textToSpeech.mp3")
