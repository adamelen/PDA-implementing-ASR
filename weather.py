# coding=utf-8

import requests
import json
import datetime
import difflib
from translation import translation
from convert_datetime import convert_datetime

def weather(base_url, city_name, city_id, lang, app_id, tr_base_url, tr_app_id, tz_base_url, tz_app_id):
    '''Requests the weather for a specific city in the next hours and returns the weather forecast in a string'''
    weather_url = base_url + city_id + '&units=metric' + '&lang=' + lang + '&APPID=' + app_id  # units=metric is for Celcius degrees
    wresp = requests.get(weather_url)
    wdata = wresp.json()

    # extract the most important information
    forecast = (wdata['list'])[0]
    datetime_str = forecast['dt_txt']  # in UTC
    weather = ((forecast['weather'])[0])['description']
    temp_max = int((forecast['main'])['temp_max'])
    temp_min = int((forecast['main'])['temp_min'])
    humidity = (forecast['main'])['humidity']

    localDatetime = convert_datetime(datetime_str, city_name, tz_base_url, tz_app_id)  #convert date and time according to timezone
    localDate = localDatetime.strftime('%A %d %B %Y')  #extract date
    localTime = int(localDatetime.strftime('%H'))  #extract time

    if (lang == 'el'):
        localDate = translation(tr_base_url, tr_app_id, localDate, 'en-el')
        textToTell = localDate+" "+str(localTime)+unicode(" η ώρα, η πρόγνωση του καιρού είναι ", 'utf-8')+weather+unicode(". Η ελάχιστη θερμοκρασία θα είναι ", 'utf-8')+str(temp_min)+unicode(" και η μέγιστη ", 'utf-8')+str(temp_max)+unicode(" βαθμοί Κελσίου. Η υγρασία θα είναι ", 'utf-8')+str(humidity)+unicode(" τα εκατό.", 'utf-8')
    else:
        textToTell = "Weather forecast for "+localDate+" "+str(localTime)+" o'clock is "+weather+". Minimum temperature will be "+str(temp_min)+" and maximum "+str(temp_max)+" Celsius degrees. Humidity will be "+str(humidity)+" percent." 
    return textToTell

def find_city_id(city_name):
    '''Matches the given city_name with the most similar name in the city.list.json file that corresponds to a code. That code is returned as the city_id'''

    # open the json file that contains a list of all possible cities
    f = open('./city.list.json', 'r')
    data = json.load(f)

    # store the name of every city in a list
    i=0
    city_list = []
    for city_data in data:
        city_list.append(city_data['name'])
        i = i + 1

    # find the best match among cities and return its id
    match = difflib.get_close_matches(city_name.capitalize(), city_list, n=1)[0]
    city = (item for item in data if item['name'] == match)
    city_id = (city.next())['id']
    return str(city_id)
