import time
import requests
import pytz
import datetime

def convert_datetime(datetime_str, city_name, base_url, app_id):
    # find coordinates of the desired city
    geocode_url = base_url + 'geocode/json?address=' + city_name.capitalize() + '&key=' + app_id
    gcresp = requests.get(geocode_url)
    gcdata = gcresp.json()
    lat = ((((gcdata['results'])[0])['geometry'])['location'])['lat']
    lng = ((((gcdata['results'])[0])['geometry'])['location'])['lng']

    # find time from epoch
    time_tuple = time.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    timestamp = time.mktime(time_tuple)

    # make a request to Google TimeZone API and get timeZone name as a response
    timezone_url = base_url + 'timezone/json?location=' + str(lat) + ',' + str(lng) + '&timestamp=' + str(timestamp) + '&key=' + app_id
    tzresp = requests.get(timezone_url)
    tzdata = tzresp.json()
    tz = tzdata['timeZoneId']

    # convert date and time to local ones
    dt = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    dt_utc = dt.replace(tzinfo=pytz.utc)
    localDatetime = dt_utc.astimezone(pytz.timezone(tz))
    return localDatetime
