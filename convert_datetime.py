import time
import requests
import pytz
import datetime

def convert_datetime(dt, city_name, base_url, app_id, convert_to):
    ''' Converts either utc time to local or local to utc based on the city_name '''
    # find coordinates of the desired city
    geocode_url = base_url + 'geocode/json?address=' + city_name.capitalize() + '&key=' + app_id
    gcresp = requests.get(geocode_url)
    gcdata = gcresp.json()
    lat = ((((gcdata['results'])[0])['geometry'])['location'])['lat']
    lng = ((((gcdata['results'])[0])['geometry'])['location'])['lng']

    # find time from epoch
    timestamp = time.mktime(dt.timetuple())

    # make a request to Google TimeZone API and get timezone name as a response
    timezone_url = base_url + 'timezone/json?location=' + str(lat) + ',' + str(lng) + '&timestamp=' + str(timestamp) + '&key=' + app_id
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
