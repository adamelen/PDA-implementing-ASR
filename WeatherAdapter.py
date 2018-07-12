# coding=utf-8

import ConfigParser
import requests
import json
import datetime
import time
import pytz
from Service import Service
from Openweathermap import Openweathermap
from Xweather import Xweather

class WeatherAdapter(Service):
    ''' A class that acts as an adapter between Service and weather interfaces (like openweathermap) '''

    def __init__(self):
        # get information from config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        self.lang = (config.get('GENERAL', 'LANGUAGE')).lower()
        self.tz_base_url = config.get('TIMEZONE', 'BASE_URL')
        self.tz_app_id = config.get('TIMEZONE', 'APP_ID')
        self.check = config.get('WEATHER', 'SPECIFIC_CITY_NAME')
        self.APIs = {
            'openweathermap': lambda: Openweathermap(),
            'xweather': lambda: Xweather()
            } 
        self.w = self.APIs[config.get('WEATHER','CHOOSE_API')]() # weather object

    def find_coordinates(self, city_name):
        ''' Find the coordinates of the given city '''
        geocode_url = "{}geocode/json?address={}&key={}".format(self.tz_base_url, city_name.capitalize(), self.tz_app_id)
        gcresp = requests.get(geocode_url)
        gcdata = gcresp.json()
        lat = ((((gcdata['results'])[0])['geometry'])['location'])['lat']
        lng = ((((gcdata['results'])[0])['geometry'])['location'])['lng']
        return (lat, lng)

    def convert_datetime(self, dt, lat, lng, convert_to):
        ''' Converts either utc time to local or local to utc based on the city_name '''
        # find time from epoch
        timestamp = time.mktime(dt.timetuple())

        # make a request to Google TimeZone API and get timezone name as a response
        timezone_url = "{}timezone/json?location={},{}&timestamp={}&key={}".format(self.tz_base_url, str(lat), str(lng), str(timestamp), self.tz_app_id)
        tzresp = requests.get(timezone_url)
        tzdata = tzresp.json()
        tz = tzdata['timeZoneId']
        timezone = pytz.timezone(tz)

        if (convert_to == 'local'):  # convert date and time to local ones
            dt = dt.replace(tzinfo=pytz.utc)
            newDatetime = dt.astimezone(pytz.timezone(tz))
        else:  # convert date and time to utc
            dt = timezone.localize(dt)
            newDatetime = (dt.astimezone(pytz.utc)).replace(tzinfo=None)
        return newDatetime

    def getInfo(self, vc, trl):
        ''' Get the weather forecast by calling the API that config.ini states. It processes the data before and after the call to the API '''
        if (self.check == 'ON'):
            city_name = config.get('WEATHER', 'CITY_NAME')  # use a predefined city_name
        else:
            city_name = vc.parameters['location']

        (lat, lng) = self.find_coordinates(city_name)

        # extract information about the date and time the user said
        if 'from' in vc.parameters['datetime']:  # if there is an interval in 'datetime', extract the time it starts and add 4 hours in order to get the middle of the interval
            dt_from = datetime.datetime.strptime((vc.parameters['datetime'])['from'], '%Y-%m-%dT%H:%M:%S.000+00:00')
            dt_from = self.convert_datetime(dt_from, lat, lng, 'utc')  # suppose that the time is in the timezone of the city_name -> convert it to UTC
            dt = dt_from + datetime.timedelta(hours=4)
        else:
            dt = datetime.datetime.strptime(vc.parameters['datetime'], '%Y-%m-%dT%H:%M:%S.000+00:00')
            dt = self.convert_datetime(dt, lat, lng, 'utc')

        # Call the API
        info = self.w.getWeather(city_name, lat, lng, dt)

        # If there aren't any errors, return the weather forecast
        if (info['error_days'] == None):
            localDatetime = self.convert_datetime(info['dt_new'], lat, lng, 'local')  #convert date and time according to timezone
            localDate = localDatetime.strftime('%A %d %B %Y')  #extract date
            localTime = int(localDatetime.strftime('%H'))  #extract time

            vc.textToTell = "Weather forecast for {} {} o'clock is {}. Minimum temperature will be {} and maximum {} Celsius degrees. Humidity will be {} percent.".format(localDate, str(localTime), info['weather'], str(info['temp_min']), str(info['temp_max']), str(info['humidity']))
        # otherwise display the error message
        else:
            vc.textToTell = 'There is no weather forecast for so many days ahead, only for the next {} days.'.format(info['error_days'])

        # Translate the above text in Greek if the desired language is Greek
        if (self.lang == 'el'):  
            vc.textToTell = trl.translation(vc.textToTell, 'en', 'el')

        return vc
