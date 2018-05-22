import os
import pyaudio
import wave
import time
import sys
import requests
import json
import gTTS
import datetime
from pocketsphinx import AudioFile

# ---------------- record speaker's speech and save it to "speak.wav"------------------------------
# instantiate PyAudio
p = pyaudio.PyAudio()

# prepare wav file
wf = wave.open('speak.wav', 'wb')
wf.setnchannels(1)
wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wf.setframerate(16000)

# define callback
def callback(in_data, frame_count, time_info, status):
    data = None
    wf.writeframes(in_data)
    return (data, pyaudio.paContinue)

# open stream using callback
stream = p.open(format=pyaudio.paInt16,  #proekupse meta apo elegxo etoimou .wav
                channels=1,
                rate=16000,
                input=True,
                stream_callback=callback)

# start the stream
stream.start_stream()

# wait for stream to finish (5)
#while stream.is_active():
#    time.sleep(0.1)
raw_input("When you finish, press Enter")

# stop stream
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio
p.terminate()

print("Recording Done")

# -------------------------------- Speech to Text ---------------------------
config = {
    'audio_file': '/home/elena/Diplwmatikh/FirstTry/speak.wav',
    # ELLHNIKA
    #'hmm':'/home/elena/Diplwmatikh/Sphinx/other/cmusphinx-el-gr-5.2/el-gr.cd_cont_5000',
    #'lm':'/home/elena/Diplwmatikh/Sphinx/other/cmusphinx-el-gr-5.2/el-gr.lm.bin',
    #'dic':'/home/elena/Diplwmatikh/Sphinx/other/cmusphinx-el-gr-5.2/el-gr.dic'
}

text = ""
audio = AudioFile(**config)
for phrase in audio:
    print(phrase)
    text = text + str(phrase) + " "

# ------------------------------- Text to Intent-Value (pros to paron orizw ena sugkekrimeno text gia ta upoloipa vhmata)----------------------------
text = "tell me the weather in thessaloniki"
ACCESS_TOKEN = 'ELYUKJ64AQSQUKGN7DOQC4X4VDKQIMYH'
headers = {'authorization': 'Bearer ' + ACCESS_TOKEN}
resp = requests.get('https://api.wit.ai/message?v=20180515&q=%s' % text, headers = headers)
data = json.loads(resp.content) 

intent = (((data['entities'])['intent'])[0])['value']
print(intent)
# edw, otan oloklhrw8oun ta intents, analoga me to intent pou vrhka 8a anazhtw to katallhlo value (p.x location, pizza_type etc)
value = (((data['entities'])['location'])[0])['value']
print(value)
print(data)

# ----------------------------------- Get weather forecast -------------------------------------
WEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast?id='
CITY_ID = '734077'  # code for thessaloniki
APP_ID = 'ab4b28ef1854e003f4830ceff45c62e7'
LANG = 'en'
weather_url = WEATHER_BASE_URL + CITY_ID + '&units=metric' + '&lang=' + LANG + '&APPID=' + APP_ID  # units=metric is for Celcius degrees
wresp = requests.get(weather_url)
wdata = wresp.json()
#print(wdata)

# extract the most important information
forecast = (wdata['list'])[0]
time = forecast['dt_txt']  # se UDT
weather = ((forecast['weather'])[0])['description']
temp_max = (forecast['main'])['temp_max']
temp_min = (forecast['main'])['temp_min']
humidity = (forecast['main'])['humidity']

temp = datetime.datetime.strptime(time[:10], '%Y-%m-%d').date()
fDate = temp.strftime('%A %d %B %Y')
print(fDate)
localTime = int(time[11:13]) + 3  #extract time and convert it according to timezone (only for Thessaloniki +3)
# genika mporei na kanei automata allagh wras an 3erei thn perioxh : https://stackoverflow.com/questions/10997577/python-timezone-conversion
# na to kanw otan 3erw k poies poleis uposthrizw k me ti morfh
textToTell = "Weather forecast for %s %d o'clock is %s. Minimum temperature will be %.2f and maximum %.2f Celsius degrees. Humidity will be %d percent."
print(textToTell % (fDate, localTime, weather, temp_min, temp_max, humidity))

# -------------------------------- Convert text to speech --------------------------------------
ttsobj = gTTS(textToTell % (fDate, localTime, weather, temp_min, temp_max, humidity))
ttsobj.save("textToSpeech.mp3")
os.system("mpg321 textToSpeech.mp3")
