import requests
import json
import datetime
import difflib

def weather(base_url, city_id, lang, app_id):
    '''Requests the weather for a specific city in the next hours and returns the weather forecast in a string'''
    weather_url = base_url + city_id + '&units=metric' + '&lang=' + lang + '&APPID=' + app_id  # units=metric is for Celcius degrees
    wresp = requests.get(weather_url)
    wdata = wresp.json()

    # extract the most important information
    forecast = (wdata['list'])[0]
    time = forecast['dt_txt']  # in UDT
    weather = ((forecast['weather'])[0])['description']
    temp_max = int((forecast['main'])['temp_max'])
    temp_min = int((forecast['main'])['temp_min'])
    humidity = (forecast['main'])['humidity']

    temp = datetime.datetime.strptime(time[:10], '%Y-%m-%d').date()
    fDate = temp.strftime('%A %d %B %Y')
    localTime = int(time[11:13]) + 3  #extract time and convert it according to timezone (only for Thessaloniki +3)

    textToTell = "Weather forecast for "+fDate+" "+str(localTime)+" o'clock is "+weather+". Minimum temperature will be "+str(temp_min)+" and maximum "+str(temp_max)+" Celsius degrees. Humidity will be "+str(humidity)+" percent." 
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
    match = difflib.get_close_matches('thessaloniki'.capitalize(), city_list, n=1)[0]
    city = (item for item in data if item['name'] == match)
    city_id = (city.next())['id']
    return str(city_id)
