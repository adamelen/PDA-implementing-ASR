# coding=utf-8

import ConfigParser
import requests
import json
import codecs

def hospital(parameters):
    ''' Sends a request to google API "Places" to find hospitals in a certain region and returns a text that contains names and addresses of these hospitals'''

    # get information from config file
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    base_url = config.get('HOSPITAL', 'HOSPITAL_BASE_URL')
    app_id = config.get('HOSPITAL', 'APP_ID')
    loc_base_url = config.get('HOSPITAL', 'FIND_LOCATION_BASE_URL')

    if ('location' in parameters):
        if  ('near' in parameters['location']):
            del parameters['location']  # because wit.ai stores words like "nearby" in "location", but I don't want this to happen
    
    # Find hospitals in 'location'
    if 'location' in parameters:
        location = parameters['location']
        query = 'hospitals+in+' + location
        hosp_url = base_url + 'textsearch/json?query=' + query + '&key=' + app_id
        hosp_resp = requests.get(hosp_url)
        hosp_data = json.loads(hosp_resp.content)
        results = hosp_data['results']
        textToTell = ""
        for res in results:
            textToTell = textToTell + res['name'] + " - " + res['formatted_address'] + "\n"

    # Find hospitals in a range=dist around user's location
    else:
        if 'distance' in parameters:    # distance must be in kilometers
            dist = parameters['distance']
        elif parameters=={}:
            dist = 3
        loc_resp = requests.get(loc_base_url)
        loc_data = json.loads(loc_resp.text)
        lat = str(loc_data['latitude'])
        lng = str(loc_data['longitude']) 
        location = lat+","+lng
        hosp_url = base_url + 'nearbysearch/json?' + 'location=' + location + '&radius=' + str(dist*1000) + '&name=hospital&type=hospital&key=' + app_id
        hosp_resp = requests.get(hosp_url)
        hosp_data = json.loads(hosp_resp.content)
        results = hosp_data['results']
        textToTell = ""
        for res in results:
            textToTell = textToTell + res['name'] + " - " + res['vicinity'] + "\n"

    return textToTell

