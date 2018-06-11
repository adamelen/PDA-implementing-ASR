# coding=utf-8

import ConfigParser
import requests
import json
import datetime
import time
import difflib
from translation import translation
from convert_datetime import convert_datetime

def weather(parameters):
    '''Requests the weather (from https://openweathermap.org/) for a specific city in the next hours and returns the weather forecast in a string'''

    # list containing the hours of the day for which the user can get the weather forecast  
    hours = [0, 3, 6, 9, 12, 15, 18, 21]     

    # get information from config file
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    lang = (config.get('GENERAL', 'LANGUAGE')).lower()
    base_url = config.get('WEATHER', 'WEATHER_BASE_URL')
    app_id = config.get('WEATHER', 'APP_ID')
    tr_base_url = config.get('TRANSLATION', 'BASE_URL')
    tr_app_id = config.get('TRANSLATION', 'APP_ID')
    tz_base_url = config.get('TIMEZONE', 'BASE_URL')
    tz_app_id = config.get('TIMEZONE', 'APP_ID')
    if (config.get('WEATHER', 'SPECIFIC_CITY_ID') == 'ON'):  # use a predefined city_id
        city_id = config.get('WEATHER', 'CITY_ID')
        city_name = config.get('WEATHER', 'CITY_NAME')
    else:
        ''' if 'location' not in parameters
            loc_base_url = 'http://freegeoip.net/json'
            loc_resp = requests.get(loc_base_url)
            loc_data = json.loads(loc_resp.text)
            lat = str(loc_data['latitude'])
            lng = str(loc_data['longitude'])'''
        city_name = parameters['location']
        city_id = find_city_id(city_name)  # otherwise find the city_id that corresponds to the city_name

    # extract information about the date and time the user said
    if 'from' in parameters['datetime']:  # if there is an interval in 'datetime', extract the time it starts and add 4 hours in order to get the middle of the interval
        dt_from = datetime.datetime.strptime((parameters['datetime'])['from'], '%Y-%m-%dT%H:%M:%S.000+00:00')
        dt_from = convert_datetime(dt_from, city_name, tz_base_url, tz_app_id, 'utc')  # suppose that the time is in the timezone of the city_name -> convert it to UTC
        dt = dt_from + datetime.timedelta(hours=4)
        print(dt)
    else:
        dt = datetime.datetime.strptime(parameters['datetime'], '%Y-%m-%dT%H:%M:%S.000+00:00')
        dt = convert_datetime(dt, city_name, tz_base_url, tz_app_id, 'utc')

    now = datetime.datetime.utcnow()
    diff = dt - now
    days = diff.days
    seconds = diff.total_seconds()
    # desired day of forecast must be in the next 5 days, otherwise there is no forecast for that day
    if (seconds<=432000):
        # decide which item from the list of data the API sends coresponds to the desired day and time
        if (dt.hour < now.hour):
            days = days + 1  # e.g. if days=1, it means that the desired day is the next one (but the desired hour might be <24 hours ahead)
        i = 0
        while (hours[i]<=now.hour and i<len(hours)):
            i = i + 1
        if (i==8):  # if the current hour is greater than 21:00 (UTC) then the next forecast will be at 00:00 of the next day and days will decrease by 1
            i = 0
            days = days -1
        dt_hour_index = hours.index(min(hours, key=lambda x:abs(x-dt.hour)))
        if (days==0 and dt_hour_index<i):  # if the time where desired time is rounded has passed, select the next possible one
            dt_hour_index = dt_hour_index + 1
        final_index = days*len(hours) + dt_hour_index - i

        # request the information about the weather from the api
        weather_url = base_url + city_id + '&units=metric' + '&lang=' + lang + '&APPID=' + app_id  # units=metric is for Celcius degrees
        wresp = requests.get(weather_url)
        wdata = wresp.json()    

        # extract the most important information
        forecast = (wdata['list'])[final_index]
        datetime_str = forecast['dt_txt']  # in UTC
        weather = ((forecast['weather'])[0])['description']
        temp_max = int((forecast['main'])['temp_max'])
        temp_min = int((forecast['main'])['temp_min'])
        humidity = (forecast['main'])['humidity']
    
        dt_new = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        localDatetime = convert_datetime(dt_new, city_name, tz_base_url, tz_app_id, 'local')  #convert date and time according to timezone
        localDate = localDatetime.strftime('%A %d %B %Y')  #extract date
        localTime = int(localDatetime.strftime('%H'))  #extract time

        if (lang == 'el'):
            localDate = translation(tr_base_url, tr_app_id, localDate, 'en-el')
            textToTell = localDate+" "+str(localTime)+unicode(" η ώρα, η πρόγνωση του καιρού είναι ", 'utf-8')+weather+unicode(". Η ελάχιστη θερμοκρασία θα είναι ", 'utf-8')+str(temp_min)+unicode(" και η μέγιστη ", 'utf-8')+str(temp_max)+unicode(" βαθμοί Κελσίου. Η υγρασία θα είναι ", 'utf-8')+str(humidity)+unicode(" τα εκατό.", 'utf-8')
        else:
            textToTell = "Weather forecast for "+localDate+" "+str(localTime)+" o'clock is "+weather+". Minimum temperature will be "+str(temp_min)+" and maximum "+str(temp_max)+" Celsius degrees. Humidity will be "+str(humidity)+" percent."

    else:
        if (lang == 'el'):
            textToTell = unicode('Δεν υπάρχει πρόγνωση καιρού για τόσες μέρες μετά, μόνο για τις επόμενες 5 μέρες.', 'utf-8')
        else:
            textToTell = 'There is no weather forecast for so many days ahead, only for the next 5 days.'

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
