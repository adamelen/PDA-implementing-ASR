# coding=utf-8

import ConfigParser
import requests
import json
import datetime
import time
import difflib
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
        self.tz_base_url = config.get('TIMEZONE', 'BASE_URL')
        self.tz_app_id = config.get('TIMEZONE', 'APP_ID')
        self.loc_base_url = config.get('PLACES', 'FIND_LOCATION_BASE_URL')
        self.APIs = {
            'openweathermap': lambda: Openweathermap(),
            'xweather': lambda: Xweather()
            } 
        self.w = self.APIs[config.get('WEATHER','CHOOSE_API')]() # weather object
        self.responses = {
            'el':
            [u"\nΑν θέλεις τον καιρό σε άλλη πόλη, επανάλαβε το ερώτημά σου συμπεριλαμβάνοντας την πόλη.",
             u"\nΑν θέλεις τον καιρό σε άλλη χρονική στιγμή, επανάλαβε το ερώτημά σου συμπεριλαμβάνοντας τη χρονική στιγμή.",
             u"{}: {} {} η ώρα, η πρόγνωση του καιρού είναι {}. Η ελάχιστη θερμοκρασία θα είναι {} και η μέγιστη {} βαθμοί Κελσίου. Η υγρασία θα είναι {} τα εκατό.",
             u"Δεν υπάρχει πρόγνωση καιρού για τόσες μέρες μετά, μόνο για τις επόμενες 5 μέρες."],
            'en':
            ["\nIf you want to know the weather in another city, ask your question again specifying the city name.",
             "\nIf you want to know about the weather in another moment, ask your question again specifying that moment.",
             "Weather forecast in {} at {} {} o'clock is {}. Minimum temperature will be {} and maximum {} Celsius degrees. Humidity will be {} percent.",
             "There is no weather forecast for so many days ahead, only for the next {} days."]
            }

    def find_coordinates(self, city_name):
        ''' Find the coordinates of the given city '''
        geocode_url = "{}geocode/json?address={}&key={}".format(self.tz_base_url, city_name.capitalize(), self.tz_app_id)
        gcresp = requests.get(geocode_url)
        gcdata = gcresp.json()
        lat = ((((gcdata['results'])[0])['geometry'])['location'])['lat']
        lng = ((((gcdata['results'])[0])['geometry'])['location'])['lng']
        return (lat, lng)

    def convert_datetime(self, dt, lat, lng, convert_to):
        ''' Converts either utc time to local or local to utc based on the city's coordinates '''
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

    def getInfo(self, vc, trl, lang):
        ''' Get the weather forecast by calling the API that config.ini states. It processes the data before and after the call to the API '''
        addText = ''
        # check if the user gave location and datetime, otherwise use the current ones and inform him about it
        if 'location' in vc.parameters:
            city_name = vc.parameters['location']
        else:
            loc_resp = requests.get(self.loc_base_url)
            loc_data = json.loads(loc_resp.text)   
            city_name = str(loc_data['city'])
            addText = addText + self.responses[lang][0] 

        (lat, lng) = self.find_coordinates(city_name)

        if 'datetime' in vc.parameters:
            # extract information about the date and time the user said
            if 'from' in vc.parameters['datetime']:  # if there is an interval in 'datetime', extract the time it starts and add 4 hours in order to get the middle of the interval
                dt_from = datetime.datetime.strptime((vc.parameters['datetime'])['from'], '%Y-%m-%dT%H:%M:%S.000+00:00')
                dt_from = self.convert_datetime(dt_from, lat, lng, 'utc')  # suppose that the time is in the timezone of the city_name -> convert it to UTC
                dt = dt_from + datetime.timedelta(hours=4)
            else:
                dt = datetime.datetime.strptime(vc.parameters['datetime'], '%Y-%m-%dT%H:%M:%S.000+00:00')
                dt = self.convert_datetime(dt, lat, lng, 'utc')
        else:
            dt = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # get the next available weather forecast, asking about the forecast for 10 minutes later (in order not to get an error if there is a delay somewhere)
            addText = addText + self.responses[lang][1]

        # call the API to get the weather forecast
        info = self.w.getWeather(city_name, dt, lang)

        if (info['error_days'] == None):    
            localDatetime = self.convert_datetime(info['dt_new'], lat, lng, 'local')  #convert date and time according to timezone
            localDate = localDatetime.strftime('%A %d %B %Y')  #extract date
            localTime = int(localDatetime.strftime('%H'))  #extract time

            if (lang == 'el'):
                city_name = trl.translate(city_name, 'en', 'el')
                localDate = trl.translate(localDate, 'en', 'el')

            vc.textToTell = self.responses[lang][2].format(city_name.capitalize(), localDate, localTime, info['weather'], info['temp_min'], info['temp_max'], info['humidity']) + addText
        else:
            vc.textToTell = self.responses[lang][3].format(info['error_days'])

        return vc
