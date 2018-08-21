# coding=utf-8

import ConfigParser
import requests
import json
import datetime
import time
import difflib
import pytz
from Weather import Weather

class Openweathermap(Weather):
    ''' A <<Proxy>> that communicates with the http://api.openweathermap.org API and gets information about the weather '''

    def __init__(self):
        # list containing the hours of the day for which the user can get the weather forecast  
        self.hours = [0, 3, 6, 9, 12, 15, 18, 21]

        # get information from config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        self.base_url = config.get('OPENWEATHERMAP', 'WEATHER_BASE_URL')
        self.app_id = config.get('OPENWEATHERMAP', 'APP_ID')

        self.error_days = 5

    def find_city_id(self, city_name):
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

    def getWeather(self, city_name, dt, lang):
        info = {}
        city_id = self.find_city_id(city_name)  # find the city_id that corresponds to the city_name

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
            while (self.hours[i]<=now.hour and i<len(self.hours)):
                i = i + 1
            if (i==8):  # if the current hour is greater than 21:00 (UTC) then the next forecast will be at 00:00 of the next day and days will decrease by 1
                i = 0
                days = days -1
            dt_hour_index = self.hours.index(min(self.hours, key=lambda x:abs(x-dt.hour)))
            if (days==0 and dt_hour_index<i):  # if the time where desired time is rounded has passed, select the next possible one
                dt_hour_index = dt_hour_index + 1
            final_index = days*len(self.hours) + dt_hour_index - i

            # request the information about the weather from the api
            weather_url = "{}{}&units=metric&lang={}&APPID={}".format(self.base_url, city_id, lang, self.app_id)  # units=metric is for Celcius degrees
            wresp = requests.get(weather_url)
            wdata = wresp.json()    

            # extract the most important information
            forecast = (wdata['list'])[final_index]
            datetime_str = forecast['dt_txt']  # in UTC
            info['weather'] = ((forecast['weather'])[0])['description']
            info['temp_max'] = int((forecast['main'])['temp_max'])
            info['temp_min'] = int((forecast['main'])['temp_min'])
            info['humidity'] = (forecast['main'])['humidity']
            info['dt_new'] = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S') # date and time of forecast
            info['error_days'] = None
        else:
            info['weather'] = None
            info['temp_max'] = None
            info['temp_min'] = None
            info['humidity'] = None
            info['dt_new'] = None
            info['error_days'] = self.error_days
        return info            
